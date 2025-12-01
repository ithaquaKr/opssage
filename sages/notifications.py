"""
Notification system for sending alerts and incident reports.
Supports multiple notification channels including Telegram.
"""

import logging

import httpx

from sages.config import get_config
from sages.models import AlertInput, IncidentDiagnosticReport

logger = logging.getLogger(__name__)


class TelegramNotifier:
    """Send notifications via Telegram Bot API."""

    def __init__(self, bot_token: str | None = None, chat_id: str | None = None):
        """
        Initialize Telegram notifier.

        Args:
            bot_token: Telegram bot token (will use config if not provided)
            chat_id: Telegram chat ID (will use config if not provided)
        """
        config = get_config()
        self.bot_token = bot_token or config.get("telegram.bot_token")
        self.chat_id = chat_id or config.get("telegram.chat_id")
        self.dashboard_url = config.get(
            "telegram.dashboard_url", "http://localhost:3000"
        )
        self.enabled = config.get("telegram.enabled", True) and bool(
            self.bot_token and self.chat_id
        )

        if not self.enabled:
            logger.warning(
                "Telegram notifications disabled: Check config.yaml telegram settings"
            )

    async def send_message(self, message: str, parse_mode: str = "HTML") -> bool:
        """
        Send a message to Telegram.

        Args:
            message: Message text to send
            parse_mode: Parse mode (Markdown, HTML, or None)

        Returns:
            True if message was sent successfully, False otherwise
        """
        if not self.enabled:
            logger.debug("Telegram not enabled, skipping notification")
            return False

        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": message,
            "parse_mode": parse_mode,
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                logger.info(
                    f"Telegram notification sent successfully to chat {self.chat_id}"
                )
                return True
        except Exception as e:
            logger.error(f"Failed to send Telegram notification: {e}")
            return False

    async def send_incident_start(self, incident_id: str, alert: AlertInput) -> bool:
        """
        Send notification when incident analysis starts.

        Args:
            incident_id: Unique incident identifier
            alert: The alert that triggered the incident

        Returns:
            True if notification was sent successfully
        """
        incident_url = f"{self.dashboard_url}/incidents/{incident_id}"

        # Truncate message if too long
        msg = alert.message
        if len(msg) > 150:
            msg = msg[:147] + "..."

        message = f"""
🚨 <b>Incident Analysis Started</b>

<b>Alert:</b> {alert.alert_name}
<b>Severity:</b> {alert.severity.upper()}
<b>Namespace:</b> {alert.labels.get('namespace', 'N/A')}
<b>Service:</b> {alert.labels.get('service', 'N/A')}

<b>Message:</b> {msg}

⏳ Analysis in progress...

<a href="{incident_url}">View Full Details</a>
"""
        return await self.send_message(message.strip())

    async def send_incident_complete(
        self,
        incident_id: str,
        alert: AlertInput,
        diagnostic_report: IncidentDiagnosticReport,
        duration_seconds: float,
    ) -> bool:
        """
        Send notification when incident analysis completes.

        Args:
            incident_id: Unique incident identifier
            alert: The alert that triggered the incident
            diagnostic_report: The diagnostic report from analysis
            duration_seconds: How long the analysis took

        Returns:
            True if notification was sent successfully
        """
        incident_url = f"{self.dashboard_url}/incidents/{incident_id}"

        # Format confidence score as percentage
        confidence_pct = int(diagnostic_report.confidence_score * 100)

        # Truncate root cause if too long
        root_cause = diagnostic_report.root_cause
        if len(root_cause) > 150:
            root_cause = root_cause[:147] + "..."

        # Format top 2 immediate actions only
        actions = diagnostic_report.recommended_remediation.short_term_actions[:2]
        short_term = "\n".join(f"  • {action}" for action in actions)
        remaining = (
            len(diagnostic_report.recommended_remediation.short_term_actions) - 2
        )
        if remaining > 0:
            short_term += (
                f"\n  • +{remaining} more action{'s' if remaining > 1 else ''}"
            )

        message = f"""
✅ <b>Incident Analysis Complete</b>

<b>Alert:</b> {alert.alert_name}
<b>Duration:</b> {duration_seconds:.1f}s

🎯 <b>Root Cause</b> ({confidence_pct}%):
{root_cause}

🔧 <b>Top Actions:</b>
{short_term}

<a href="{incident_url}">📊 View Full Report</a>
"""
        return await self.send_message(message.strip())

    async def send_incident_error(
        self,
        incident_id: str,
        alert: AlertInput,
        error: str,
        duration_seconds: float,
    ) -> bool:
        """
        Send notification when incident analysis fails.

        Args:
            incident_id: Unique incident identifier
            alert: The alert that triggered the incident
            error: Error message
            duration_seconds: How long the analysis took before failing

        Returns:
            True if notification was sent successfully
        """
        incident_url = f"{self.dashboard_url}/incidents/{incident_id}"

        # Truncate error if too long
        error_msg = str(error)
        if len(error_msg) > 200:
            error_msg = error_msg[:197] + "..."

        message = f"""
❌ <b>Incident Analysis Failed</b>

<b>Alert:</b> {alert.alert_name}
<b>Duration:</b> {duration_seconds:.1f}s

⚠️ <b>Error:</b>
<pre>{error_msg}</pre>

<a href="{incident_url}">View Incident Details</a>
"""
        return await self.send_message(message.strip())

    async def send_test_result_summary(
        self,
        total_scenarios: int,
        passed: int,
        failed: int,
        duration_seconds: float,
    ) -> bool:
        """
        Send test result summary notification.

        Args:
            total_scenarios: Total number of test scenarios
            passed: Number of passed tests
            failed: Number of failed tests
            duration_seconds: Total test duration

        Returns:
            True if notification was sent successfully
        """
        success_rate = (passed / total_scenarios * 100) if total_scenarios > 0 else 0
        status_emoji = "✅" if failed == 0 else "⚠️"

        message = f"""
{status_emoji} <b>E2E Test Results</b>

<b>Total Scenarios:</b> {total_scenarios}
✅ <b>Passed:</b> {passed}
❌ <b>Failed:</b> {failed}
📊 <b>Success Rate:</b> {success_rate:.1f}%
⏱️ <b>Duration:</b> {duration_seconds:.1f}s

{self._get_status_bar(passed, failed)}
"""
        return await self.send_message(message.strip())

    def _get_status_bar(self, passed: int, failed: int) -> str:
        """Generate a visual status bar."""
        total = passed + failed
        if total == 0:
            return ""

        passed_blocks = int((passed / total) * 10)
        failed_blocks = 10 - passed_blocks

        bar = "█" * passed_blocks + "▓" * failed_blocks
        return f"`[{bar}]`"


# Global notifier instance
_notifier: TelegramNotifier | None = None


def get_notifier() -> TelegramNotifier:
    """
    Get the global TelegramNotifier instance.

    Returns:
        TelegramNotifier instance
    """
    global _notifier
    if _notifier is None:
        _notifier = TelegramNotifier()
    return _notifier
