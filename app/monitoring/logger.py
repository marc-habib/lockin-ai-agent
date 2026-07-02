"""
Request logger for LockIn AI.

Logs all requests to JSONL for monitoring and analysis.
"""

import json
from pathlib import Path
from datetime import datetime
from app.schemas.monitoring import RequestLog
from app.config import settings


class RequestLogger:
    """Logger for request monitoring."""
    
    def __init__(self, log_file: str = "logs/runs.jsonl"):
        """
        Initialize request logger.
        
        Args:
            log_file: Path to JSONL log file
        """
        self.log_file = Path(log_file)
        self._ensure_log_directory()
    
    def _ensure_log_directory(self) -> None:
        """Create log directory if it doesn't exist."""
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
    
    def log(self, request_log: RequestLog) -> None:
        """
        Log a request to JSONL.
        
        Args:
            request_log: Request log entry
        """
        # Convert to dict and then to JSON
        log_dict = request_log.model_dump()
        
        # Convert datetime to ISO format
        if isinstance(log_dict.get('timestamp'), datetime):
            log_dict['timestamp'] = log_dict['timestamp'].isoformat()
        
        # Append to JSONL file
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_dict) + '\n')
    
    def get_recent_logs(self, limit: int = 100) -> list[dict]:
        """
        Get recent log entries.
        
        Args:
            limit: Maximum number of entries to return
        
        Returns:
            List of log dicts
        """
        if not self.log_file.exists():
            return []
        
        logs = []
        
        with open(self.log_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    try:
                        logs.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
        
        # Return most recent entries
        return logs[-limit:]
    
    def get_logs_by_user(self, user_id: str, limit: int = 50) -> list[dict]:
        """
        Get logs for a specific user.
        
        Args:
            user_id: User identifier
            limit: Maximum number of entries to return
        
        Returns:
            List of log dicts for the user
        """
        if not self.log_file.exists():
            return []
        
        user_logs = []
        
        with open(self.log_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    try:
                        log = json.loads(line)
                        if log.get('user_id') == user_id:
                            user_logs.append(log)
                    except json.JSONDecodeError:
                        continue
        
        # Return most recent entries
        return user_logs[-limit:]
    
    def get_statistics(self) -> dict:
        """
        Get aggregate statistics from logs.
        
        Returns:
            Dict with statistics
        """
        if not self.log_file.exists():
            return {
                'total_requests': 0,
                'avg_latency_ms': 0,
                'success_rate': 0,
                'total_cost_usd': 0
            }
        
        total_requests = 0
        total_latency = 0
        successful_requests = 0
        total_cost = 0.0
        
        with open(self.log_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    try:
                        log = json.loads(line)
                        total_requests += 1
                        total_latency += log.get('latency_ms', 0)
                        
                        if log.get('status') == 'success':
                            successful_requests += 1
                        
                        if log.get('estimated_cost_usd'):
                            total_cost += log['estimated_cost_usd']
                    
                    except json.JSONDecodeError:
                        continue
        
        return {
            'total_requests': total_requests,
            'avg_latency_ms': round(total_latency / total_requests, 1) if total_requests > 0 else 0,
            'success_rate': round(successful_requests / total_requests * 100, 1) if total_requests > 0 else 0,
            'total_cost_usd': round(total_cost, 4)
        }


# Global logger instance
request_logger = RequestLogger()
