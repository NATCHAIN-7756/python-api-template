"""
Core 模块
SCALE OS v10.0
"""

from app.core.addon import BaseAddon, AddonInfo
from app.core.addon_loader import addon_loader
from app.core.hook import hooks, HookSystem, Event, EventType, on_event, handle_event

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
]
