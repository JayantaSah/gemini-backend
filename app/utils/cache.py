import json
import redis
from typing import List, Optional
from app.config import settings

# Redis client
redis_client = redis.from_url(settings.redis_url, decode_responses=True)


def get_redis_client():
    """Get Redis client instance"""
    return redis_client


def cache_user_chatrooms(user_id: int, chatrooms: List[dict], ttl: int = 600) -> None:
    """Cache user chatrooms with TTL (default 10 minutes)"""
    cache_key = f"user_chatrooms:{user_id}"
    redis_client.setex(cache_key, ttl, json.dumps(chatrooms))


def get_cached_chatrooms(user_id: int) -> Optional[List[dict]]:
    """Get cached user chatrooms"""
    cache_key = f"user_chatrooms:{user_id}"
    cached_data = redis_client.get(cache_key)
    if cached_data:
        return json.loads(cached_data)
    return None


def invalidate_chatroom_cache(user_id: int) -> None:
    """Invalidate user chatroom cache"""
    cache_key = f"user_chatrooms:{user_id}"
    redis_client.delete(cache_key)


def cache_user_session(user_id: int, session_data: dict, ttl: int = 86400) -> None:
    """Cache user session data (default 24 hours)"""
    cache_key = f"user_session:{user_id}"
    redis_client.setex(cache_key, ttl, json.dumps(session_data))


def get_cached_user_session(user_id: int) -> Optional[dict]:
    """Get cached user session data"""
    cache_key = f"user_session:{user_id}"
    cached_data = redis_client.get(cache_key)
    if cached_data:
        return json.loads(cached_data)
    return None


def invalidate_user_session(user_id: int) -> None:
    """Invalidate user session cache"""
    cache_key = f"user_session:{user_id}"
    redis_client.delete(cache_key)

