from typing import Dict, Any, Callable, Awaitable
import asyncio
from ..core.rate_limiter import RateLimiter
from ..core.load_balancer import LoadBalancer
from ..config import Config

class RateLimitMiddleware:
    """Middleware that combines rate limiting and load balancing."""
    
    def __init__(self):
        self.rate_limiter = RateLimiter()
        self.load_balancer = LoadBalancer()
        self._setup_done = False
        
    async def setup(self):
        """Setup the middleware and start background tasks."""
        if not self._setup_done:
            # Start queue processing
            asyncio.create_task(self.load_balancer.process_queue(self._handle_queued_request))
            self._setup_done = True
            
    async def _handle_queued_request(self, request: Dict[str, Any]) -> Any:
        """Handle a request from the queue."""
        handler = request.pop("handler", None)
        if handler:
            return await handler(request)
        return None
        
    async def handle_request(
        self,
        request: Dict[str, Any],
        handler: Callable[[Dict[str, Any]], Awaitable[Any]],
        user_id: str,
        ip: str
    ) -> Any:
        """
        Handle an incoming request with rate limiting and load balancing.
        
        Args:
            request: The request to process
            handler: Async function to handle the request
            user_id: User identifier for rate limiting
            ip: IP address for rate limiting
            
        Returns:
            Response from the handler or error message
        """
        # Check rate limits first
        if not await self.rate_limiter.check_rate_limit(user_id, ip):
            remaining_tokens = await self.rate_limiter.get_remaining_tokens(user_id, ip)
            return {
                "error": "Rate limit exceeded",
                "remaining_tokens": remaining_tokens,
                "retry_after": Config.QUEUE_CONFIG["retry_delay"]
            }
            
        # Add handler to request for queue processing
        request["handler"] = handler
        
        # Handle through load balancer
        return await self.load_balancer.handle_request(request, self._handle_queued_request)
        
    async def get_system_status(self, user_id: str, ip: str) -> Dict[str, Any]:
        """Get current system status including rate limits and load."""
        return {
            "rate_limits": await self.rate_limiter.get_remaining_tokens(user_id, ip),
            "system_load": await self.load_balancer.system_load
        } 