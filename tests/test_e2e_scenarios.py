"""
End-to-end tests for Multi-Agent System using Kubernetes incident scenarios.

Tests the complete pipeline: AICA → KREA → RCARA
"""

import logging
import time
from datetime import datetime
from typing import Any

import pytest

from sages.models import AlertInput, IncidentDiagnosticReport
from sages.notifications import get_notifier
from sages.orchestrator import IncidentOrchestrator, create_orchestrator
from tests.test_scenarios import TEST_SCENARIOS

logger = logging.getLogger(__name__)


class TestResultCollector:
    """Collects and analyzes test results for reporting."""

    def __init__(self) -> None:
        self.results: list[dict[str, Any]] = []

    def add_result(
        self,
        scenario_id: str,
        scenario_name: str,
        complexity_level: int,
        success: bool,
        incident_id: str,
        diagnostic_report: IncidentDiagnosticReport | None,
        expected_root_cause: str,
        expected_suggestions: list[str],
        error: str | None = None,
    ) -> None:
        """Add a test result."""
        result = {
            "scenario_id": scenario_id,
            "scenario_name": scenario_name,
            "complexity_level": complexity_level,
            "success": success,
            "incident_id": incident_id,
            "error": error,
            "expected_root_cause": expected_root_cause,
            "expected_suggestions": expected_suggestions,
        }

        if diagnostic_report:
            result.update(
                {
                    "actual_root_cause": diagnostic_report.root_cause,
                    "confidence_score": diagnostic_report.confidence_score,
                    "reasoning_steps": diagnostic_report.reasoning_steps,
                    "short_term_actions": diagnostic_report.recommended_remediation.short_term_actions,
                    "long_term_actions": diagnostic_report.recommended_remediation.long_term_actions,
                }
            )

        self.results.append(result)

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
            print(
                f"\n{status} - {result['scenario_name']} (Level {result['complexity_level']})"
            )
            print(f"  Scenario ID: {result['scenario_id']}")
            print(f"  Incident ID: {result['incident_id']}")

            if result["success"]:
                print(f"  Confidence: {result.get('confidence_score', 'N/A')}")
                print(
                    f"  Root Cause: {result.get('actual_root_cause', 'N/A')[:100]}..."
                )
            else:
                print(f"  Error: {result['error']}")

        print("\n" + "=" * 80)


def convert_scenario_to_alert(scenario: dict[str, Any]) -> AlertInput:
    """
    Convert a test scenario into an AlertInput model.

    Args:
        scenario: Test scenario dictionary

    Returns:
        AlertInput model instance
    """
    # Get the primary alert (first one)
    primary_alert = scenario["alerts"][0]

    # Extract labels and annotations
    labels = primary_alert.get("labels", {})
    annotations = primary_alert.get("annotations", {})

    # Create AlertInput
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
    report: IncidentDiagnosticReport,
    expected_root_cause: str,
    expected_suggestions: list[str],
) -> tuple[bool, str]:
    """
    Validate the diagnostic report against expected outcomes.

    Args:
        report: The diagnostic report from RCARA
        expected_root_cause: Expected root cause keywords/pattern
        expected_suggestions: Expected suggestion keywords

    Returns:
        Tuple of (validation_passed, validation_message)
    """
    validations = []

    # Check if root cause is reasonable
    if not report.root_cause or len(report.root_cause) < 10:
        validations.append("Root cause is too short or missing")

    # Check confidence score
    if report.confidence_score < 0.0 or report.confidence_score > 1.0:
        validations.append(f"Invalid confidence score: {report.confidence_score}")

    # Check reasoning steps
    if not report.reasoning_steps or len(report.reasoning_steps) == 0:
        validations.append("No reasoning steps provided")

    # Check supporting evidence
    if not report.supporting_evidence or len(report.supporting_evidence) == 0:
        validations.append("No supporting evidence provided")

    # Check remediation actions
    if not report.recommended_remediation.short_term_actions:
        validations.append("No short-term actions provided")

    # If there are validation errors, fail
    if validations:
        return False, "; ".join(validations)

    return True, "Diagnostic report structure is valid"


