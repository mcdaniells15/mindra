import asyncio
from typing import Dict, Any, Optional, Callable, Awaitable
from collections import deque
from datetime import datetime
import time
from ..config import Config

class RequestQueue:
    """Manages request queuing and processing."""
    
    def __init__(self):
        self.queue = asyncio.Queue(maxsize=Config.QUEUE_CONFIG["max_queue_size"])
        self.in_flight_requests = 0
        self._lock = asyncio.Lock()
        
    async def add_request(self, request: Dict[str, Any]) -> bool:
        """Add request to queue. Returns False if queue is full."""
        try:
            await asyncio.wait_for(
                self.queue.put(request),
                timeout=Config.QUEUE_CONFIG["queue_timeout"]
            )
            return True
        except asyncio.TimeoutError:
            return False
            
    async def get_request(self) -> Optional[Dict[str, Any]]:
        """Get next request from queue."""
        try:
            request = await self.queue.get()
            async with self._lock:
                self.in_flight_requests += 1
            return request
        except asyncio.QueueEmpty:
            return None
            
    async def complete_request(self):
        """Mark a request as completed."""
        async with self._lock:
            self.in_flight_requests -= 1
            
    @property
    async def queue_size(self) -> int:
        """Get current queue size."""
        return self.queue.qsize()
        
    @property
    async def active_requests(self) -> int:
        """Get number of requests currently being processed."""
        async with self._lock:
            return self.in_flight_requests

class LoadBalancer:
    """Implements round-robin load balancing with request queuing."""
    
    def __init__(self):
        self.request_queue = RequestQueue()
        self.current_requests = 0
        self._lock = asyncio.Lock()
        
    async def handle_request(
        self,
        request: Dict[str, Any],
        handler: Callable[[Dict[str, Any]], Awaitable[Any]]
    ) -> Any:
        """
        Handle an incoming request with load balancing and queuing.
        
        Args:
            request: The request to process
            handler: Async function to handle the request
            
        Returns:
            Response from the handler or None if request was rejected
        """
        # Check if we can process more requests
        async with self._lock:
            if (
                self.current_requests >= Config.LOAD_BALANCING["max_requests_in_flight"]
                and not await self.request_queue.add_request(request)
            ):
                return {
                    "error": "System is at capacity",
                    "queue_size": await self.request_queue.queue_size,
                    "retry_after": Config.QUEUE_CONFIG["retry_delay"]
                }
                
            self.current_requests += 1
            
        try:
            # Process the request
            return await asyncio.wait_for(
                handler(request),
                timeout=Config.LOAD_BALANCING["request_timeout"]
            )
        except asyncio.TimeoutError:
            return {
                "error": "Request timed out",
                "retry_after": Config.QUEUE_CONFIG["retry_delay"]
            }
        finally:
            async with self._lock:
                self.current_requests -= 1
                
    async def process_queue(self, handler: Callable[[Dict[str, Any]], Awaitable[Any]]):
        """Background task to process queued requests."""
        while True:
            request = await self.request_queue.get_request()
            if request:
                try:
                    await self.handle_request(request, handler)
                finally:
                    await self.request_queue.complete_request()
            await asyncio.sleep(0.1)  # Prevent tight loop
            
    @property
    async def system_load(self) -> Dict[str, int]:
        """Get current system load metrics."""
        return {
            "current_requests": self.current_requests,
            "queue_size": await self.request_queue.queue_size,
            "active_requests": await self.request_queue.active_requests
        } 