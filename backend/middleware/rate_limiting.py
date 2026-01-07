"""
Rate limiting middleware - simple per-IP rate limiting
"""
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from fastapi import status
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, Tuple
import time


class RateLimitingMiddleware(BaseHTTPMiddleware):
    """
    Simple per-IP rate limiting middleware
    
    Tracks requests per IP address with a sliding window approach.
    """
    
    def __init__(
        self,
        app,
        requests_per_minute: int = 60,
        requests_per_hour: int = 1000,
        requests_per_day: int = 10000
    ):
        """
        Initialize rate limiting middleware
        
        Args:
            app: FastAPI application
            requests_per_minute: Max requests per minute per IP
            requests_per_hour: Max requests per hour per IP
            requests_per_day: Max requests per day per IP
        """
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        self.requests_per_day = requests_per_day
        
        # Track requests: {ip: [(timestamp, ...), ...]}
        self.request_history: Dict[str, list] = defaultdict(list)
        
        # Clean up old entries periodically
        self.last_cleanup = time.time()
        self.cleanup_interval = 300  # 5 minutes
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP from request, handling proxies"""
        # Check for forwarded IP (from reverse proxy)
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            # X-Forwarded-For can contain multiple IPs, take the first one
            return forwarded.split(",")[0].strip()
        
        # Check for real IP header
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip.strip()
        
        # Fallback to direct client IP
        if request.client:
            return request.client.host
        
        return "unknown"
    
    def _cleanup_old_entries(self, current_time: float):
        """Remove request history older than 24 hours"""
        if current_time - self.last_cleanup < self.cleanup_interval:
            return
        
        cutoff_time = current_time - 86400  # 24 hours in seconds
        
        for ip in list(self.request_history.keys()):
            # Remove old timestamps
            self.request_history[ip] = [
                ts for ts in self.request_history[ip]
                if ts > cutoff_time
            ]
            # Remove IP if no recent requests
            if not self.request_history[ip]:
                del self.request_history[ip]
        
        self.last_cleanup = current_time
    
    def _check_rate_limit(self, ip: str, current_time: float) -> Tuple[bool, str]:
        """
        Check if IP has exceeded rate limits
        
        Returns:
            (allowed, message) - whether request is allowed and error message if not
        """
        # Get request timestamps for this IP
        timestamps = self.request_history[ip]
        
        # Check per-minute limit
        minute_ago = current_time - 60
        recent_minute = [ts for ts in timestamps if ts > minute_ago]
        if len(recent_minute) >= self.requests_per_minute:
            return False, "Rate limit exceeded: too many requests per minute"
        
        # Check per-hour limit
        hour_ago = current_time - 3600
        recent_hour = [ts for ts in timestamps if ts > hour_ago]
        if len(recent_hour) >= self.requests_per_hour:
            return False, "Rate limit exceeded: too many requests per hour"
        
        # Check per-day limit
        day_ago = current_time - 86400
        recent_day = [ts for ts in timestamps if ts > day_ago]
        if len(recent_day) >= self.requests_per_day:
            return False, "Rate limit exceeded: too many requests per day"
        
        # All checks passed
        return True, ""
    
    async def dispatch(self, request: Request, call_next):
        """Process request with rate limiting"""
        # Skip rate limiting for health checks, static endpoints, and CORS preflight requests
        if request.url.path in ["/", "/health", "/version"]:
            return await call_next(request)
        
        # Skip rate limiting for OPTIONS requests (CORS preflight)
        if request.method == "OPTIONS":
            return await call_next(request)
        
        # Get client IP
        client_ip = self._get_client_ip(request)
        
        # Cleanup old entries periodically
        current_time = time.time()
        self._cleanup_old_entries(current_time)
        
        # Check rate limits
        allowed, error_msg = self._check_rate_limit(client_ip, current_time)
        
        if not allowed:
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "success": False,
                    "message": error_msg,
                    "error": "Please try again later"
                }
            )
        
        # Record this request
        self.request_history[client_ip].append(current_time)
        
        # Process request
        response = await call_next(request)
        return response






