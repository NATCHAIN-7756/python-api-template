"""
Core 模块
SCALE OS v10.0
"""

from app.core.addon import BaseAddon, AddonInfo
from app.core.addon_loader import addon_loader
from app.core.hook import hooks, HookSystem, Event, EventType, on_event, handle_event
from app.core.cache import cache, CacheService, cached, cache_invalidate, CacheKeys
from app.core.queue import task_queue, TaskQueue, Task, TaskStatus, TaskPriority, task, periodic_task

__all__ = [
    # 插件系统
    "BaseAddon",
    "AddonInfo",
    "addon_loader",
    
    # 钩子系统
    "hooks",
    "HookSystem",
    "Event",
    "EventType",
    "on_event",
    "handle_event",
    
    # 缓存系统
    "cache",
    "CacheService",
    "cached",
    "cache_invalidate",
    "CacheKeys",
    
    # 任务队列
    "task_queue",
    "TaskQueue",
    "Task",
    "TaskStatus",
    "TaskPriority",
    "task",
    "periodic_task",
]
