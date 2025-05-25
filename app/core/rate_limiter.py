"""
Rate limiter module for API requests.

This module implements a queue-based rate limiting system to manage
API requests within allowed limits.
"""

import time
import asyncio
from fastapi import HTTPException, Depends
from typing import Dict, List, Optional, Callable
import threading
from collections import deque

class RateLimiter:
    """
    Queue-based rate limiter for API requests.
    
    This class implements a token bucket algorithm with a request queue
    to handle rate limiting for API calls.
    """
    
    def __init__(self, max_requests: int, time_window: int, max_queue_size: int = 100):
        """
        Initialize the rate limiter.
        
        Args:
            max_requests: Maximum number of requests allowed in the time window
            time_window: Time window in seconds
            max_queue_size: Maximum size of the request queue
        """
        self.max_requests = max_requests
        self.time_window = time_window
        self.max_queue_size = max_queue_size
        self.request_timestamps: deque = deque(maxlen=max_requests)
        self.request_queue: asyncio.Queue = asyncio.Queue(maxsize=max_queue_size)
        self.lock = threading.Lock()
        
        # Start the queue processor
        self.queue_task = asyncio.create_task(self._process_queue())
    
    async def limit(self):
        """
        Rate limiting dependency for FastAPI endpoints.
        
        This method can be used as a dependency in FastAPI routes to
        apply rate limiting.
        
        Raises:
            HTTPException: If rate limit is exceeded and queue is full
        """
        # Check if we're under the rate limit
        current_time = time.time()
        
        with self.lock:
            # Remove timestamps outside the current window
            while self.request_timestamps and self.request_timestamps[0] < current_time - self.time_window:
                self.request_timestamps.popleft()
            
            # If we're under the limit, allow the request immediately
            if len(self.request_timestamps) < self.max_requests:
                self.request_timestamps.append(current_time)
                return
        
        # If we're over the limit, try to queue the request
        try:
            # Create a future to wait on
            future = asyncio.Future()
            await self.request_queue.put(future)
            
            # Wait for our turn (when the future is resolved)
            await future
            
        except asyncio.QueueFull:
            # If the queue is full, reject the request
            raise HTTPException(
                status_code=429,
                detail="Too many requests. Please try again later."
            )
    
    async def _process_queue(self):
        """
        Process the request queue.
        
        This method runs in the background and processes queued requests
        as rate limit capacity becomes available.
        """
        while True:
            # Get the next request from the queue
            future = await self.request_queue.get()
            
            # Wait until we can process a request
            await self._wait_for_token()
            
            # Mark the future as done to unblock the waiting request
            future.set_result(None)
            
            # Mark the task as done in the queue
            self.request_queue.task_done()
    
    async def _wait_for_token(self):
        """
        Wait until a token is available in the rate limiter.
        """
        while True:
            current_time = time.time()
            
            with self.lock:
                # Remove timestamps outside the current window
                while self.request_timestamps and self.request_timestamps[0] < current_time - self.time_window:
                    self.request_timestamps.popleft()
                
                # If we're under the limit, add a timestamp and return
                if len(self.request_timestamps) < self.max_requests:
                    self.request_timestamps.append(current_time)
                    return
            
            # If we're still over the limit, wait a bit and try again
            oldest_timestamp = self.request_timestamps[0]
            wait_time = oldest_timestamp + self.time_window - current_time
            
            if wait_time > 0:
                await asyncio.sleep(min(wait_time, 1.0))  # Wait at most 1 second at a time
            else:
                await asyncio.sleep(0.1)  # Avoid busy waiting

class UserRateLimiter:
    """
    User-specific rate limiter.
    
    This class manages rate limits on a per-user basis.
    """
    
    def __init__(self, max_requests: int, time_window: int, max_queue_size: int = 100):
        """
        Initialize the user rate limiter.
        
        Args:
            max_requests: Maximum number of requests allowed in the time window
            time_window: Time window in seconds
            max_queue_size: Maximum size of the request queue
        """
        self.max_requests = max_requests
        self.time_window = time_window
        self.max_queue_size = max_queue_size
        self.limiters: Dict[str, RateLimiter] = {}
        self.lock = threading.Lock()
    
    def get_limiter(self, user_id: str) -> RateLimiter:
        """
        Get or create a rate limiter for a specific user.
        
        Args:
            user_id: User identifier
            
        Returns:
            RateLimiter for the specified user
        """
        with self.lock:
            if user_id not in self.limiters:
                self.limiters[user_id] = RateLimiter(
                    max_requests=self.max_requests,
                    time_window=self.time_window,
                    max_queue_size=self.max_queue_size
                )
            return self.limiters[user_id]
    
    def limit_for_user(self, user_id: str) -> Callable:
        """
        Create a dependency for rate limiting a specific user.
        
        Args:
            user_id: User identifier
            
        Returns:
            Dependency function for FastAPI
        """
        limiter = self.get_limiter(user_id)
        
        async def limit():
            await limiter.limit()
        
        return limit
