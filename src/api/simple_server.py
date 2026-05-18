"""
Simplified FastAPI server - works with Python 3.13
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import random
import uuid
from datetime import datetime
from typing import List, Dict, Any
from contextlib import asynccontextmanager

# Global storage
logs = []
services = ['auth-service', 'payment-api', 'user-db', 'frontend', 'recommendation-engine']

def generate_log() -> Dict[str, Any]:
    """Generate a single log entry"""
    is_anomaly = random.random() < 0.1
    
    return {
        'log_id': str(uuid.uuid4())[:8],
        'timestamp': datetime.now().isoformat(),
        'service': random.choice(services),
        'status_code': random.choice([200, 200, 200, 400, 401, 500]) if not is_anomaly else random.choice([401, 500, 503]),
        'latency_ms': random.randint(50, 300) if not is_anomaly else random.randint(1000, 5000),
        'message': 'Request processed successfully' if not is_anomaly else 'ERROR: Anomaly detected - unusual pattern',
        'user': f'user_{random.randint(1, 100)}',
        'is_anomaly': 1 if is_anomaly else 0
    }

async def generate_logs_periodically():
    """Background task to generate logs every 5 seconds"""
    while True:
        # Generate 5-10 logs per batch
        batch_size = random.randint(5, 15)
        for _ in range(batch_size):
            log = generate_log()
            logs.append(log)
            # Keep only last 1000 logs
            if len(logs) > 1000:
                logs.pop(0)
        await asyncio.sleep(5)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    asyncio.create_task(generate_logs_periodically())
    yield
    # Shutdown
    print("Shutting down...")

# Create app
app = FastAPI(
    title="Log Anomaly Detection API",
    description="Real-time log streaming API",
    lifespan=lifespan
)

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "service": "Log Anomaly Detection",
        "status": "running",
        "total_logs": len(logs)
    }

@app.get("/logs")
async def get_logs(limit: int = 100):
    """Get recent logs"""
    return {
        "total": len(logs),
        "logs": logs[-limit:]
    }

@app.get("/stats")
async def get_stats():
    """Get statistics"""
    if not logs:
        return {"total": 0, "anomaly_count": 0, "services": {}}
    
    anomaly_count = sum(1 for l in logs if l.get('is_anomaly', 0) == 1)
    services_count = {}
    for l in logs:
        service = l.get('service', 'unknown')
        services_count[service] = services_count.get(service, 0) + 1
    
    return {
        "total": len(logs),
        "anomaly_count": anomaly_count,
        "anomaly_rate": round(anomaly_count / len(logs) * 100, 2),
        "services": services_count
    }