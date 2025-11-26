#!/usr/bin/env python3
"""
Mock services for testing OpsSage without real infrastructure.
Provides mock metrics, logs, and events APIs.
"""

import os
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

SERVICE_TYPE = os.getenv("SERVICE_TYPE", "metrics")

app = FastAPI(title=f"Mock {SERVICE_TYPE.capitalize()} Service")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Mock Metrics Service
@app.get("/metrics/query")
async def query_metrics(
    metric: str = Query(...),
    start_time: str = Query(None),
    end_time: str = Query(None),
    step: str = Query("1m"),
) -> Dict[str, Any]:
    """Mock Prometheus-style metrics query."""

    # Generate random time series data
    now = datetime.now()
    start = now - timedelta(hours=1)

    timestamps = []
    values = []

    current = start
    base_value = random.uniform(50, 90)

    while current <= now:
        timestamps.append(int(current.timestamp()))
        # Add some variation
        value = base_value + random.uniform(-10, 10)
        values.append(round(value, 2))
        current += timedelta(minutes=1)

    return {
        "status": "success",
        "data": {
            "resultType": "matrix",
            "result": [
                {
                    "metric": {"__name__": metric, "job": "mock"},
                    "values": [[ts, str(val)] for ts, val in zip(timestamps, values)],
                }
            ],
        },
    }


@app.get("/metrics/instant")
async def instant_metrics(metric: str = Query(...)) -> Dict[str, Any]:
    """Mock instant metric query."""
    value = random.uniform(50, 95)

    return {
        "status": "success",
        "data": {
            "resultType": "vector",
            "result": [
                {
                    "metric": {"__name__": metric, "job": "mock"},
                    "value": [int(datetime.now().timestamp()), str(round(value, 2))],
                }
            ],
        },
    }


# Mock Logs Service
@app.get("/logs/query")
async def query_logs(
    query: str = Query(...),
    start_time: str = Query(None),
    end_time: str = Query(None),
    limit: int = Query(100),
) -> Dict[str, Any]:
    """Mock Loki-style logs query."""

    log_levels = ["INFO", "WARN", "ERROR", "DEBUG"]
    services = ["api-server", "worker", "database", "cache"]

    logs = []
    now = datetime.now()

    for i in range(min(limit, 50)):
        timestamp = now - timedelta(minutes=i)
        level = random.choice(log_levels)
        service = random.choice(services)

        messages = {
            "ERROR": [
                "Connection timeout to database",
                "Failed to process request",
                "Memory allocation failed",
                "Unexpected null pointer",
            ],
            "WARN": [
                "High memory usage detected",
                "Slow query detected",
                "Connection pool near capacity",
                "Cache miss rate high",
            ],
            "INFO": [
                "Request processed successfully",
                "Connection established",
                "Cache updated",
                "Health check passed",
            ],
        }

        message = random.choice(messages.get(level, messages["INFO"]))

        logs.append({
            "timestamp": timestamp.isoformat(),
            "level": level,
            "service": service,
            "message": message,
            "labels": {
                "service": service,
                "level": level,
                "namespace": "production",
            },
        })

    return {
        "status": "success",
        "data": {
            "result": logs,
            "stats": {
                "summary": {
                    "bytesProcessed": len(logs) * 100,
                    "linesProcessed": len(logs),
                    "execTime": 0.05,
                }
            },
        },
    }


# Mock Events Service
@app.get("/events")
async def query_events(
    namespace: str = Query(None),
    kind: str = Query(None),
    start_time: str = Query(None),
    end_time: str = Query(None),
) -> Dict[str, Any]:
    """Mock Kubernetes events query."""

    event_types = ["Normal", "Warning"]
    reasons = [
        "Created",
        "Started",
        "Pulled",
        "Scheduled",
        "FailedScheduling",
        "BackOff",
        "Unhealthy",
    ]

    events = []
    now = datetime.now()

    for i in range(20):
        timestamp = now - timedelta(minutes=i * 5)
        event_type = random.choice(event_types)
        reason = random.choice(reasons)

        events.append({
            "type": event_type,
            "reason": reason,
            "message": f"Event: {reason} at {timestamp.strftime('%H:%M:%S')}",
            "firstTimestamp": timestamp.isoformat(),
            "lastTimestamp": timestamp.isoformat(),
            "count": random.randint(1, 5),
            "involvedObject": {
                "kind": kind or "Pod",
                "namespace": namespace or "production",
                "name": f"pod-{random.randint(1000, 9999)}",
            },
        })

    return {
        "items": events,
        "metadata": {
            "continue": "",
            "resourceVersion": "12345",
        },
    }


@app.get("/health")
async def health() -> Dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy", "service": SERVICE_TYPE}


@app.get("/")
async def root() -> Dict[str, str]:
    """Root endpoint."""
    return {
        "service": f"Mock {SERVICE_TYPE.capitalize()} Service",
        "status": "running",
        "endpoints": {
            "metrics": "/metrics/query, /metrics/instant",
            "logs": "/logs/query",
            "events": "/events",
        }[SERVICE_TYPE] if SERVICE_TYPE in ["metrics", "logs", "events"] else "/metrics/query",
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
