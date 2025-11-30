#!/bin/bash
# OpsSage Alert Testing Script
# Send various incident alerts to test the system

set -e

# Configuration
API_URL="${API_URL:-http://localhost:8000}"
ALERT_ENDPOINT="${API_URL}/api/v1/alerts"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored messages
print_info() {
    echo -e "${BLUE}ℹ ${1}${NC}"
}

print_success() {
    echo -e "${GREEN}✓ ${1}${NC}"
}

print_error() {
    echo -e "${RED}✗ ${1}${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ ${1}${NC}"
}

# Function to send alert and display result
send_alert() {
    local scenario_name=$1
    local json_file=$2

    print_info "Sending alert: ${scenario_name}"

    response=$(curl -s -X POST "${ALERT_ENDPOINT}" \
        -H 'Content-Type: application/json' \
        -d @"${json_file}" \
        -w "\n%{http_code}")

    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')

    if [ "$http_code" -eq 200 ] || [ "$http_code" -eq 201 ]; then
        incident_id=$(echo "$body" | python3 -c "import sys, json; print(json.load(sys.stdin).get('incident_id', 'N/A'))" 2>/dev/null || echo "N/A")
        print_success "Alert sent successfully (HTTP ${http_code})"
        print_info "Incident ID: ${incident_id}"
        echo
    else
        print_error "Failed to send alert (HTTP ${http_code})"
        echo "$body" | python3 -m json.tool 2>/dev/null || echo "$body"
        echo
    fi
}

# Main script
main() {
    echo "========================================"
    echo "OpsSage Alert Testing"
    echo "========================================"
    echo
    print_info "API URL: ${API_URL}"
    echo

    # Check if backend is healthy
    print_info "Checking backend health..."
    if curl -s -f "${API_URL}/api/v1/health" > /dev/null 2>&1; then
        print_success "Backend is healthy"
    else
        print_error "Backend is not responding"
        exit 1
    fi
    echo

    # Parse arguments
    scenario="${1:-all}"

    case "$scenario" in
        1|crashloop)
            send_alert "Scenario 1: Pod CrashLoopBackOff" "$(dirname $0)/alerts/01_crashloop.json"
            ;;
        2|cpu)
            send_alert "Scenario 2: Node CPU Exhaustion" "$(dirname $0)/alerts/02_cpu_exhaustion.json"
            ;;
        3|oom)
            send_alert "Scenario 3: OOM Kill" "$(dirname $0)/alerts/03_oom_kill.json"
            ;;
        4|disk)
            send_alert "Scenario 4: Disk Pressure" "$(dirname $0)/alerts/04_disk_pressure.json"
            ;;
        5|network)
            send_alert "Scenario 5: Network Latency" "$(dirname $0)/alerts/05_network_latency.json"
            ;;
        6|database)
            send_alert "Scenario 6: Database Connection Pool" "$(dirname $0)/alerts/06_db_connections.json"
            ;;
        7|service)
            send_alert "Scenario 7: Service Unavailable" "$(dirname $0)/alerts/07_service_down.json"
            ;;
        8|deployment)
            send_alert "Scenario 8: Failed Deployment" "$(dirname $0)/alerts/08_failed_deployment.json"
            ;;
        all)
            print_warning "Sending ALL test scenarios..."
            echo
            send_alert "Scenario 1: Pod CrashLoopBackOff" "$(dirname $0)/alerts/01_crashloop.json"
            sleep 2
            send_alert "Scenario 2: Node CPU Exhaustion" "$(dirname $0)/alerts/02_cpu_exhaustion.json"
            sleep 2
            send_alert "Scenario 3: OOM Kill" "$(dirname $0)/alerts/03_oom_kill.json"
            sleep 2
            send_alert "Scenario 4: Disk Pressure" "$(dirname $0)/alerts/04_disk_pressure.json"
            sleep 2
            send_alert "Scenario 5: Network Latency" "$(dirname $0)/alerts/05_network_latency.json"
            sleep 2
            send_alert "Scenario 6: Database Connection Pool" "$(dirname $0)/alerts/06_db_connections.json"
            sleep 2
            send_alert "Scenario 7: Service Unavailable" "$(dirname $0)/alerts/07_service_down.json"
            sleep 2
            send_alert "Scenario 8: Failed Deployment" "$(dirname $0)/alerts/08_failed_deployment.json"
            ;;
        *)
            echo "Usage: $0 [scenario]"
            echo
            echo "Scenarios:"
            echo "  1 | crashloop   - Pod CrashLoopBackOff"
            echo "  2 | cpu         - Node CPU Exhaustion"
            echo "  3 | oom         - OOM Kill"
            echo "  4 | disk        - Disk Pressure"
            echo "  5 | network     - Network Latency"
            echo "  6 | database    - Database Connection Pool"
            echo "  7 | service     - Service Unavailable"
            echo "  8 | deployment  - Failed Deployment"
            echo "  all             - Send all scenarios (default)"
            echo
            echo "Examples:"
            echo "  $0              # Send all scenarios"
            echo "  $0 1            # Send only crashloop scenario"
            echo "  $0 crashloop    # Send only crashloop scenario"
            exit 1
            ;;
    esac

    print_success "Testing completed!"
}

main "$@"
