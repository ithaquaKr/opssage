# Pydantic Validation Error Fix

## Problem

When running E2E tests, the system encountered a Pydantic validation error:

```
2025-12-01 01:12:03,732 - sages.orchestrator - ERROR - Error analyzing incident 77229fc3-4347-496f-bc16-be042ec2eaa0: 1 validation error for AICAOutput
primary_context_package.affected_components.node
  Input should be a valid string [type=string_type, input_value=None, input_type=NoneType]
    For further information visit https://errors.pydantic.dev/2.12/v/string_type
```

Additionally, there was a deprecation warning:

```
DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
```

## Root Cause

### Issue 1: Validation Error

The `AffectedComponents` model in `sages/models.py` defined all fields as required strings with default values:

```python
class AffectedComponents(BaseModel):
    service: str = Field("", description="Affected service name")
    namespace: str = Field("", description="Kubernetes namespace")
    pod: str = Field("", description="Affected pod name")
    node: str = Field("", description="Affected node name")
```

The AICA agent was returning `None` for fields when information wasn't available, but Pydantic expected strings. While default values exist, they only apply when fields are omitted, not when explicitly set to `None`.

### Issue 2: Datetime Deprecation

Python 3.13 deprecated `datetime.utcnow()` in favor of timezone-aware datetimes using `datetime.now(UTC)`.

## Solution

### Fix 1: Make Fields Optional

Updated `AffectedComponents` to accept `None` values (sages/models.py:25-31):

```python
class AffectedComponents(BaseModel):
    """Components affected by the incident."""

    service: str | None = Field(None, description="Affected service name")
    namespace: str | None = Field(None, description="Kubernetes namespace")
    pod: str | None = Field(None, description="Affected pod name")
    node: str | None = Field(None, description="Affected node name")
```

### Fix 2: Update AICA Prompt

Updated the AICA system prompt to reflect that fields can be null (sages/subagents/aica.py:54-59):

```python
"affected_components": {
  "service": "string or null",
  "namespace": "string or null",
  "pod": "string or null",
  "node": "string or null"
},
```

### Fix 3: Replace datetime.utcnow()

Replaced all occurrences of `datetime.utcnow()` with `datetime.now(UTC)`:

**Files updated:**
- sages/models.py (3 occurrences)
- sages/context_store.py (4 occurrences)
- sages/tools.py (3 occurrences)
- scripts/run_e2e_tests.py (4 occurrences)

**Example change:**

```python
# Before
from datetime import datetime
timestamp: datetime = Field(default_factory=datetime.utcnow, ...)

# After
from datetime import UTC, datetime
timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC), ...)
```

## Files Modified

1. **sages/models.py**
   - Added `UTC` import
   - Changed `AffectedComponents` fields to `str | None`
   - Updated `default_factory` to use `datetime.now(UTC)`

2. **sages/subagents/aica.py**
   - Updated system prompt to specify fields can be null

3. **sages/context_store.py**
   - Added `UTC` import
   - Replaced `datetime.utcnow()` → `datetime.now(UTC)`

4. **sages/tools.py**
   - Added `UTC` import
   - Replaced `datetime.utcnow()` → `datetime.now(UTC)`

5. **scripts/run_e2e_tests.py**
   - Added `UTC` import
   - Replaced `datetime.utcnow()` → `datetime.now(UTC)`

## Verification

### Test 1: Model Validation

```bash
docker exec opssage-backend python -c "
from sages.models import AffectedComponents
ac = AffectedComponents(node=None, service='test-service', namespace='test-ns', pod=None)
print('✓ Model validation passed with None values')
print(f'Node: {ac.node}, Service: {ac.service}, Namespace: {ac.namespace}, Pod: {ac.pod}')
"
```

**Result:**
```
✓ Model validation passed with None values
Node: None, Service: test-service, Namespace: test-ns, Pod: None
```

### Test 2: Datetime UTC

```bash
docker exec opssage-backend python -c "
from sages.models import AlertInput
from datetime import datetime, UTC
alert = AlertInput(
    alert_name='TestAlert',
    severity='critical',
    message='Test message',
    firing_condition='test > 0'
)
print(f'✓ AlertInput created with default timestamp: {alert.timestamp}')
print(f'  Timezone aware: {alert.timestamp.tzinfo is not None}')
"
```

**Result:**
```
✓ AlertInput created with default timestamp: 2025-11-30 18:16:29.394210+00:00
  Timezone aware: True
```

### Test 3: Backend Health

```bash
curl http://localhost:8000/api/v1/health
```

**Result:**
```json
{"status":"healthy","components":{"orchestrator":"ok","context_store":"ok"}}
```

## Impact

### Positive

1. **Flexibility**: The system now handles alerts gracefully when some component information is unavailable
2. **Compliance**: No more deprecation warnings in Python 3.13+
3. **Correctness**: All timestamps are now timezone-aware (UTC)
4. **Robustness**: The system can process a wider range of alert formats

### Compatibility

- **No breaking changes**: The fields can still accept strings as before
- **Backward compatible**: Existing code that provides strings continues to work
- **Forward compatible**: Prepared for Python 3.14+ when `datetime.utcnow()` will be removed

## Testing Recommendations

1. **Run E2E Tests**: Verify all scenarios pass without validation errors
   ```bash
   pytest tests/test_e2e_scenarios.py -v
   ```

2. **Test with Various Alert Formats**: Ensure system handles alerts with missing component info
   ```bash
   # Alert with minimal information
   curl -X POST http://localhost:8000/api/v1/alerts \
     -H "Content-Type: application/json" \
     -d '{
       "alert_name": "TestAlert",
       "severity": "warning",
       "message": "Test",
       "labels": {},
       "annotations": {},
       "firing_condition": "test > 0",
       "timestamp": "2025-11-30T18:00:00Z"
     }'
   ```

3. **Verify Telegram Notifications**: Test notification flow works correctly
   ```bash
   pytest tests/test_telegram_integration.py -v
   ```

## Summary

✅ **Fixed**: Pydantic validation error for `affected_components.node`
✅ **Fixed**: Deprecated `datetime.utcnow()` usage across codebase
✅ **Updated**: AICA prompt to reflect optional fields
✅ **Verified**: Backend health and model validation working correctly

The system is now more robust and can handle alerts with incomplete component information while maintaining Python 3.13+ compatibility.
