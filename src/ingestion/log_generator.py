"""
Log generator for testing and demo purposes
Creates realistic logs with controlled anomalies
"""

import random
import datetime
import uuid
from typing import List, Dict, Any

class LogGenerator:
    def __init__(self):
        self.services = ['auth-service', 'payment-api', 'user-db', 'frontend', 
                        'recommendation-engine', 'search-service', 'notification-service']
        self.users = [f'user_{i}' for i in range(1, 101)]
        self.regions = ['us-east-1', 'eu-west-1', 'ap-south-1', 'sa-east-1']
        
    def generate_normal_log(self) -> Dict[str, Any]:
        """Generate a normal (non-anomalous) log"""
        return {
            'log_id': str(uuid.uuid4())[:8],
            'timestamp': datetime.datetime.now().isoformat(),
            'service': random.choice(self.services),
            'user': random.choice(self.users),
            'region': random.choice(self.regions),
            'status_code': 200,
            'latency_ms': random.randint(50, 300),
            'message': 'Request processed successfully',
            'is_anomaly': 0
        }
    
    def generate_anomaly_log(self, anomaly_type: str = None) -> Dict[str, Any]:
        """Generate an anomalous log entry"""
        if anomaly_type is None:
            anomaly_type = random.choice(['latency_spike', 'error_flood', 'auth_failure', 'timeout'])
        
        log = {
            'log_id': str(uuid.uuid4())[:8],
            'timestamp': datetime.datetime.now().isoformat(),
            'service': random.choice(self.services),
            'user': random.choice(self.users),
            'region': random.choice(self.regions),
            'is_anomaly': 1
        }
        
        if anomaly_type == 'latency_spike':
            log['status_code'] = 200
            log['latency_ms'] = random.randint(3000, 10000)
            log['message'] = '⚠️ CRITICAL: Severe latency detected - Response time exceeded threshold'
            
        elif anomaly_type == 'error_flood':
            log['status_code'] = random.choice([500, 502, 503, 504])
            log['latency_ms'] = random.randint(100, 500)
            log['message'] = '❌ ERROR: Database connection pool exhausted - Multiple connection failures'
            
        elif anomaly_type == 'auth_failure':
            log['status_code'] = 401
            log['latency_ms'] = random.randint(20, 100)
            log['message'] = '🔐 SECURITY ALERT: Multiple failed login attempts from unknown IP'
            
        else:  # timeout
            log['status_code'] = 504
            log['latency_ms'] = random.randint(30000, 60000)
            log['message'] = '⏰ TIMEOUT: Request timed out after 30 seconds'
        
        return log
    
    def generate_batch(self, total: int = 100, anomaly_rate: float = 0.1) -> List[Dict]:
        """Generate a batch of logs with specified anomaly rate"""
        logs = []
        for _ in range(total):
            if random.random() < anomaly_rate:
                logs.append(self.generate_anomaly_log())
            else:
                logs.append(self.generate_normal_log())
        return logs
    
    def generate_stream(self, num_logs: int = 1000, anomaly_rate: float = 0.05):
        """Generator for streaming logs"""
        for _ in range(num_logs):
            if random.random() < anomaly_rate:
                yield self.generate_anomaly_log()
            else:
                yield self.generate_normal_log()


# Test
if __name__ == "__main__":
    gen = LogGenerator()
    batch = gen.generate_batch(20, anomaly_rate=0.2)
    
    print("Sample Logs:")
    print("-" * 60)
    for log in batch[:5]:
        status = "🚨 ANOMALY" if log['is_anomaly'] else "✅ Normal"
        print(f"{status} | {log['service']} | {log['latency_ms']}ms | {log['message'][:50]}")