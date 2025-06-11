import time
from functools import wraps
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, Optional, Tuple, Union
import re

# Simple in-memory cache
# In production, consider using Redis
cache_store: Dict[str, Tuple[Any, float, Optional[float]]] = {}

def cache(
    ttl: int = 300,  # 5 minutes default TTL
    key_prefix: str = '',
    max_size: int = 1000  # Maximum number of cached items
) -> Callable:
    """Cache decorator with TTL and size limit
    
    Args:
        ttl: Time to live in seconds
        key_prefix: Prefix for cache key
        max_size: Maximum number of items in cache
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs) -> Any:
            # Generate cache key
            cache_key = f"{key_prefix}:{f.__name__}:{str(args)}:{str(kwargs)}"
            
            current_time = time.time()
            
            # Clean expired entries if cache is full
            if len(cache_store) >= max_size:
                _clean_expired_cache(current_time)
                
                # If still full, remove oldest entries
                while len(cache_store) >= max_size:
                    oldest_key = min(
                        cache_store.keys(),
                        key=lambda k: cache_store[k][1]
                    )
                    del cache_store[oldest_key]
            
            # Check if cached and not expired
            if cache_key in cache_store:
                value, timestamp, expiry = cache_store[cache_key]
                if expiry is None or current_time < expiry:
                    return value
            
            # Calculate result
            result = f(*args, **kwargs)
            
            # Store in cache
            expiry_time = current_time + ttl if ttl > 0 else None
            cache_store[cache_key] = (result, current_time, expiry_time)
            
            return result
        return decorated_function
    return decorator

def _clean_expired_cache(current_time: float) -> None:
    """Remove expired entries from cache"""
    expired_keys = [
        key for key, (_, _, expiry) in cache_store.items()
        if expiry is not None and current_time >= expiry
    ]
    for key in expired_keys:
        del cache_store[key]

def clear_cache(prefix: str = '') -> None:
    """Clear all cache entries with given prefix"""
    if prefix:
        keys_to_delete = [
            key for key in cache_store.keys()
            if key.startswith(prefix)
        ]
        for key in keys_to_delete:
            del cache_store[key]
    else:
        cache_store.clear()

def get_cache_stats() -> Dict[str, Union[int, float]]:
    """Get cache statistics"""
    current_time = time.time()
    total_items = len(cache_store)
    expired_items = sum(
        1 for _, _, expiry in cache_store.values()
        if expiry is not None and current_time >= expiry
    )
    
    # Calculate average age of cached items
    if total_items > 0:
        avg_age = sum(
            current_time - timestamp
            for _, timestamp, _ in cache_store.values()
        ) / total_items
    else:
        avg_age = 0
    
    return {
        'total_items': total_items,
        'expired_items': expired_items,
        'active_items': total_items - expired_items,
        'average_age': avg_age
    }

def cache_sensor_data(
    data: Any,
    device_id: str,
    sensor_type: str,
    ttl: int = 300
) -> None:
    """Cache sensor data with specific key"""
    key = f"sensor:{device_id}:{sensor_type}"
    current_time = time.time()
    cache_store[key] = (data, current_time, current_time + ttl)

def get_cached_sensor_data(
    device_id: str,
    sensor_type: str
) -> Optional[Any]:
    """Get cached sensor data if not expired"""
    key = f"sensor:{device_id}:{sensor_type}"
    if key in cache_store:
        value, _, expiry = cache_store[key]
        if expiry is None or time.time() < expiry:
            return value
    return None

def delete_pattern(pattern: str) -> int:
    """Delete cache entries matching a pattern"""
    deleted_count = 0
    keys_to_delete = []
    
    # Convert pattern to regex (simple glob pattern support)
    regex_pattern = pattern.replace('*', '.*')
    
    for key in cache_store.keys():
        if re.match(regex_pattern, key):
            keys_to_delete.append(key)
    
    for key in keys_to_delete:
        del cache_store[key]
        deleted_count += 1
    
    return deleted_count