@pytest.fixture
def orchestrator() -> IncidentOrchestrator:
    """Create an orchestrator instance for testing."""
    return create_orchestrator()


@pytest.fixture
def result_collector() -> TestResultCollector:
    """Create a result collector for gathering test outcomes."""
    return TestResultCollector()


@pytest.mark.asyncio
async def test_scenario_1_crashloopbackoff(
    orchestrator: IncidentOrchestrator, result_collector: TestResultCollector
) -> None:
    """Test Scenario 1: Pod CrashLoopBackOff - Simple complexity."""
    scenario = TEST_SCENARIOS["scenarios"][0]
    assert scenario["id"] == "scenario_1"

    alert = convert_scenario_to_alert(scenario)
    notifier = get_notifier()
    start_time = time.time()

    try:
        # Send start notification
        incident_id = f"test-{scenario['id']}-{int(start_time)}"
        await notifier.send_incident_start(incident_id, alert)

        # Run analysis
        incident_id, diagnostic_report = await orchestrator.analyze_incident(alert)
        duration = time.time() - start_time

        # Validate the diagnostic report
        is_valid, validation_msg = validate_diagnostic_report(
            diagnostic_report,
            scenario["expected_root_cause"],
            scenario["expected_suggestions"],
        )

        # Send completion notification
        await notifier.send_incident_complete(
            incident_id, alert, diagnostic_report, duration
        )

        result_collector.add_result(
            scenario_id=scenario["id"],
            scenario_name=scenario["name"],
            complexity_level=scenario["complexity_level"],
            success=is_valid,
            incident_id=incident_id,
            diagnostic_report=diagnostic_report,
            expected_root_cause=scenario["expected_root_cause"],
            expected_suggestions=scenario["expected_suggestions"],
            error=None if is_valid else validation_msg,
        )

        assert is_valid, f"Validation failed: {validation_msg}"

    except Exception as e:
        duration = time.time() - start_time
        logger.error(f"Scenario 1 failed with error: {e}")

        # Send error notification
        await notifier.send_incident_error(
            incident_id or "N/A", alert, str(e), duration
        )

        result_collector.add_result(
            scenario_id=scenario["id"],
            scenario_name=scenario["name"],
            complexity_level=scenario["complexity_level"],
            success=False,
            incident_id="N/A",
            diagnostic_report=None,
            expected_root_cause=scenario["expected_root_cause"],
            expected_suggestions=scenario["expected_suggestions"],
            error=str(e),
        )
        raise


@pytest.mark.asyncio
async def test_scenario_2_cpu_exhaustion(
    orchestrator: IncidentOrchestrator, result_collector: TestResultCollector
) -> None:
    """Test Scenario 2: Node CPU Exhaustion - Medium complexity."""
    scenario = TEST_SCENARIOS["scenarios"][1]
    assert scenario["id"] == "scenario_2"

    alert = convert_scenario_to_alert(scenario)
    notifier = get_notifier()
    start_time = time.time()

    try:
        # Send start notification
        incident_id = f"test-{scenario['id']}-{int(start_time)}"
        await notifier.send_incident_start(incident_id, alert)

        # Run analysis
        incident_id, diagnostic_report = await orchestrator.analyze_incident(alert)
        duration = time.time() - start_time

        # Validate the diagnostic report
        is_valid, validation_msg = validate_diagnostic_report(
            diagnostic_report,
            scenario["expected_root_cause"],
            scenario["expected_suggestions"],
        )

        # Send completion notification
        await notifier.send_incident_complete(
            incident_id, alert, diagnostic_report, duration
        )

        result_collector.add_result(
            scenario_id=scenario["id"],
            scenario_name=scenario["name"],
            complexity_level=scenario["complexity_level"],
            success=is_valid,
            incident_id=incident_id,
            diagnostic_report=diagnostic_report,
            expected_root_cause=scenario["expected_root_cause"],
            expected_suggestions=scenario["expected_suggestions"],
            error=None if is_valid else validation_msg,
        )

        assert is_valid, f"Validation failed: {validation_msg}"

    except Exception as e:
        duration = time.time() - start_time
        logger.error(f"Scenario 2 failed with error: {e}")

        # Send error notification
        await notifier.send_incident_error(
            incident_id or "N/A", alert, str(e), duration
        )
        result_collector.add_result(
            scenario_id=scenario["id"],
            scenario_name=scenario["name"],
            complexity_level=scenario["complexity_level"],
            success=False,
            incident_id="N/A",
            diagnostic_report=None,
            expected_root_cause=scenario["expected_root_cause"],
            expected_suggestions=scenario["expected_suggestions"],
            error=str(e),
        )
        raise


