"""
Size limiting middleware - enforce request size limits
"""
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from fastapi import status
import json


class SizeLimitingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to enforce request size limits
    
    Limits:
    - General request body: 1MB (default)
    - Resume uploads: 10MB (via endpoint-specific validation)
    """
    
    def __init__(
        self,
        app,
        max_request_size: int = 1024 * 1024,  # 1MB default
        max_upload_size: int = 10 * 1024 * 1024  # 10MB for file uploads
    ):
        """
        Initialize size limiting middleware
        
        Args:
            app: FastAPI application
            max_request_size: Maximum request body size in bytes (default 1MB)
            max_upload_size: Maximum file upload size in bytes (default 10MB)
        """
        super().__init__(app)
        self.max_request_size = max_request_size
        self.max_upload_size = max_upload_size
    
    async def dispatch(self, request: Request, call_next):
        """Process request with size limiting"""
        # Check Content-Length header if present
        content_length = request.headers.get("Content-Length")
        if content_length:
            try:
                size = int(content_length)
                # Determine max size based on endpoint
                is_upload_endpoint = "/resume/analyze" in request.url.path
                max_size = self.max_upload_size if is_upload_endpoint else self.max_request_size
                
                if size > max_size:
                    return JSONResponse(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        content={
                            "success": False,
                            "message": f"Request too large. Maximum size: {max_size // (1024 * 1024)}MB",
                            "error": "Request size exceeds allowed limit"
                        }
                    )
            except ValueError:
                # Invalid Content-Length, let it through but will be caught later
                pass
        
        # Process request
        response = await call_next(request)
        return response





