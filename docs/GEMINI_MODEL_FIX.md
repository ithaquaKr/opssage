# Gemini Model Configuration Fix

## Problem

When running OpsSage, you may encounter this error:

```
Error: 404 NOT_FOUND. {'error': {'code': 404, 'message': 'models/gemini-1.5-flash is not found for API version v1beta, or is not supported for generateContent. Call ListModels to see the list of available models and their supported methods.', 'status': 'NOT_FOUND'}}
```

## Root Cause

The Google Generative AI SDK and ADK require specific model naming conventions. The model names `gemini-1.5-flash` and `gemini-1.5-pro` are not recognized by the API.

## Solution

Use the `-latest` suffix for model names to ensure compatibility:

### ✅ Correct Model Names

```yaml
models:
  worker_model: gemini-1.5-flash-latest
  critic_model: gemini-1.5-pro-latest
```

### ❌ Incorrect Model Names

```yaml
models:
  worker_model: gemini-1.5-flash  # Will cause 404 error
  critic_model: gemini-1.5-pro    # Will cause 404 error
```

## Files Updated

The following files have been updated with the correct model names:

1. **config.yaml** - Main configuration file
2. **config.example.yaml** - Template configuration file

## Applying the Fix

### Option 1: Use Updated Config (Recommended)

If you're using Docker:

```bash
# Restart backend to reload configuration
docker-compose restart backend

# Verify it's working
curl http://localhost:8000/api/v1/health
```

### Option 2: Manual Update

If you have a custom `config.yaml`:

1. Open `config.yaml`
2. Update the model names:
   ```yaml
   models:
     worker_model: gemini-1.5-flash-latest
     critic_model: gemini-1.5-pro-latest
   ```
3. Restart the backend:
   ```bash
   docker-compose restart backend
   # or if running locally:
   # Ctrl+C and run: python run.py
   ```

## Available Model Names

Google's Generative AI models use the following naming convention:

### Flash Models (Fast, Cost-Effective)
- `gemini-1.5-flash-latest` - Latest stable version
- `gemini-1.5-flash-001` - Specific version
- `gemini-1.5-flash-002` - Specific version

### Pro Models (More Capable)
- `gemini-1.5-pro-latest` - Latest stable version
- `gemini-1.5-pro-001` - Specific version
- `gemini-1.5-pro-002` - Specific version

### Experimental Models
- `gemini-2.0-flash-exp` - Experimental Gemini 2.0
- `gemini-exp-1206` - Dated experimental version

## Verification

To verify the fix is working:

### 1. Check Backend Health

```bash
curl http://localhost:8000/api/v1/health
```

Expected output:
```json
{
  "status": "healthy",
  "components": {
    "orchestrator": "ok",
    "context_store": "ok"
  }
}
```

### 2. Check Backend Logs

```bash
docker logs opssage-backend --tail 20
```

Look for successful startup without model errors:
```
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 3. Test with a Simple Alert (Optional)

```bash
curl -X POST http://localhost:8000/api/v1/incidents/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "alert_name": "TestAlert",
    "severity": "critical",
    "message": "Test message",
    "labels": {"namespace": "test"},
    "annotations": {},
    "firing_condition": "test > 0",
    "timestamp": "2025-11-30T00:00:00Z"
  }'
```

If configured correctly, this will trigger the incident analysis flow using the correct model names.

## Model Selection Guide

### When to Use Flash (`gemini-1.5-flash-latest`)

- ✅ Real-time incident analysis (AICA, KREA)
- ✅ High-volume operations
- ✅ Cost-sensitive workloads
- ✅ Sub-agents that need quick responses

**Used by:**
- AICA (Alert Ingestion & Context Agent)
- KREA (Knowledge Retrieval & Enrichment Agent)

### When to Use Pro (`gemini-1.5-pro-latest`)

- ✅ Complex reasoning tasks (RCARA)
- ✅ Root cause analysis
- ✅ Critical decision-making
- ✅ Higher accuracy requirements

**Used by:**
- RCARA (Root Cause Analysis & Remediation Agent)

## Troubleshooting

### Still Getting 404 Errors?

1. **Check API Key**: Ensure `GEMINI_API_KEY` is set correctly
   ```bash
   echo $GEMINI_API_KEY
   ```

2. **Verify Model Access**: Some models require API allowlisting
   ```bash
   curl "https://generativelanguage.googleapis.com/v1beta/models?key=$GEMINI_API_KEY" | jq '.models[].name'
   ```

3. **Check Configuration Loading**:
   ```bash
   docker exec opssage-backend cat /app/config.yaml | grep -A 3 "models:"
   ```

### Model Not Available in Your Region?

If certain models aren't available:

1. Check Google AI Studio for regional availability
2. Try alternative models:
   ```yaml
   models:
     worker_model: gemini-1.0-pro-latest
     critic_model: gemini-1.5-pro-latest
   ```

### API Quota Exceeded?

Monitor your API usage at: https://aistudio.google.com/

## Additional Resources

- [Google Generative AI Models](https://ai.google.dev/models/gemini)
- [Model Naming Conventions](https://ai.google.dev/gemini-api/docs/models/gemini)
- [Google ADK Documentation](https://github.com/google/genai-adk-python)

## Summary

✅ **Fixed**: Updated model names to use `-latest` suffix
✅ **Applied**: Configuration updated in both `config.yaml` and `config.example.yaml`
✅ **Verified**: Backend is healthy and running with correct model configuration

The 404 error should now be resolved, and OpsSage will use the correct Gemini model names for all agent operations.
