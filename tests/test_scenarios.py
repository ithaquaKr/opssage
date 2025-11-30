"""
Kubernetes Incident Simulation Scenarios for Multi-Agent System Testing.

These scenarios are designed to test the complete MAS pipeline:
- AICA (Alert Ingestion & Context Agent)
- KREA (Knowledge Retrieval & Enrichment Agent)
- RCARA (Root Cause Analysis & Remediation Agent)
"""

from datetime import datetime

TEST_SCENARIOS = {
    "scenarios": [
        {
            "id": "scenario_1",
            "name": "Pod CrashLoopBackOff - Misconfigured Environment Variable",
            "description": "A single microservice pod enters CrashLoopBackOff due to a misconfigured environment variable",
            "alerts": [
                {
                    "fingerprint": "a1b2c3d4e5f6",
                    "status": "firing",
                    "labels": {
                        "alertname": "KubePodCrashLooping",
                        "namespace": "production",
                        "pod": "payment-service-7d9f8b6c5-xk4nm",
                        "container": "payment-service",
                        "severity": "critical",
                        "service": "payment-service",
                    },
                    "annotations": {
                        "summary": "Pod payment-service-7d9f8b6c5-xk4nm in production namespace is crash looping",
                        "description": "Pod payment-service-7d9f8b6c5-xk4nm has restarted 15 times in the last 10 minutes",
                        "runbook_url": "https://runbooks.example.com/KubePodCrashLooping",
                    },
                    "startsAt": "2025-11-29T10:15:00Z",
                    "endsAt": "0001-01-01T00:00:00Z",
                    "generatorURL": "http://prometheus:9090/graph?g0.expr=rate%28kube_pod_container_status_restarts_total%5B5m%5D%29+%3E+0",
                }
            ],
            "logs": [
                "2025-11-29T10:15:12Z payment-service-7d9f8b6c5-xk4nm payment-service ERROR Failed to parse configuration: invalid value for key 'DATABASE_URL'",
                "2025-11-29T10:15:12Z payment-service-7d9f8b6c5-xk4nm payment-service ERROR Configuration validation failed: DATABASE_URL must be a valid PostgreSQL connection string",
                "2025-11-29T10:15:12Z payment-service-7d9f8b6c5-xk4nm payment-service FATAL Application startup failed, exiting with code 1",
                "2025-11-29T10:15:45Z payment-service-7d9f8b6c5-xk4nm payment-service INFO Starting payment-service v2.4.1",
                "2025-11-29T10:15:45Z payment-service-7d9f8b6c5-xk4nm payment-service ERROR Failed to parse configuration: invalid value for key 'DATABASE_URL'",
                "2025-11-29T10:15:45Z payment-service-7d9f8b6c5-xk4nm payment-service FATAL Application startup failed, exiting with code 1",
            ],
            "metrics": {
                "kube_pod_container_status_restarts_total": 15,
                "kube_pod_status_phase": 0,
                "container_cpu_usage_seconds_total": 0.02,
                "container_memory_usage_bytes": 45678912,
                "kube_pod_container_status_waiting": 1,
                "kube_pod_container_status_ready": 0,
            },
            "dependencies": {
                "payment-service": {
                    "depends_on": ["postgres-db"],
                    "failure_propagation": [],
                }
            },
            "expected_root_cause": "Misconfigured environment variable DATABASE_URL in the pod deployment configuration",
            "expected_suggestions": [
                "Validate the DATABASE_URL environment variable in the deployment manifest",
                "Check the ConfigMap or Secret referenced by the deployment for correct database connection string format",
                "Redeploy the pod with corrected environment variable configuration",
            ],
            "complexity_level": 1,
        },
        {
            "id": "scenario_2",
            "name": "Node CPU Exhaustion - Resource Saturation",
            "description": "A Kubernetes node experiences CPU saturation, causing pod throttling and degraded service performance",
            "alerts": [
                {
                    "fingerprint": "x7y8z9w0v1u2",
                    "status": "firing",
                    "labels": {
                        "alertname": "NodeHighCpuUsage",
                        "node": "worker-node-03",
                        "severity": "warning",
                        "cluster": "prod-us-east-1",
                    },
                    "annotations": {
                        "summary": "Node worker-node-03 CPU usage is critically high",
                        "description": "CPU usage on worker-node-03 has been above 95% for 10 minutes",
                        "runbook_url": "https://runbooks.example.com/NodeHighCpuUsage",
                    },
                    "startsAt": "2025-11-29T11:20:00Z",
                    "endsAt": "0001-01-01T00:00:00Z",
                    "generatorURL": "http://prometheus:9090/graph?g0.expr=node_cpu_usage+%3E+0.95",
                },
                {
                    "fingerprint": "a2b3c4d5e6f7",
                    "status": "firing",
                    "labels": {
                        "alertname": "KubeNodeNotReady",
                        "node": "worker-node-03",
                        "severity": "critical",
                        "cluster": "prod-us-east-1",
                    },
                    "annotations": {
                        "summary": "Node worker-node-03 is intermittently not ready",
                        "description": "Node worker-node-03 status has been NotReady 3 times in the last 15 minutes",
                        "runbook_url": "https://runbooks.example.com/KubeNodeNotReady",
                    },
                    "startsAt": "2025-11-29T11:25:00Z",
                    "endsAt": "0001-01-01T00:00:00Z",
                    "generatorURL": "http://prometheus:9090/graph?g0.expr=kube_node_status_condition",
                },
                {
                    "fingerprint": "m8n9o0p1q2r3",
                    "status": "firing",
                    "labels": {
                        "alertname": "PodCpuThrottlingHigh",
                        "namespace": "production",
                        "pod": "analytics-worker-5c8d9e7f6-hg3km",
                        "node": "worker-node-03",
                        "severity": "warning",
                    },
                    "annotations": {
                        "summary": "Pod analytics-worker-5c8d9e7f6-hg3km is experiencing high CPU throttling",
                        "description": "Pod has been throttled for 65% of the time over the last 5 minutes",
                        "runbook_url": "https://runbooks.example.com/PodCpuThrottlingHigh",
                    },
                    "startsAt": "2025-11-29T11:22:00Z",
                    "endsAt": "0001-01-01T00:00:00Z",
                    "generatorURL": "http://prometheus:9090/graph?g0.expr=rate%28container_cpu_cfs_throttled_seconds_total%5B5m%5D%29+%3E+0.5",
                },
            ],
            "logs": [
                "2025-11-29T11:20:15Z worker-node-03 kubelet WARNING CPU usage exceeded 95% threshold",
                "2025-11-29T11:21:32Z worker-node-03 kernel WARNING CPU throttling detected on cgroup /kubepods/burstable/analytics-worker",
                "2025-11-29T11:22:05Z analytics-worker-5c8d9e7f6-hg3km analytics-worker WARNING Request processing latency increased to 2500ms (normal: 150ms)",
                "2025-11-29T11:22:47Z analytics-worker-5c8d9e7f6-hg3km analytics-worker ERROR Task queue backlog increased to 1234 items (threshold: 100)",
                "2025-11-29T11:23:15Z worker-node-03 kubelet ERROR Failed to update node status: context deadline exceeded",
                "2025-11-29T11:24:02Z worker-node-03 kubelet WARNING Node memory pressure detected due to CPU saturation affecting process scheduling",
                "2025-11-29T11:25:18Z worker-node-03 kubelet ERROR NodeNotReady: node worker-node-03 status changed to NotReady",
                "2025-11-29T11:26:30Z analytics-worker-5c8d9e7f6-hg3km analytics-worker WARNING CPU throttle rate: 0.65 (65% of time throttled)",
            ],
            "metrics": {
                "node_cpu_usage": 0.97,
                "node_cpu_seconds_total": 145823.45,
                "node_memory_usage_bytes": 15728640000,
                "node_load1": 24.5,
                "node_load5": 18.2,
                "node_load15": 12.8,
                "container_cpu_cfs_throttled_seconds_total": 892.34,
                "container_cpu_usage_seconds_total": 1245.67,
                "kube_pod_container_resource_limits_cpu_cores": 2.0,
                "kube_pod_container_resource_requests_cpu_cores": 1.5,
                "kube_node_status_condition": 0,
            },
            "dependencies": {
                "analytics-worker": {
                    "depends_on": ["kafka-cluster", "redis-cache"],
                    "failure_propagation": ["degraded_performance"],
                },
                "other-pods-on-node": {
                    "depends_on": ["worker-node-03"],
                    "failure_propagation": ["latency_increase", "intermittent_failures"],
                },
            },
            "expected_root_cause": "CPU resource exhaustion on worker-node-03 due to analytics-worker pod consuming resources without proper limits, causing node-level performance degradation and pod throttling",
            "expected_suggestions": [
                "Adjust CPU resource requests and limits for analytics-worker pod to prevent resource exhaustion",
                "Enable or tune Horizontal Pod Autoscaler (HPA) for analytics-worker deployment to distribute load across multiple pods",
                "Scale the node pool to add additional worker nodes and redistribute pod workloads",
                "Investigate analytics-worker workload patterns and optimize resource-intensive operations",
            ],
            "complexity_level": 2,
        },
        {
            "id": "scenario_3",
            "name": "Multi-Service Dependency Failure - Cascading Authentication Service Outage",
            "description": "Authentication Service failure propagates to dependent services (Order Service, Payment Service), producing cascading errors",
            "alerts": [
                {
                    "fingerprint": "k4l5m6n7o8p9",
                    "status": "firing",
                    "labels": {
                        "alertname": "ServiceDown",
                        "namespace": "production",
                        "service": "auth-service",
                        "severity": "critical",
                    },
                    "annotations": {
                        "summary": "Auth Service is down",
                        "description": "Auth Service has failed health checks for 5 consecutive minutes",
                        "runbook_url": "https://runbooks.example.com/ServiceDown",
                    },
                    "startsAt": "2025-11-29T14:10:00Z",
                    "endsAt": "0001-01-01T00:00:00Z",
                    "generatorURL": "http://prometheus:9090/graph?g0.expr=up%7Bservice%3D%22auth-service%22%7D+%3D%3D+0",
                },
                {
                    "fingerprint": "q9r0s1t2u3v4",
                    "status": "firing",
                    "labels": {
                        "alertname": "ServiceErrorRateHigh",
                        "namespace": "production",
                        "service": "auth-service",
                        "severity": "critical",
                    },
                    "annotations": {
                        "summary": "Auth Service error rate is critically high",
                        "description": "Error rate for auth-service is 98% over the last 5 minutes",
                        "runbook_url": "https://runbooks.example.com/ServiceErrorRateHigh",
                    },
                    "startsAt": "2025-11-29T14:08:00Z",
                    "endsAt": "0001-01-01T00:00:00Z",
                    "generatorURL": "http://prometheus:9090/graph?g0.expr=rate%28http_requests_total%7Bstatus%3D~%225..%22%7D%5B5m%5D%29",
                },
                {
                    "fingerprint": "w5x6y7z8a9b0",
                    "status": "firing",
                    "labels": {
                        "alertname": "HTTP500RateIncrease",
                        "namespace": "production",
                        "service": "order-service",
                        "severity": "warning",
                    },
                    "annotations": {
                        "summary": "Order Service experiencing high 500 error rate",
                        "description": "HTTP 500 errors increased by 450% in order-service",
                        "runbook_url": "https://runbooks.example.com/HTTP500RateIncrease",
                    },
                    "startsAt": "2025-11-29T14:11:00Z",
                    "endsAt": "0001-01-01T00:00:00Z",
                    "generatorURL": "http://prometheus:9090/graph?g0.expr=rate%28http_requests_total%7Bstatus%3D%22500%22%7D%5B5m%5D%29",
                },
                {
                    "fingerprint": "c1d2e3f4g5h6",
                    "status": "firing",
                    "labels": {
                        "alertname": "DependencyRequestFailure",
                        "namespace": "production",
                        "service": "payment-service",
                        "dependency": "auth-service",
                        "severity": "critical",
                    },
                    "annotations": {
                        "summary": "Payment Service cannot reach auth-service dependency",
                        "description": "95% of requests from payment-service to auth-service are failing",
                        "runbook_url": "https://runbooks.example.com/DependencyRequestFailure",
                    },
                    "startsAt": "2025-11-29T14:10:30Z",
                    "endsAt": "0001-01-01T00:00:00Z",
                    "generatorURL": "http://prometheus:9090/graph?g0.expr=dependency_request_success_rate",
                },
            ],
            "logs": [
                "2025-11-29T14:07:45Z auth-service-6f8a9b7c5-kl2mn auth-service ERROR JWT signing key rotation failed: invalid key format in secrets/jwt-signing-key",
                "2025-11-29T14:07:46Z auth-service-6f8a9b7c5-kl2mn auth-service FATAL Unable to initialize token validator: RSA key parse error",
                "2025-11-29T14:08:12Z auth-service-6f8a9b7c5-kl2mn auth-service ERROR Failed to verify token signature: crypto/rsa: invalid key",
                "2025-11-29T14:08:15Z auth-service-6f8a9b7c5-kl2mn auth-service ERROR Authentication backend connection pool exhausted",
                "2025-11-29T14:10:23Z order-service-8c9d0e1f2-pq3rs order-service ERROR Failed to validate auth token: upstream service auth-service returned 500",
                "2025-11-29T14:10:24Z order-service-8c9d0e1f2-pq3rs order-service WARNING Auth validation timeout after 5000ms (threshold: 1000ms)",
                "2025-11-29T14:10:25Z order-service-8c9d0e1f2-pq3rs order-service ERROR Request processing failed: authentication required but auth service unavailable",
                "2025-11-29T14:10:35Z payment-service-3g4h5i6j7-tu8vw payment-service ERROR Dependency check failed: auth-service health check returned 503",
                "2025-11-29T14:10:36Z payment-service-3g4h5i6j7-tu8vw payment-service ERROR Circuit breaker opened for auth-service after 20 consecutive failures",
                "2025-11-29T14:11:02Z payment-service-3g4h5i6j7-tu8vw payment-service ERROR Payment authorization failed: upstream dependency error from auth-service",
                "2025-11-29T14:11:15Z order-service-8c9d0e1f2-pq3rs order-service ERROR Database transaction rolled back: authentication failure prevented order creation",
                "2025-11-29T14:12:00Z auth-service-6f8a9b7c5-kl2mn auth-service ERROR Health check failed: token validation subsystem not operational",
            ],
            "metrics": {
                "http_requests_total_auth_service": 12450,
                "http_requests_errors_auth_service": 12201,
                "http_500_rate_auth_service": 0.98,
                "http_500_rate_order_service": 0.42,
                "http_500_rate_payment_service": 0.38,
                "service_up_auth_service": 0,
                "service_up_order_service": 1,
                "service_up_payment_service": 1,
                "request_latency_seconds_auth_service_p99": 8.5,
                "request_latency_seconds_order_service_p99": 5.2,
                "request_latency_seconds_payment_service_p99": 4.8,
                "dependency_request_success_rate_order_to_auth": 0.05,
                "dependency_request_success_rate_payment_to_auth": 0.03,
                "circuit_breaker_open_payment_auth": 1,
            },
            "dependencies": {
                "auth-service": {
                    "depends_on": ["postgres-db", "redis-cache", "secrets-manager"],
                    "failure_propagation": ["order-service", "payment-service", "user-service"],
                },
                "order-service": {
                    "depends_on": ["auth-service", "inventory-service", "postgres-db"],
                    "failure_propagation": ["frontend-api"],
                },
                "payment-service": {
                    "depends_on": ["auth-service", "stripe-gateway", "postgres-db"],
                    "failure_propagation": ["order-service", "frontend-api"],
                },
            },
            "expected_root_cause": "Configuration regression in auth-service JWT signing key after recent deployment, causing token signature validation failures and cascading authentication errors across dependent services",
            "expected_suggestions": [
                "Roll back auth-service to previous stable version (before JWT key rotation change)",
                "Apply circuit breaker pattern to prevent cascading failures when auth-service is degraded",
                "Improve release validation process with pre-deployment health checks for critical configuration changes",
                "Implement graceful degradation in dependent services to handle auth-service outages",
                "Add monitoring and alerting for JWT key rotation and validation subsystem health",
            ],
            "complexity_level": 3,
        },
    ]
}
