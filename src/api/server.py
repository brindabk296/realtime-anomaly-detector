"""
FastAPI server with WebSocket support for real-time log streaming
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import asyncio
from loguru import logger

from src.ingestion.stream_processor import StreamProcessor
from src.ingestion.log_generator import LogGenerator

# Global instances
stream_processor = StreamProcessor()
log_generator = LogGenerator()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    logger.info("Starting Real-Time Anomaly Detection API...")
    
    # Start stream processor
    asyncio.create_task(stream_processor.start_processing())
    
    # Start demo log generator (for testing)
    asyncio.create_task(generate_demo_logs())
    
    yield
    
    # Shutdown
    logger.info("Shutting down...")
    stream_processor.stop()

async def generate_demo_logs():
    """Generate demo logs every 10 seconds for testing"""
    while True:
        # Generate batch of 10 logs with 10% anomaly rate
        batch = log_generator.generate_batch(10, anomaly_rate=0.1)
        for log in batch:
            await stream_processor.add_log(log)
        await asyncio.sleep(10)

# Create FastAPI app
app = FastAPI(
    title="Real-Time Log Anomaly Detection API",
    description="Stream logs and detect anomalies in real-time",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint - API health check"""
    return {
        "service": "Real-Time Log Anomaly Detection",
        "status": "running",
        "stream_active": stream_processor.is_running,
        "window_size": len(stream_processor.window),
        "active_connections": len(stream_processor.active_connections)
    }

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}

@app.get("/stats")
async def get_stats():
    """Get stream statistics"""
    return stream_processor.get_window_stats()

@app.get("/window")
async def get_window(limit: int = 50):
    """Get recent logs from window"""
    logs = list(stream_processor.window)[-limit:]
    return {"total": len(logs), "logs": logs}

@app.websocket("/ws/logs")
async def websocket_logs(websocket: WebSocket):
    """
    WebSocket endpoint for real-time log streaming
    Clients receive logs as they arrive
    """
    await websocket.accept()
    stream_processor.active_connections.append(websocket)
    logger.info(f"WebSocket client connected. Total: {len(stream_processor.active_connections)}")
    
    try:
        while True:
            # Keep connection alive with ping/pong
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
            elif data == "stats":
                await websocket.send_json(stream_processor.get_window_stats())
    except WebSocketDisconnect:
        stream_processor.active_connections.remove(websocket)
        logger.info(f"WebSocket client disconnected. Remaining: {len(stream_processor.active_connections)}")

