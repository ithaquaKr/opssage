#!/bin/bash
# Quick curl examples for testing OpsSage alerts
# Use these for manual testing without the test script

API_URL="${API_URL:-http://localhost:8000}"

echo "OpsSage Alert Testing - Direct curl Examples"
echo "=============================================="
echo

# Example 1: Simple inline JSON
echo "1. Simple alert (inline JSON):"
echo "-------------------------------"
cat << 'EOF'
curl -X POST http://localhost:8000/api/v1/alerts \
  -H 'Content-Type: application/json' \
  -d '{
    "alert_name": "TestAlert",
    "severity": "critical",
    "message": "Test message",
    "labels": {"namespace": "test"},
    "annotations": {},
    "firing_condition": "test > 0",
    "timestamp": "2025-12-01T00:00:00Z"
  }'
EOF
echo
echo

# Example 2: Using heredoc for better formatting
echo "2. Using heredoc (better formatting):"
echo "--------------------------------------"
cat << 'EOF'
curl -X POST http://localhost:8000/api/v1/alerts \
  -H 'Content-Type: application/json' \
  -d @- << 'ALERT'
{
  "alert_name": "PodCrashLoopBackOff",
  "severity": "critical",
  "message": "Pod is crash looping",
  "labels": {
    "namespace": "production",
    "service": "payment-service"
  },
  "annotations": {
    "summary": "Payment service unstable"
  },
  "firing_condition": "restarts > 10",
  "timestamp": "2025-12-01T00:00:00Z"
}
ALERT
EOF
echo
echo

# Example 3: Using JSON file
echo "3. Using external JSON file:"
echo "----------------------------"
cat << 'EOF'
curl -X POST http://localhost:8000/api/v1/alerts \
  -H 'Content-Type: application/json' \
  -d @alerts/01_crashloop.json
EOF
echo
echo

# Example 4: With pretty-printed output
echo "4. With pretty output (using jq):"
echo "----------------------------------"
cat << 'EOF'
curl -X POST http://localhost:8000/api/v1/alerts \
  -H 'Content-Type: application/json' \
  -d @alerts/01_crashloop.json | jq .
EOF
echo
echo

# Example 5: Verbose output for debugging
echo "5. Verbose mode (debugging):"
echo "----------------------------"
cat << 'EOF'
curl -v -X POST http://localhost:8000/api/v1/alerts \
  -H 'Content-Type: application/json' \
  -d @alerts/01_crashloop.json
EOF
echo
echo

# Example 6: Silent mode with HTTP status
echo "6. Show only HTTP status:"
echo "-------------------------"
cat << 'EOF'
curl -s -o /dev/null -w "%{http_code}\n" \
  -X POST http://localhost:8000/api/v1/alerts \
  -H 'Content-Type: application/json' \
  -d @alerts/01_crashloop.json
EOF
echo
echo

# Example 7: Multiple alerts in sequence
echo "7. Send multiple alerts:"
echo "------------------------"
cat << 'EOF'
for alert in alerts/*.json; do
  echo "Sending: $alert"
  curl -X POST http://localhost:8000/api/v1/alerts \
    -H 'Content-Type: application/json' \
    -d @"$alert"
  echo
  sleep 2
done
EOF
echo
echo

# Example 8: Query incident status
echo "8. Query incident by ID:"
echo "------------------------"
cat << 'EOF'
# First, send an alert and capture the incident ID
INCIDENT_ID=$(curl -s -X POST http://localhost:8000/api/v1/alerts \
  -H 'Content-Type: application/json' \
  -d @alerts/01_crashloop.json | jq -r .incident_id)

# Then query the incident
curl http://localhost:8000/api/v1/incidents/$INCIDENT_ID | jq .
EOF
echo
echo

# Example 9: List all incidents
echo "9. List all incidents:"
echo "----------------------"
cat << 'EOF'
curl http://localhost:8000/api/v1/incidents | jq .
EOF
echo
echo

# Example 10: Health check
echo "10. Check backend health:"
echo "-------------------------"
cat << 'EOF'
curl http://localhost:8000/api/v1/health | jq .
EOF
echo
echo

echo "=============================================="
echo "Ready to test! Copy and paste any example above."
echo
echo "For automated testing, use: ./test_alerts.sh"
echo "=============================================="
