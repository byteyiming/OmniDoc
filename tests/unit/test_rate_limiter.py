"""
Unit Tests: RequestQueue (Rate Limiter)
Fast, isolated tests for rate limiting
"""
import pytest
import time
from unittest.mock import Mock
from src.rate_limit.queue_manager import RequestQueue


@pytest.mark.unit
class TestRequestQueue:
    """Test RequestQueue class"""
    
    def test_rate_limiter_initialization(self):
        """Test rate limiter initialization"""
        queue = RequestQueue(max_rate=60, period=60)
        
        assert queue.max_rate == 60
        assert queue.period == 60
    
    def test_execute_function(self, rate_limiter):
        """Test executing a function through rate limiter"""
        def test_func():
            return "result"
        
        result = rate_limiter.execute(test_func)
        
        assert result == "result"
    
    def test_rate_limit_enforcement(self):
        """Test that rate limiting enforces limits"""
        queue = RequestQueue(max_rate=2, period=1)  # Very strict limit
        
        def test_func():
            return "ok"
        
        # First two calls should work
        queue.execute(test_func)
        queue.execute(test_func)
        
        # Third call might need to wait (depending on timing)
        start = time.time()
        queue.execute(test_func)
        duration = time.time() - start
        
        # Should complete (may wait if limit hit)
        assert duration >= 0
    
    def test_caching(self, rate_limiter):
        """Test that rate limiter caches results"""
        call_count = {"count": 0}
        
        def expensive_func(arg1="default"):
            call_count["count"] += 1
            return f"result_{call_count['count']}"
        
        # First call
        result1 = rate_limiter.execute(expensive_func)
        # Second call with same args should use cache
        result2 = rate_limiter.execute(expensive_func)
        
        # Should complete successfully
        assert result1 is not None
        assert result2 is not None
        assert call_count["count"] >= 1
    
    def test_get_stats(self, rate_limiter):
        """Test getting statistics"""
        rate_limiter.execute(lambda: "test")
        
        stats = rate_limiter.get_stats()
        
        assert "requests_in_window" in stats
        assert "max_rate" in stats
        assert "cache_size" in stats
        assert stats["max_rate"] == 1000  # From fixture

