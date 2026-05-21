"""
Redis 缓存服务
SCALE OS v10.0
"""

from typing import Optional, Any, Callable, TypeVar, ParamSpec
from functools import wraps
import json
import asyncio

try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

from app.core.config import settings


P = ParamSpec("P")
T = TypeVar("T")


class CacheService:
    """缓存服务"""
    
    def __init__(self, redis_url: Optional[str] = None):
        self._redis: Optional[redis.Redis] = None
        self._redis_url = redis_url or getattr(settings, "REDIS_URL", None)
        self._enabled = bool(self._redis_url) and REDIS_AVAILABLE
        self._local_cache: dict[str, Any] = {}  # 本地缓存降级
    
    async def connect(self):
        """连接 Redis"""
        if not self._enabled:
            return
        
        if REDIS_AVAILABLE and self._redis_url:
            try:
                self._redis = redis.from_url(
                    self._redis_url,
                    encoding="utf-8",
                    decode_responses=True
                )
                # 测试连接
                await self._redis.ping()
            except Exception as e:
                print(f"Redis connection failed: {e}")
                self._enabled = False
                self._redis = None
    
    async def disconnect(self):
        """断开连接"""
        if self._redis:
            await self._redis.close()
    
    async def get(self, key: str) -> Optional[Any]:
        """获取缓存"""
        if self._redis:
            try:
                value = await self._redis.get(key)
                if value:
                    return json.loads(value)
            except Exception as e:
                print(f"Redis get error: {e}")
        
        # 降级到本地缓存
        return self._local_cache.get(key)
    
    async def set(self, key: str, value: Any, ttl: int = 300):
        """设置缓存"""
        if self._redis:
            try:
                await self._redis.setex(key, ttl, json.dumps(value, default=str))
            except Exception as e:
                print(f"Redis set error: {e}")
        
        # 同时写入本地缓存
        self._local_cache[key] = value
    
    async def delete(self, key: str):
        """删除缓存"""
        if self._redis:
            try:
                await self._redis.delete(key)
            except Exception as e:
                print(f"Redis delete error: {e}")
        
        if key in self._local_cache:
            del self._local_cache[key]
    
    async def delete_pattern(self, pattern: str):
        """删除匹配的缓存"""
        if self._redis:
            try:
                keys = await self._redis.keys(pattern)
                if keys:
                    await self._redis.delete(*keys)
            except Exception as e:
                print(f"Redis delete_pattern error: {e}")
    
    async def exists(self, key: str) -> bool:
        """检查缓存是否存在"""
        if self._redis:
            try:
                return await self._redis.exists(key) > 0
            except Exception as e:
                print(f"Redis exists error: {e}")
        
        return key in self._local_cache
    
    async def incr(self, key: str, amount: int = 1) -> int:
        """计数器增加"""
        if self._redis:
            try:
                return await self._redis.incrby(key, amount)
            except Exception as e:
                print(f"Redis incr error: {e}")
        
        # 本地计数
        self._local_cache[key] = self._local_cache.get(key, 0) + amount
        return self._local_cache[key]
    
    async def expire(self, key: str, ttl: int):
        """设置过期时间"""
        if self._redis:
            try:
                await self._redis.expire(key, ttl)
            except Exception as e:
                print(f"Redis expire error: {e}")
    
    async def get_ttl(self, key: str) -> int:
        """获取剩余过期时间"""
        if self._redis:
            try:
                return await self._redis.ttl(key)
            except Exception as e:
                print(f"Redis ttl error: {e}")
        
        return -1


# 全局缓存实例
cache = CacheService()


# ============ 缓存装饰器 ============

def cached(
    key_prefix: str,
    ttl: int = 300,
    key_builder: Optional[Callable] = None,
):
    """
    缓存装饰器
    
    @cached("user", ttl=600)
    async def get_user(user_id: int):
        ...
    
    缓存 key: user:{user_id}
    """
    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        @wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            # 构建 key
            if key_builder:
                cache_key = key_builder(*args, **kwargs)
            else:
                # 默认使用第一个参数作为 key
                key_parts = [key_prefix]
                if args:
                    key_parts.append(str(args[0]))
                cache_key = ":".join(key_parts)
            
            # 尝试从缓存获取
            cached_value = await cache.get(cache_key)
            if cached_value is not None:
                return cached_value
            
            # 执行函数
            result = await func(*args, **kwargs)
            
            # 写入缓存
            if result is not None:
                await cache.set(cache_key, result, ttl)
            
            return result
        
        return wrapper
    return decorator


def cache_invalidate(key_prefix: str, key_builder: Optional[Callable] = None):
    """
    缓存失效装饰器
    
    @cache_invalidate("user")
    async def update_user(user_id: int, data: dict):
        ...
    """
    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        @wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            # 执行函数
            result = await func(*args, **kwargs)
            
            # 清除缓存
            if key_builder:
                cache_key = key_builder(*args, **kwargs)
            else:
                key_parts = [key_prefix]
                if args:
                    key_parts.append(str(args[0]))
                cache_key = ":".join(key_parts)
            
            await cache.delete(cache_key)
            
            return result
        
        return wrapper
    return decorator


# ============ 缓存键生成器 ============

class CacheKeys:
    """缓存键生成器"""
    
    @staticmethod
    def user(user_id: int) -> str:
        return f"user:{user_id}"
    
    @staticmethod
    def user_profile(user_id: int) -> str:
        return f"user:profile:{user_id}"
    
    @staticmethod
    def post(post_id: int) -> str:
        return f"post:{post_id}"
    
    @staticmethod
    def post_list(page: int, filters: str = "") -> str:
        return f"posts:{page}:{filters}"
    
    @staticmethod
    def category_tree() -> str:
        return "category:tree"
    
    @staticmethod
    def menu_tree(tenant_id: Optional[int] = None) -> str:
        return f"menu:tree:{tenant_id or 'global'}"
    
    @staticmethod
    def tenant(identifier: str) -> str:
        return f"tenant:{identifier}"
    
    @staticmethod
    def addon_config(addon_id: str, tenant_id: Optional[int] = None) -> str:
        return f"addon:{addon_id}:config:{tenant_id or 'global'}"
    
    @staticmethod
    def hot_search() -> str:
        return "search:hot"
    
    @staticmethod
    def rate_limit(key: str) -> str:
        return f"rate_limit:{key}"
