#!/bin/bash
# Test OpsSage with realistic incident scenarios
# Based on scenarios defined in tests/test_scenarios.py

set -e

API_URL="${API_URL:-http://localhost:8000}"
ALERT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/alerts" && pwd)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_header() {
    echo -e "\n${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

send_alert() {
    local file=$1
    local description=$2

    echo -e "${YELLOW}Sending:${NC} $description"
    echo -e "${BLUE}File:${NC} $(basename $file)"

    response=$(curl -s -w "\n%{http_code}" -X POST "$API_URL/api/v1/alerts" \
        -H 'Content-Type: application/json' \
        -d @"$file")

    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')

    if [ "$http_code" -eq 200 ] || [ "$http_code" -eq 201 ]; then
        print_success "Alert sent successfully (HTTP $http_code)"
        echo "$body" | jq -C '.' 2>/dev/null || echo "$body"
    else
        print_error "Failed to send alert (HTTP $http_code)"
        echo "$body"
        return 1
    fi
    echo
}

wait_with_countdown() {
    local seconds=$1
    local message=${2:-"Waiting"}

    for ((i=seconds; i>0; i--)); do
        echo -ne "\r${message} ${i}s...  "
        sleep 1
    done
    echo -ne "\r${message} done!     \n"
}

test_scenario_1() {
    print_header "SCENARIO 1: Pod CrashLoopBackOff"
    echo "Complexity: 1 (Simple)"
    echo "Description: Single pod crash looping due to misconfigured environment variable"
    echo "Expected Root Cause: Misconfigured DATABASE_URL environment variable"
    echo

    send_alert "$ALERT_DIR/scenario_1_pod_crashloop.json" \
        "KubePodCrashLooping - payment-service pod crash looping"

    print_success "Scenario 1 complete"
}

test_scenario_2() {
    print_header "SCENARIO 2: Node CPU Exhaustion"
    echo "Complexity: 2 (Moderate)"
    echo "Description: Node CPU saturation causing pod throttling and degraded performance"
    echo "Expected Root Cause: CPU resource exhaustion on worker-node-03"
    echo

    send_alert "$ALERT_DIR/scenario_2_node_cpu.json" \
        "NodeHighCpuUsage - worker-node-03 CPU critically high"

    wait_with_countdown 2 "Simulating time progression"

    send_alert "$ALERT_DIR/scenario_2_pod_throttling.json" \
        "PodCpuThrottlingHigh - analytics-worker experiencing throttling"

    wait_with_countdown 3 "Simulating time progression"

    send_alert "$ALERT_DIR/scenario_2_node_not_ready.json" \
        "KubeNodeNotReady - worker-node-03 intermittently not ready"

    print_success "Scenario 2 complete - All 3 related alerts sent"
}

test_scenario_3() {
    print_header "SCENARIO 3: Cascading Authentication Service Outage"
    echo "Complexity: 3 (Complex)"
    echo "Description: Auth service failure cascading to dependent services"
    echo "Expected Root Cause: JWT signing key configuration regression in auth-service"
    echo

    send_alert "$ALERT_DIR/scenario_3_auth_errors.json" \
        "ServiceErrorRateHigh - auth-service error rate at 98%"

    wait_with_countdown 2 "Simulating error escalation"

    send_alert "$ALERT_DIR/scenario_3_auth_down.json" \
        "ServiceDown - auth-service health checks failing"

    wait_with_countdown 1 "Simulating failure propagation"

    send_alert "$ALERT_DIR/scenario_3_payment_dependency.json" \
        "DependencyRequestFailure - payment-service cannot reach auth-service"

    wait_with_countdown 2 "Simulating cascade effect"

    send_alert "$ALERT_DIR/scenario_3_order_500s.json" \
        "HTTP500RateIncrease - order-service experiencing 500 errors"

    print_success "Scenario 3 complete - All 4 cascading alerts sent"
}

show_incidents() {
    print_header "FETCHING INCIDENTS"

    echo "Retrieving all incidents from OpsSage..."
    echo

    incidents=$(curl -s "$API_URL/api/v1/incidents")

    if [ $? -eq 0 ]; then
        echo "$incidents" | jq -C '.' 2>/dev/null || echo "$incidents"
    else
        print_error "Failed to fetch incidents"
    fi
}

check_health() {
    echo -e "${BLUE}Checking OpsSage backend health...${NC}"

    health=$(curl -s "$API_URL/api/v1/health" 2>/dev/null)

    if [ $? -eq 0 ]; then
        print_success "Backend is healthy"
        echo "$health" | jq -C '.' 2>/dev/null || echo "$health"
        return 0
    else
        print_error "Backend is not accessible at $API_URL"
        echo "Please ensure the OpsSage backend is running"
        return 1
    fi
    echo
}

show_usage() {
    echo "Usage: $0 [scenario|all|list|health]"
    echo
    echo "Commands:"
    echo "  1           Run Scenario 1: Pod CrashLoopBackOff"
    echo "  2           Run Scenario 2: Node CPU Exhaustion"
    echo "  3           Run Scenario 3: Cascading Auth Outage"
    echo "  all         Run all scenarios sequentially"
    echo "  list        List all incidents"
    echo "  health      Check backend health"
    echo
    echo "Environment Variables:"
    echo "  API_URL     OpsSage API URL (default: http://localhost:8000)"
    echo
    echo "Examples:"
    echo "  $0 1                    # Run scenario 1"
    echo "  $0 all                  # Run all scenarios"
    echo "  API_URL=http://prod:8000 $0 health"
    echo
}

main() {
    local command=${1:-help}

    case "$command" in
        1)
            check_health || exit 1
            test_scenario_1
            ;;
        2)
            check_health || exit 1
            test_scenario_2
            ;;
        3)
            check_health || exit 1
            test_scenario_3
            ;;
        all)
            check_health || exit 1
            test_scenario_1
            wait_with_countdown 5 "Waiting before next scenario"
            test_scenario_2
            wait_with_countdown 5 "Waiting before next scenario"
            test_scenario_3
            wait_with_countdown 3 "Processing incidents"
            show_incidents
            ;;
        list)
            show_incidents
            ;;
        health)
            check_health
            ;;
        help|--help|-h)
            show_usage
            ;;
        *)
            print_error "Unknown command: $command"
            echo
            show_usage
            exit 1
            ;;
    esac
}

# Check if jq is installed
if ! command -v jq &> /dev/null; then
    print_warning "jq is not installed. Output will not be formatted."
    print_warning "Install jq for better output: brew install jq"
    echo
fi

main "$@"
