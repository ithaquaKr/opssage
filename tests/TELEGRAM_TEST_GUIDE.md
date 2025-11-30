# Telegram Integration Testing Guide

Quick reference for testing Telegram notifications in OpsSage.

## Quick Start

### 1. Set Up Telegram Bot (One-Time Setup)

```bash
# 1. Create bot with BotFather
# Open Telegram → Search @BotFather → /newbot → Follow prompts

# 2. Get your Chat ID
# Start chat with your bot → Send any message → Visit:
# https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates

# 3. Set environment variables
export TELEGRAM_BOT_TOKEN="1234567890:ABCdefGHIjklMNOpqrsTUVwxyz"
export TELEGRAM_CHAT_ID="123456789"
```

### 2. Run Tests

```bash
# Run all Telegram tests
pytest tests/test_telegram_integration.py -v

# Run specific test
pytest tests/test_telegram_integration.py::test_send_simple_message -v -s

# Run with live output
pytest tests/test_telegram_integration.py -v -s
```

## Test Coverage

### Basic Functionality (17 tests)

✅ **Configuration Tests**

- Notifier initialization with config
- Custom credentials handling
- Singleton pattern verification
- Disabled state handling

✅ **Message Sending**

- Simple text messages
- Markdown formatting
- Special characters and emojis
- Long message truncation

✅ **Incident Notifications**

- Start notification
- Completion notification with diagnostic report
- Error notification
- Full lifecycle flow

✅ **Advanced Features**

- Test result summaries
- Concurrent notifications
- Status bar visualization

## Test Output Examples

### Successful Test Run

```bash
$ pytest tests/test_telegram_integration.py -v

tests/test_telegram_integration.py::TestTelegramNotifier::test_notifier_initialization PASSED
tests/test_telegram_integration.py::TestTelegramNotifier::test_send_simple_message PASSED
tests/test_telegram_integration.py::test_complete_notification_flow PASSED
...

17 passed in 12.5s
```

### Telegram Messages You'll Receive

**1. Simple Test Message:**

```
🧪 Test Message

This is a test message from OpsSage Telegram integration tests.

Timestamp: 2025-11-30T15:30:00.123456
Test ID: test_send_simple_message

✅ If you see this, the integration is working!
```

**2. Incident Start:**

```
🚨 Incident Analysis Started

Incident ID: test-incident-1732976400
Alert: TestAlert
Severity: CRITICAL
Namespace: test-namespace
Service: test-service

Message: Test alert for Telegram integration

⏳ Analysis in progress...
```

**3. Incident Complete:**

```
✅ Incident Analysis Complete

Incident ID: test-incident-1732976400
Alert: TestAlert
Duration: 12.5s

🎯 Root Cause (Confidence: 85%):
Test root cause: Configuration error in test-service deployment

🔧 Immediate Actions:
  • Rollback the deployment to previous stable version
  • Fix the DATABASE_URL environment variable in config map
  • Restart affected pods after config update

📊 Analysis Steps: 3
📝 Evidence Items: 3
```

**4. Test Summary:**

```
✅ E2E Test Results

Total Scenarios: 10
✅ Passed: 8
❌ Failed: 2
📊 Success Rate: 80.0%
⏱️ Duration: 45.5s

[████████▓▓]
```

## Test Categories

### Synchronous Tests (Non-async)

```bash
pytest tests/test_telegram_integration.py::TestTelegramNotifier::test_notifier_initialization
pytest tests/test_telegram_integration.py::TestTelegramNotifier::test_status_bar_generation
pytest tests/test_telegram_integration.py::test_config_loading
```

### Asynchronous Tests (Async)

```bash
pytest tests/test_telegram_integration.py::test_send_simple_message
pytest tests/test_telegram_integration.py::test_complete_notification_flow
pytest tests/test_telegram_integration.py::test_concurrent_notifications
```

## Skipped Tests

Tests will automatically skip if Telegram is not configured:

```
SKIPPED [1] tests/test_telegram_integration.py:95: Telegram not configured, skipping integration test
```

This is expected behavior when:

- No bot token set
- No chat ID set
- `telegram.enabled = false` in config

## Running Tests in CI/CD

### GitHub Actions

```yaml
- name: Run Telegram Integration Tests
  env:
      TELEGRAM_BOT_TOKEN: ${{ secrets.TELEGRAM_BOT_TOKEN }}
      TELEGRAM_CHAT_ID: ${{ secrets.TELEGRAM_CHAT_ID }}
  run: |
      pytest tests/test_telegram_integration.py -v
```

### Skip Telegram Tests in CI

```bash
# Run all tests except Telegram integration
pytest tests/ -v -m "not telegram"

# Or just run E2E tests
pytest tests/test_e2e_scenarios.py -v
```

## Troubleshooting

### "Telegram not configured" - Tests Skipped

**Solution:**

```bash
# Check environment variables are set
echo $TELEGRAM_BOT_TOKEN
echo $TELEGRAM_CHAT_ID

# Check config.yaml
cat config.yaml | grep -A 3 "telegram:"
```

### "HTTP 401 Unauthorized"

**Problem:** Invalid bot token

**Solution:**

```bash
# Verify token works
curl "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/getMe"
```

### "HTTP 400 Bad Request: chat not found"

**Problem:** Wrong chat ID or bot not started

**Solution:**

1. Open Telegram
2. Search for your bot
3. Click "START" or send any message
4. Get chat ID again from getUpdates

### Messages Not Arriving

**Check:**

1. Bot is not blocked in Telegram
2. Chat ID is correct (positive number for personal chat)
3. Network connectivity to api.telegram.org
4. Bot token hasn't been revoked

## Advanced Usage

### Test with Custom Notifier

```python
@pytest.mark.asyncio
async def test_custom_notifier():
    # Create notifier with custom settings
    notifier = TelegramNotifier(
        bot_token="custom_token",
        chat_id="custom_chat"
    )

    # Send test message
    success = await notifier.send_message("Custom test")
    assert success
```

### Mock Telegram API for Unit Tests

```python
from unittest.mock import patch, AsyncMock

@pytest.mark.asyncio
async def test_with_mock():
    with patch('httpx.AsyncClient.post', new_callable=AsyncMock) as mock_post:
        mock_post.return_value.status_code = 200

        notifier = TelegramNotifier()
        success = await notifier.send_message("Test")

        assert success
        mock_post.assert_called_once()
```

## Performance

Expected test execution times:

- **Non-async tests**: < 1 second
- **Single async test**: 1-2 seconds
- **All 17 tests**: 10-15 seconds
- **With rate limiting**: Up to 30 seconds

Rate limiting is built into tests (1 second delay between messages) to avoid hitting Telegram API limits.

## Related Files

- **Test File**: `tests/test_telegram_integration.py`
- **Notifier Implementation**: `sages/notifications.py`
- **Configuration**: `config.yaml`
- **Test Documentation**: `tests/README.md`

## Next Steps

1. ✅ Run basic tests to verify setup
2. ✅ Check Telegram for test messages
3. ✅ Review test coverage
4. 🔄 Integrate with CI/CD pipeline
5. 🔄 Add custom test scenarios as needed

## Support

For issues or questions:

- Check `tests/README.md` for comprehensive documentation
- Review Telegram Bot API docs: <https://core.telegram.org/bots/api>
- Check OpsSage logs for detailed error messages