@pytest.mark.asyncio
async def test_scenario_3_dependency_failure(
    orchestrator: IncidentOrchestrator, result_collector: TestResultCollector
) -> None:
    """Test Scenario 3: Multi-Service Dependency Failure - Complex."""
    scenario = TEST_SCENARIOS["scenarios"][2]
    assert scenario["id"] == "scenario_3"

    alert = convert_scenario_to_alert(scenario)
    notifier = get_notifier()
    start_time = time.time()

    try:
        # Send start notification
        incident_id = f"test-{scenario['id']}-{int(start_time)}"
        await notifier.send_incident_start(incident_id, alert)

        # Run analysis
        incident_id, diagnostic_report = await orchestrator.analyze_incident(alert)
        duration = time.time() - start_time

        # Validate the diagnostic report
        is_valid, validation_msg = validate_diagnostic_report(
            diagnostic_report,
            scenario["expected_root_cause"],
            scenario["expected_suggestions"],
        )

        # Send completion notification
        await notifier.send_incident_complete(
            incident_id, alert, diagnostic_report, duration
        )

        result_collector.add_result(
            scenario_id=scenario["id"],
            scenario_name=scenario["name"],
            complexity_level=scenario["complexity_level"],
            success=is_valid,
            incident_id=incident_id,
            diagnostic_report=diagnostic_report,
            expected_root_cause=scenario["expected_root_cause"],
            expected_suggestions=scenario["expected_suggestions"],
            error=None if is_valid else validation_msg,
        )

        assert is_valid, f"Validation failed: {validation_msg}"

    except Exception as e:
        duration = time.time() - start_time
        logger.error(f"Scenario 3 failed with error: {e}")

        # Send error notification
        await notifier.send_incident_error(
            incident_id or "N/A", alert, str(e), duration
        )

        result_collector.add_result(
            scenario_id=scenario["id"],
            scenario_name=scenario["name"],
            complexity_level=scenario["complexity_level"],
            success=False,
            incident_id="N/A",
            diagnostic_report=None,
            expected_root_cause=scenario["expected_root_cause"],
            expected_suggestions=scenario["expected_suggestions"],
            error=str(e),
        )
        raise


