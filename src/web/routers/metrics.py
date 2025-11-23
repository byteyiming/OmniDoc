"""
Metrics and observability endpoints.

Provides Redis usage statistics, parallel execution metrics, and system observability.
"""
from __future__ import annotations

from typing import Dict, Any, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from src.utils.redis_client import get_redis_pool
from src.coordination.metrics import _metrics_store, get_metrics
from src.utils.logger import get_logger
from src.web.monitoring import get_all_metrics, get_timing_stats

logger = get_logger(__name__)

router = APIRouter(prefix="/api/metrics", tags=["metrics"])


class RedisUsageResponse(BaseModel):
    """Redis usage statistics and rate limiting info"""
    available: bool
    usage_stats: Optional[Dict[str, Any]] = None
    rate_limit_reached: bool = False
    message: Optional[str] = None


class SystemMetricsResponse(BaseModel):
    """System-wide metrics"""
    redis: RedisUsageResponse
    parallel_execution: Dict[str, Any]
    counters: Dict[str, int]
    timings: Dict[str, Dict[str, float]]


@router.get("/redis", response_model=RedisUsageResponse)
async def get_redis_usage() -> RedisUsageResponse:
    """
    Get Redis usage statistics and rate limiting information.
    
    Useful for monitoring Redis request consumption and avoiding monthly limits.
    
    Returns:
        RedisUsageResponse with usage stats and rate limit status
    """
    redis_pool = get_redis_pool()
    
    if not redis_pool:
        return RedisUsageResponse(
            available=False,
            message="Redis not configured"
        )
    
    try:
        usage_stats = redis_pool.get_usage_stats()
        can_make, error_msg = redis_pool.check_rate_limit()
        
        return RedisUsageResponse(
            available=True,
            usage_stats=usage_stats,
            rate_limit_reached=not can_make,
            message=error_msg if not can_make else None
        )
    except Exception as e:
        logger.error(f"Failed to get Redis usage stats: {e}")
        return RedisUsageResponse(
            available=False,
            message=f"Error retrieving stats: {str(e)}"
        )


@router.get("/parallel-execution/{project_id}")
async def get_parallel_execution_metrics(project_id: str) -> Dict[str, Any]:
    """
    Get parallel execution metrics for a specific project.
    
    Returns metrics about document generation performance, including:
    - Total execution time
    - Sequential time estimate
    - Speedup achieved
    - Parallel efficiency
    - Wave-by-wave breakdown
    
    Args:
        project_id: Project identifier
        
    Returns:
        Dictionary with execution metrics
    """
    if project_id not in _metrics_store:
        raise HTTPException(status_code=404, detail="Project metrics not found. Project may not exist or may not have started execution yet.")
    
    metrics = _metrics_store[project_id]
    return metrics.get_summary()


@router.get("/system", response_model=SystemMetricsResponse)
async def get_system_metrics() -> SystemMetricsResponse:
    """
    Get comprehensive system metrics.
    
    Includes:
    - Redis usage and rate limiting
    - System counters (requests, errors, etc.)
    - Timing statistics
    - Active parallel execution projects
    
    Returns:
        SystemMetricsResponse with all metrics
    """
    # Get Redis usage
    redis_pool = get_redis_pool()
    redis_response = RedisUsageResponse(
        available=redis_pool is not None,
        usage_stats=redis_pool.get_usage_stats() if redis_pool else None
    )
    
    # Get all counters
    counters = get_all_metrics()
    
    # Get timing stats for common metrics
    timing_keys = [
        "coordination.workflow.total_time",
        "coordination.wave.execution_time",
        "coordination.document.generation_time"
    ]
    timings = {}
    for key in timing_keys:
        stats = get_timing_stats(key)
        if stats:
            timings[key] = stats
    
    # Get active parallel execution projects
    active_projects = {
        project_id: metrics.get_summary()
        for project_id, metrics in _metrics_store.items()
    }
    
    return SystemMetricsResponse(
        redis=redis_response,
        parallel_execution={
            "active_projects": len(active_projects),
            "projects": active_projects
        },
        counters=counters,
        timings=timings
    )

