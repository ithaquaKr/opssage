#!/usr/bin/env python3
"""
Standalone E2E test runner for Multi-Agent System scenarios.

This script runs all Kubernetes incident simulation scenarios through the
AICA → KREA → RCARA pipeline and generates detailed reports.

Usage:
    python scripts/run_e2e_tests.py [--scenario <scenario_id>] [--output <json_file>]

Examples:
    # Run all scenarios
    python scripts/run_e2e_tests.py

    # Run a specific scenario
    python scripts/run_e2e_tests.py --scenario scenario_1

    # Run all scenarios and save results to JSON
    python scripts/run_e2e_tests.py --output results.json
"""

import argparse
import asyncio
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sages.models import AlertInput, IncidentDiagnosticReport
from sages.orchestrator import create_orchestrator
from tests.test_scenarios import TEST_SCENARIOS

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class E2ETestRunner:
    """End-to-end test runner for MAS scenarios."""

    def __init__(self) -> None:
        self.orchestrator = create_orchestrator()
        self.results: list[dict[str, Any]] = []

    def convert_scenario_to_alert(self, scenario: dict[str, Any]) -> AlertInput:
        """Convert a test scenario into an AlertInput model."""
        primary_alert = scenario["alerts"][0]
        labels = primary_alert.get("labels", {})
        annotations = primary_alert.get("annotations", {})

        return AlertInput(
            alert_name=labels.get("alertname", "UnknownAlert"),
            severity=labels.get("severity", "unknown"),
            message=annotations.get("description", scenario["description"]),
            labels=labels,
            annotations=annotations,
            firing_condition=annotations.get("summary", ""),
            timestamp=datetime.fromisoformat(
                primary_alert.get("startsAt", "2025-11-29T00:00:00Z").replace("Z", "+00:00")
            ),
        )

    def validate_diagnostic_report(
        self,
        report: IncidentDiagnosticReport,
        expected_root_cause: str,
        expected_suggestions: list[str],
    ) -> tuple[bool, list[str]]:
        """
        Validate the diagnostic report against expected outcomes.

        Returns:
            Tuple of (is_valid, list of validation issues)
        """
        issues = []

        # Check root cause
        if not report.root_cause or len(report.root_cause) < 10:
            issues.append("Root cause is too short or missing")

        # Check confidence score
        if report.confidence_score < 0.0 or report.confidence_score > 1.0:
            issues.append(f"Invalid confidence score: {report.confidence_score}")

        # Check reasoning steps
        if not report.reasoning_steps or len(report.reasoning_steps) == 0:
            issues.append("No reasoning steps provided")
        elif len(report.reasoning_steps) < 2:
            issues.append("Insufficient reasoning steps (need at least 2)")

        # Check supporting evidence
        if not report.supporting_evidence or len(report.supporting_evidence) == 0:
            issues.append("No supporting evidence provided")

        # Check remediation actions
        if not report.recommended_remediation.short_term_actions:
            issues.append("No short-term actions provided")

        return len(issues) == 0, issues

    async def run_scenario(self, scenario: dict[str, Any]) -> dict[str, Any]:
        """
        Run a single scenario through the MAS pipeline.

        Returns:
            Dictionary containing test results
        """
        logger.info(f"{'=' * 80}")
        logger.info(f"Running Scenario: {scenario['name']}")
        logger.info(f"Complexity Level: {scenario['complexity_level']}")
        logger.info(f"{'=' * 80}")

        alert = self.convert_scenario_to_alert(scenario)
        start_time = datetime.utcnow()

        result = {
            "scenario_id": scenario["id"],
            "scenario_name": scenario["name"],
            "complexity_level": scenario["complexity_level"],
            "start_time": start_time.isoformat(),
            "expected_root_cause": scenario["expected_root_cause"],
            "expected_suggestions": scenario["expected_suggestions"],
        }

        try:
            # Run the incident analysis
            incident_id, diagnostic_report = await self.orchestrator.analyze_incident(alert)
            end_time = datetime.utcnow()
            duration = (end_time - start_time).total_seconds()

            # Validate the report
            is_valid, validation_issues = self.validate_diagnostic_report(
                diagnostic_report,
                scenario["expected_root_cause"],
                scenario["expected_suggestions"],
            )

            # Collect results
            result.update(
                {
                    "success": is_valid,
                    "incident_id": incident_id,
                    "duration_seconds": duration,
                    "end_time": end_time.isoformat(),
                    "actual_root_cause": diagnostic_report.root_cause,
                    "confidence_score": diagnostic_report.confidence_score,
                    "reasoning_steps": diagnostic_report.reasoning_steps,
                    "supporting_evidence": diagnostic_report.supporting_evidence,
                    "short_term_actions": diagnostic_report.recommended_remediation.short_term_actions,
                    "long_term_actions": diagnostic_report.recommended_remediation.long_term_actions,
                    "validation_issues": validation_issues if not is_valid else [],
                    "error": None,
                }
            )

            status = "✓ PASS" if is_valid else "✗ FAIL"
            logger.info(f"{status} - Completed in {duration:.2f}s")

            if not is_valid:
                logger.warning(f"Validation issues: {', '.join(validation_issues)}")

        except Exception as e:
            end_time = datetime.utcnow()
            duration = (end_time - start_time).total_seconds()

            logger.error(f"✗ FAIL - Error: {str(e)}")

            result.update(
                {
                    "success": False,
                    "incident_id": None,
                    "duration_seconds": duration,
                    "end_time": end_time.isoformat(),
                    "error": str(e),
                    "validation_issues": [],
                }
            )

        return result

    async def run_all_scenarios(self) -> list[dict[str, Any]]:
        """Run all scenarios sequentially."""
        logger.info("Starting E2E tests for all scenarios")
        logger.info(f"Total scenarios: {len(TEST_SCENARIOS['scenarios'])}")

        for scenario in TEST_SCENARIOS["scenarios"]:
            result = await self.run_scenario(scenario)
            self.results.append(result)

        return self.results

    async def run_single_scenario(self, scenario_id: str) -> dict[str, Any]:
        """Run a single scenario by ID."""
        scenario = next(
            (s for s in TEST_SCENARIOS["scenarios"] if s["id"] == scenario_id), None
        )

        if not scenario:
            raise ValueError(f"Scenario '{scenario_id}' not found")

        result = await self.run_scenario(scenario)
        self.results.append(result)
        return result

    def print_summary(self) -> None:
        """Print a summary of test results."""
        total = len(self.results)
        passed = sum(1 for r in self.results if r["success"])
        failed = total - passed

        print("\n" + "=" * 80)
        print("END-TO-END TEST SUMMARY")
        print("=" * 80)
        print(f"Total Scenarios: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print(f"Success Rate: {(passed / total * 100) if total > 0 else 0:.1f}%")
        print("=" * 80)

        for result in self.results:
            status = "✓ PASS" if result["success"] else "✗ FAIL"
            duration = result.get("duration_seconds", 0)

            print(f"\n{status} - {result['scenario_name']} (Level {result['complexity_level']})")
            print(f"  Scenario ID: {result['scenario_id']}")
            print(f"  Duration: {duration:.2f}s")

            if result["success"]:
                print(f"  Incident ID: {result.get('incident_id', 'N/A')}")
                print(f"  Confidence: {result.get('confidence_score', 'N/A'):.2f}")
                print(f"  Root Cause: {result.get('actual_root_cause', 'N/A')[:100]}...")
                print(f"  Reasoning Steps: {len(result.get('reasoning_steps', []))}")
                print(f"  Short-term Actions: {len(result.get('short_term_actions', []))}")
                print(f"  Long-term Actions: {len(result.get('long_term_actions', []))}")
            else:
                if result.get("error"):
                    print(f"  Error: {result['error']}")
                if result.get("validation_issues"):
                    print(f"  Validation Issues:")
                    for issue in result["validation_issues"]:
                        print(f"    - {issue}")

        print("\n" + "=" * 80)

        # Print detailed analysis
        if total > 0:
            avg_confidence = sum(
                r.get("confidence_score", 0) for r in self.results if r["success"]
            ) / max(passed, 1)
            avg_duration = sum(r.get("duration_seconds", 0) for r in self.results) / total

            print("\nDETAILED ANALYSIS")
            print("=" * 80)
            print(f"Average Confidence Score: {avg_confidence:.2f}")
            print(f"Average Duration: {avg_duration:.2f}s")

            # Breakdown by complexity level
            for level in [1, 2, 3]:
                level_results = [r for r in self.results if r["complexity_level"] == level]
                if level_results:
                    level_passed = sum(1 for r in level_results if r["success"])
                    level_total = len(level_results)
                    print(
                        f"Level {level}: {level_passed}/{level_total} passed "
                        f"({level_passed / level_total * 100:.0f}%)"
                    )

            print("=" * 80 + "\n")

    def save_results(self, output_file: str) -> None:
        """Save results to a JSON file."""
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with output_path.open("w") as f:
            json.dump(
                {
                    "timestamp": datetime.utcnow().isoformat(),
                    "total_scenarios": len(self.results),
                    "passed": sum(1 for r in self.results if r["success"]),
                    "failed": sum(1 for r in self.results if not r["success"]),
                    "results": self.results,
                },
                f,
                indent=2,
            )

        logger.info(f"Results saved to {output_file}")


async def main() -> int:
    """Main entry point for the test runner."""
    parser = argparse.ArgumentParser(
        description="Run E2E tests for Multi-Agent System scenarios"
    )
    parser.add_argument(
        "--scenario",
        type=str,
        help="Run a specific scenario by ID (e.g., scenario_1)",
    )
    parser.add_argument(
        "--output",
        type=str,
        help="Save results to a JSON file",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging",
    )

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    runner = E2ETestRunner()

    try:
        if args.scenario:
            # Run single scenario
            await runner.run_single_scenario(args.scenario)
        else:
            # Run all scenarios
            await runner.run_all_scenarios()

        # Print summary
        runner.print_summary()

        # Save results if requested
        if args.output:
            runner.save_results(args.output)

        # Return exit code based on test results
        failed_count = sum(1 for r in runner.results if not r["success"])
        return 1 if failed_count > 0 else 0

    except Exception as e:
        logger.error(f"Test runner failed: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