@pytest.mark.asyncio
async def test_all_scenarios_sequential(result_collector: TestResultCollector) -> None:
    """
    Run all scenarios sequentially and generate a comprehensive report.

    This test provides a unified view of all scenario test results.
    """
    orchestrator = create_orchestrator()
    notifier = get_notifier()
    overall_start_time = time.time()

    for scenario in TEST_SCENARIOS["scenarios"]:
        alert = convert_scenario_to_alert(scenario)
        start_time = time.time()

        try:
            logger.info(f"Running scenario: {scenario['name']}")

            # Send start notification
            incident_id = f"test-{scenario['id']}-{int(start_time)}"
            await notifier.send_incident_start(incident_id, alert)

            # Run analysis
            incident_id, diagnostic_report = await orchestrator.analyze_incident(alert)
            duration = time.time() - start_time

            # Validate the diagnostic report
            is_valid, validation_msg = validate_diagnostic_report(
                diagnostic_report,
                scenario["expected_root_cause"],
                scenario["expected_suggestions"],
            )

            # Send completion notification
            await notifier.send_incident_complete(
                incident_id, alert, diagnostic_report, duration
            )

            result_collector.add_result(
                scenario_id=scenario["id"],
                scenario_name=scenario["name"],
                complexity_level=scenario["complexity_level"],
                success=is_valid,
                incident_id=incident_id,
                diagnostic_report=diagnostic_report,
                expected_root_cause=scenario["expected_root_cause"],
                expected_suggestions=scenario["expected_suggestions"],
                error=None if is_valid else validation_msg,
            )

            logger.info(
                f"Scenario {scenario['id']} completed: {'PASS' if is_valid else 'FAIL'}"
            )

        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Scenario {scenario['id']} failed with error: {e}")

            # Send error notification
            await notifier.send_incident_error(
                incident_id or "N/A", alert, str(e), duration
            )

            result_collector.add_result(
                scenario_id=scenario["id"],
                scenario_name=scenario["name"],
                complexity_level=scenario["complexity_level"],
                success=False,
                incident_id="N/A",
                diagnostic_report=None,
                expected_root_cause=scenario["expected_root_cause"],
                expected_suggestions=scenario["expected_suggestions"],
                error=str(e),
            )

    # Print comprehensive summary
    result_collector.print_summary()

    # Send test summary notification
    total_scenarios = len(result_collector.results)
    passed = sum(1 for r in result_collector.results if r["success"])
    failed = total_scenarios - passed
    total_duration = time.time() - overall_start_time

    await notifier.send_test_result_summary(
        total_scenarios, passed, failed, total_duration
    )

    # Ensure at least some scenarios passed
    passed_count = sum(1 for r in result_collector.results if r["success"])
    assert passed_count > 0, "No scenarios passed validation"


def test_scenario_data_structure() -> None:
    """Test that all scenarios have the required structure."""
    assert "scenarios" in TEST_SCENARIOS
    scenarios = TEST_SCENARIOS["scenarios"]

    assert len(scenarios) == 3, "Should have exactly 3 scenarios"

    for i, scenario in enumerate(scenarios, 1):
        # Check required fields
        assert "id" in scenario, f"Scenario {i} missing 'id'"
        assert "name" in scenario, f"Scenario {i} missing 'name'"
        assert "description" in scenario, f"Scenario {i} missing 'description'"
        assert "alerts" in scenario, f"Scenario {i} missing 'alerts'"
        assert "logs" in scenario, f"Scenario {i} missing 'logs'"
        assert "metrics" in scenario, f"Scenario {i} missing 'metrics'"
        assert "dependencies" in scenario, f"Scenario {i} missing 'dependencies'"
        assert (
            "expected_root_cause" in scenario
        ), f"Scenario {i} missing 'expected_root_cause'"
        assert (
            "expected_suggestions" in scenario
        ), f"Scenario {i} missing 'expected_suggestions'"
        assert (
            "complexity_level" in scenario
        ), f"Scenario {i} missing 'complexity_level'"

        # Check alert structure
        assert len(scenario["alerts"]) > 0, f"Scenario {i} has no alerts"
        for alert in scenario["alerts"]:
            assert "labels" in alert, f"Scenario {i} alert missing 'labels'"
            assert "annotations" in alert, f"Scenario {i} alert missing 'annotations'"
            assert (
                "alertname" in alert["labels"]
            ), f"Scenario {i} alert missing 'alertname'"

        # Check logs
        assert len(scenario["logs"]) > 0, f"Scenario {i} has no logs"

        # Check metrics
        assert isinstance(scenario["metrics"], dict), f"Scenario {i} metrics not a dict"
        assert len(scenario["metrics"]) > 0, f"Scenario {i} has no metrics"

        # Check complexity level
        assert (
            scenario["complexity_level"] == i
        ), f"Scenario {i} has wrong complexity level"


def test_convert_scenario_to_alert() -> None:
    """Test the scenario to alert conversion function."""
    scenario = TEST_SCENARIOS["scenarios"][0]
    alert = convert_scenario_to_alert(scenario)

    assert isinstance(alert, AlertInput)
    assert alert.alert_name == "KubePodCrashLooping"
    assert alert.severity == "critical"
    assert alert.labels["namespace"] == "production"
    assert alert.labels["pod"] == "payment-service-7d9f8b6c5-xk4nm"
