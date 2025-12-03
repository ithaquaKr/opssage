# Test Scenario Alerts for OpsSage

This directory contains JSON alert files based on the test scenarios defined in `tests/test_scenarios.py`. These alerts can be used to test the OpsSage system with realistic, complex incidents.

## Scenario 1: Pod CrashLoopBackOff - Misconfigured Environment Variable

**Complexity Level:** 1 (Simple)

**Description:** A single microservice pod enters CrashLoopBackOff due to a misconfigured environment variable.

**Alert Files:**

- `scenario_1_pod_crashloop.json` - Pod crash looping alert

**Expected Root Cause:** Misconfigured environment variable DATABASE_URL in the pod deployment configuration

**Test Command:**

```bash
curl -X POST http://localhost:8000/api/v1/alerts \
  -H 'Content-Type: application/json' \
  -d @alerts/scenario_1_pod_crashloop.json
```

---

## Scenario 2: Node CPU Exhaustion - Resource Saturation

**Complexity Level:** 2 (Moderate)

**Description:** A Kubernetes node experiences CPU saturation, causing pod throttling and degraded service performance.

**Alert Files:**

1. `scenario_2_node_cpu.json` - High CPU usage on worker node
2. `scenario_2_node_not_ready.json` - Node intermittently not ready
3. `scenario_2_pod_throttling.json` - Pod experiencing CPU throttling

**Expected Root Cause:** CPU resource exhaustion on worker-node-03 due to analytics-worker pod consuming resources without proper limits, causing node-level performance degradation and pod throttling

**Test Commands:**

```bash
# Send all three alerts to simulate the complete scenario
curl -X POST http://localhost:8000/api/v1/alerts \
  -H 'Content-Type: application/json' \
  -d @alerts/scenario_2_node_cpu.json

sleep 2

curl -X POST http://localhost:8000/api/v1/alerts \
  -H 'Content-Type: application/json' \
  -d @alerts/scenario_2_pod_throttling.json

sleep 3

curl -X POST http://localhost:8000/api/v1/alerts \
  -H 'Content-Type: application/json' \
  -d @alerts/scenario_2_node_not_ready.json
```

---

## Scenario 3: Multi-Service Dependency Failure - Cascading Authentication Service Outage

**Complexity Level:** 3 (Complex)

**Description:** Authentication Service failure propagates to dependent services (Order Service, Payment Service), producing cascading errors.

**Alert Files:**

1. `scenario_3_auth_down.json` - Auth service is down
2. `scenario_3_auth_errors.json` - Auth service error rate is critically high
3. `scenario_3_order_500s.json` - Order service experiencing high 500 error rate
4. `scenario_3_payment_dependency.json` - Payment service cannot reach auth-service

**Expected Root Cause:** Configuration regression in auth-service JWT signing key after recent deployment, causing token signature validation failures and cascading authentication errors across dependent services

**Test Commands:**

```bash
# Send alerts in chronological order to simulate the cascading failure
curl -X POST http://localhost:8000/api/v1/alerts \
  -H 'Content-Type: application/json' \
  -d @alerts/scenario_3_auth_errors.json

sleep 2

curl -X POST http://localhost:8000/api/v1/alerts \
  -H 'Content-Type: application/json' \
  -d @alerts/scenario_3_auth_down.json

sleep 1

curl -X POST http://localhost:8000/api/v1/alerts \
  -H 'Content-Type: application/json' \
  -d @alerts/scenario_3_payment_dependency.json

sleep 2

curl -X POST http://localhost:8000/api/v1/alerts \
  -H 'Content-Type: application/json' \
  -d @alerts/scenario_3_order_500s.json
```

---

## Automated Scenario Testing

### Test All Scenarios at Once

```bash
# Scenario 1
echo "Testing Scenario 1: Pod CrashLoopBackOff..."
curl -X POST http://localhost:8000/api/v1/alerts \
  -H 'Content-Type: application/json' \
  -d @alerts/scenario_1_pod_crashloop.json
sleep 5

# Scenario 2
echo "Testing Scenario 2: Node CPU Exhaustion..."
for alert in alerts/scenario_2_*.json; do
  echo "Sending: $alert"
  curl -X POST http://localhost:8000/api/v1/alerts \
    -H 'Content-Type: application/json' \
    -d @"$alert"
  sleep 2
done
sleep 5

# Scenario 3
echo "Testing Scenario 3: Cascading Auth Failure..."
for alert in alerts/scenario_3_*.json; do
  echo "Sending: $alert"
  curl -X POST http://localhost:8000/api/v1/alerts \
    -H 'Content-Type: application/json' \
    -d @"$alert"
  sleep 2
done
```

### View Incident Details

```bash
# List all incidents
curl http://localhost:8000/api/v1/incidents | jq .

# Get specific incident details
curl http://localhost:8000/api/v1/incidents/<INCIDENT_ID> | jq .
```

---

## Expected System Behavior

The OpsSage Multi-Agent System should:

1. **AICA (Alert Ingestion & Context Agent):**

    - Ingest each alert
    - Extract relevant context from labels and annotations
    - Group related alerts into incidents
    - Enrich with additional metadata

2. **KREA (Knowledge Retrieval & Enrichment Agent):**

    - Retrieve relevant logs and metrics
    - Query historical incident data
    - Enrich context with dependency information
    - Provide additional knowledge for analysis

3. **RCARA (Root Cause Analysis & Remediation Agent):**
    - Analyze the enriched context
    - Identify root cause(s)
    - Generate remediation suggestions
    - Prioritize actions based on impact

---

## Validation Criteria

### Scenario 1 Success Criteria

- Root cause identified: Misconfigured DATABASE_URL environment variable
- Suggestions include: Validate env var, check ConfigMap/Secret, redeploy with correct config

### Scenario 2 Success Criteria

- Root cause identified: CPU resource exhaustion on worker-node-03
- Correlation between node CPU, pod throttling, and node NotReady status
- Suggestions include: Adjust resource limits, enable HPA, scale node pool

### Scenario 3 Success Criteria

- Root cause identified: JWT signing key configuration issue in auth-service
- Dependency chain identified: auth-service → order-service, payment-service
- Cascading failure pattern recognized
- Suggestions include: Rollback, implement circuit breakers, graceful degradation

---

## Notes

- Alert timestamps are set to 2025-11-29 to match test scenarios
- Adjust the API_URL if your OpsSage backend is running on a different host/port
- Use `jq` for pretty-printed JSON output
- Monitor logs to see the multi-agent system processing these alerts
