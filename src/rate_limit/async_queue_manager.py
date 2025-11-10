"""
Async Rate Limiting Queue Manager
Implements async request queuing for rate limiting
"""
import asyncio
import time
import random
from collections import deque
from typing import Callable, Any, Optional, Coroutine
from src.utils.logger import get_logger

logger = get_logger(__name__)


class AsyncRequestQueue:
    """Manages async API request rate limiting and queuing"""
    
    def __init__(self, max_rate=50, period=60, safety_margin=0.95):
        """
        Args:
            max_rate: Maximum number of requests per period (default 50 for safety)
            period: Time period in seconds (default 60 seconds = 1 minute)
            safety_margin: Safety margin multiplier (0.95 = use 95% of max_rate to avoid hitting limits)
        """
        # Store original max_rate for reference
        self.original_max_rate = max_rate
        # Apply safety margin to be more conservative
        self.max_rate = int(max_rate * safety_margin)
        self.period = period
        self.request_times = deque()
        self.cache = {}
        self.lock = asyncio.Lock()
        logger.info(
            f"AsyncRequestQueue initialized: max_rate={self.max_rate}/min "
            f"(configured: {max_rate}/min, safety margin: {safety_margin})"
        )
    
    async def _clean_old_requests(self):
        """Remove requests older than the period"""
        current_time = time.time()
        while self.request_times and self.request_times[0] < current_time - self.period:
            self.request_times.popleft()
    
    async def _wait_if_needed(self):
        """Wait if we've hit the rate limit (async)"""
        current_time = time.time()
        
        async with self.lock:
            await self._clean_old_requests()
            
            # Check if we're approaching the rate limit (use 80% threshold for early warning)
            threshold = int(self.max_rate * 0.8)
            if len(self.request_times) >= threshold:
                if len(self.request_times) >= self.max_rate:
                    # Calculate wait time until oldest request expires
                    oldest_request = self.request_times[0]
                    wait_time = (oldest_request + self.period) - current_time + 0.5  # Increased buffer
                    if wait_time > 0:
                        logger.warning(f"⏳ Rate limit reached: Waiting {wait_time:.2f} seconds...")
                        await asyncio.sleep(wait_time)
                        await self._clean_old_requests()
                else:
                    # Approaching limit - add small jitter to spread requests
                    jitter = random.uniform(0, 0.5)
                    if jitter > 0.1:  # Only sleep if jitter is meaningful
                        await asyncio.sleep(jitter)
            
            # Record this request
            self.request_times.append(time.time())
    
    async def execute(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute an async function with rate limiting
        Also implements basic caching to reduce API calls
        
        Args:
            func: Async function to execute
            *args: Positional arguments for function
            **kwargs: Keyword arguments for function
        
        Returns:
            Function result
        
        Note: Rate limit errors (429) should be handled by the provider's retry logic.
        This method focuses on preventing rate limits through request throttling.
        """
        # Generate cache key
        cache_key = f"{func.__name__}_{str(args)}_{str(kwargs)}"
        
        # Check cache first
        if cache_key in self.cache:
            logger.debug("✅ Using cached result")
            return self.cache[cache_key]
        
        # Apply rate limiting
        await self._wait_if_needed()
        
        # Execute function
        try:
            result = await func(*args, **kwargs)
            # Cache result (limit cache size to prevent memory issues)
            if len(self.cache) > 100:
                # Remove oldest entry (simple FIFO)
                oldest_key = next(iter(self.cache))
                del self.cache[oldest_key]
            self.cache[cache_key] = result
            return result
        except Exception as e:
            # Log error but don't suppress it - let the provider handle retries
            error_str = str(e).lower()
            if "429" in error_str or "resource exhausted" in error_str or "rate limit" in error_str:
                logger.warning(f"Rate limit error detected in async queue manager: {e}")
                # Don't remove from cache on rate limit errors - we might want to retry
            else:
                logger.error(f"Error executing async function: {e}")
            raise
    
    async def get_stats(self):
        """Get current rate limiting statistics (async)"""
        async with self.lock:
            await self._clean_old_requests()
            return {
                "requests_in_window": len(self.request_times),
                "max_rate": self.max_rate,
                "original_max_rate": self.original_max_rate,
                "cache_size": len(self.cache),
                "utilization_percent": round((len(self.request_times) / self.max_rate * 100) if self.max_rate > 0 else 0, 1)
            }

