"""
Real-time stream processor with WebSocket support
"""

import asyncio
import json
from datetime import datetime
from typing import List, Dict, Any
from collections import deque
from loguru import logger

class StreamProcessor:
    """Manages real-time log streaming and WebSocket connections"""
    
    def __init__(self, window_size: int = 1000):
        self.window = deque(maxlen=window_size)
        self.active_connections = []
        self.processing_queue = asyncio.Queue()
        self.is_running = False
        self._background_task = None
    
    async def add_log(self, log: Dict[str, Any]):
        """Add a log to the processing pipeline"""
        if 'timestamp' not in log:
            log['timestamp'] = datetime.now().isoformat()
        
        self.window.append(log)
        await self.processing_queue.put(log)
        await self.broadcast(log)
        
        logger.debug(f"Log added: {log.get('service', 'unknown')}")
    
    async def broadcast(self, log: Dict[str, Any]):
        """Send log to all connected WebSocket clients"""
        for connection in self.active_connections[:]:
            try:
                await connection.send_json(log)
            except Exception as e:
                logger.error(f"Broadcast failed: {e}")
                self.active_connections.remove(connection)
    
    async def start_processing(self):
        """Start background processing of logs"""
        self.is_running = True
        
        async def process_loop():
            while self.is_running:
                try:
                    log = await asyncio.wait_for(self.processing_queue.get(), timeout=1.0)
                    # Extract basic features for immediate use
                    features = self.extract_basic_features(log)
                    log['_features'] = features
                except asyncio.TimeoutError:
                    continue
                except Exception as e:
                    logger.error(f"Processing error: {e}")
        
        self._background_task = asyncio.create_task(process_loop())
        logger.info("Stream processor started")
    
    def extract_basic_features(self, log: Dict[str, Any]) -> List[float]:
        """Extract basic features for real-time analysis"""
        try:
            ts = datetime.fromisoformat(log.get('timestamp', datetime.now().isoformat()))
        except:
            ts = datetime.now()
        
        return [
            log.get('latency_ms', 0) / 5000,
            1 if log.get('status_code', 200) >= 400 else 0,
            len(log.get('message', '')) / 500,
            ts.hour / 24,
            ts.minute / 60,
        ]
    
    def get_window_stats(self) -> Dict[str, Any]:
        """Get statistics about current window"""
        if not self.window:
            return {'total': 0, 'services': {}, 'avg_latency': 0}
        
        services = {}
        total_latency = 0
        
        for log in self.window:
            service = log.get('service', 'unknown')
            services[service] = services.get(service, 0) + 1
            total_latency += log.get('latency_ms', 0)
        
        return {
            'total': len(self.window),
            'services': services,
            'avg_latency': total_latency / len(self.window) if self.window else 0
        }
    
    def stop(self):
        """Stop the processor"""
        self.is_running = False
        if self._background_task:
            self._background_task.cancel()