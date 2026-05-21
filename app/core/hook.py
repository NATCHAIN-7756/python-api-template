"""
钩子/事件系统
SCALE OS v10.0

实现类似微擎的消息订阅器和处理器机制
"""

from typing import Callable, Any, Optional
from enum import Enum
from dataclasses import dataclass, field
from collections import defaultdict
import asyncio


class EventType(Enum):
    """事件类型定义"""
    # 用户相关
    USER_REGISTER = "user.register"
    USER_LOGIN = "user.login"
    USER_LOGOUT = "user.logout"
    USER_UPDATE = "user.update"
    USER_DELETE = "user.delete"
    
    # 内容相关
    POST_CREATE = "post.create"
    POST_UPDATE = "post.update"
    POST_DELETE = "post.delete"
    POST_PUBLISH = "post.publish"
    
    COMMENT_CREATE = "comment.create"
    COMMENT_DELETE = "comment.delete"
    
    # 互动相关
    LIKE_ADD = "like.add"
    LIKE_REMOVE = "like.remove"
    FOLLOW_ADD = "follow.add"
    FOLLOW_REMOVE = "follow.remove"
    
    # 消息相关
    MESSAGE_SEND = "message.send"
    NOTIFICATION_SEND = "notification.send"
    
    # 插件相关
    ADDON_INSTALL = "addon.install"
    ADDON_UNINSTALL = "addon.uninstall"
    ADDON_ENABLE = "addon.enable"
    ADDON_DISABLE = "addon.disable"
    
    # 系统相关
    SYSTEM_STARTUP = "system.startup"
    SYSTEM_SHUTDOWN = "system.shutdown"
    SYSTEM_ERROR = "system.error"
    
    # 自定义事件
    CUSTOM = "custom"


@dataclass
class Event:
    """事件对象"""
    type: str                           # 事件类型
    data: Any = None                    # 事件数据
    source: Optional[str] = None        # 事件来源（插件标识）
    timestamp: float = 0               # 时间戳
    stopped: bool = False              # 是否停止传播
    
    def stop(self):
        """停止事件传播"""
        self.stopped = True


@dataclass
class Listener:
    """监听器"""
    callback: Callable                  # 回调函数
    priority: int = 10                 # 优先级（越小越先执行）
    once: bool = False                 # 是否只执行一次
    source: Optional[str] = None       # 来源插件标识


class HookSystem:
    """钩子系统"""
    
    def __init__(self):
        # 订阅器（并行执行，不返回结果）
        self._subscribers: dict[str, list[Listener]] = defaultdict(list)
        # 处理器（互斥执行，返回结果）
        self._handlers: dict[str, list[Listener]] = defaultdict(list)
        # 事件队列（异步处理）
        self._event_queue: list[Event] = []
    
    # ============ 订阅器（并行，用于统计、日志等） ============
    
    def subscribe(self, event: str, callback: Callable, priority: int = 10, 
                  source: Optional[str] = None):
        """
        订阅事件（并行执行，不返回结果）
        类似微擎的 subscribes
        """
        listener = Listener(
            callback=callback,
            priority=priority,
            source=source,
        )
        self._subscribers[event].append(listener)
        # 按优先级排序
        self._subscribers[event].sort(key=lambda x: x.priority)
    
    def unsubscribe(self, event: str, callback: Callable):
        """取消订阅"""
        self._subscribers[event] = [
            l for l in self._subscribers[event] 
            if l.callback != callback
        ]
    
    # ============ 处理器（互斥，用于处理并返回结果） ============
    
    def handle(self, event: str, callback: Callable, priority: int = 10,
               source: Optional[str] = None):
        """
        注册处理器（互斥执行，返回结果）
        类似微擎的 handles
        """
        listener = Listener(
            callback=callback,
            priority=priority,
            source=source,
        )
        self._handlers[event].append(listener)
        # 按优先级排序
        self._handlers[event].sort(key=lambda x: x.priority)
    
    def unhandle(self, event: str, callback: Callable):
        """移除处理器"""
        self._handlers[event] = [
            l for l in self._handlers[event]
            if l.callback != callback
        ]
    
    # ============ 事件触发 ============
    
    def emit(self, event: str, data: Any = None, source: Optional[str] = None) -> Event:
        """
        触发事件（同步）
        1. 先执行所有订阅器（并行）
        2. 再执行处理器（互斥，第一个返回结果的停止传播）
        """
        import time
        
        evt = Event(
            type=event,
            data=data,
            source=source,
            timestamp=time.time(),
        )
        
        # 执行订阅器（并行，不停止）
        for listener in self._subscribers.get(event, []):
            try:
                listener.callback(evt)
            except Exception as e:
                # 订阅器异常不影响其他订阅器
                print(f"Subscriber error: {e}")
        
        # 执行处理器（互斥，返回结果停止）
        result = None
        for listener in self._handlers.get(event, []):
            if evt.stopped:
                break
            
            try:
                result = listener.callback(evt)
                if result is not None:
                    evt.stopped = True
            except Exception as e:
                print(f"Handler error: {e}")
        
        return evt
    
    async def emit_async(self, event: str, data: Any = None, 
                         source: Optional[str] = None) -> Event:
        """
        异步触发事件
        """
        import time
        
        evt = Event(
            type=event,
            data=data,
            source=source,
            timestamp=time.time(),
        )
        
        # 异步执行订阅器
        tasks = []
        for listener in self._subscribers.get(event, []):
            if asyncio.iscoroutinefunction(listener.callback):
                tasks.append(listener.callback(evt))
            else:
                listener.callback(evt)
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
        
        # 执行处理器
        result = None
        for listener in self._handlers.get(event, []):
            if evt.stopped:
                break
            
            try:
                if asyncio.iscoroutinefunction(listener.callback):
                    result = await listener.callback(evt)
                else:
                    result = listener.callback(evt)
                
                if result is not None:
                    evt.stopped = True
            except Exception as e:
                print(f"Handler error: {e}")
        
        return evt
    
    # ============ 工具方法 ============
    
    def get_subscribers(self, event: str) -> list[Listener]:
        """获取事件的所有订阅器"""
        return self._subscribers.get(event, [])
    
    def get_handlers(self, event: str) -> list[Listener]:
        """获取事件的所有处理器"""
        return self._handlers.get(event, [])
    
    def clear(self, source: Optional[str] = None):
        """清除指定来源的所有监听器"""
        if source is None:
            self._subscribers.clear()
            self._handlers.clear()
            return
        
        for event in self._subscribers:
            self._subscribers[event] = [
                l for l in self._subscribers[event]
                if l.source != source
            ]
        
        for event in self._handlers:
            self._handlers[event] = [
                l for l in self._handlers[event]
                if l.source != source
            ]


# 全局钩子系统实例
hooks = HookSystem()


# ============ 装饰器 ============

def on_event(event: str, priority: int = 10):
    """
    事件订阅装饰器
    @on_event("user.register")
    def on_user_register(evt):
        print(f"New user: {evt.data}")
    """
    def decorator(func):
        hooks.subscribe(event, func, priority)
        return func
    return decorator


def handle_event(event: str, priority: int = 10):
    """
    事件处理装饰器
    @handle_event("post.create")
    def handle_post_create(evt):
        # 返回结果将停止传播
        return {"status": "ok"}
    """
    def decorator(func):
        hooks.handle(event, func, priority)
        return func
    return decorator
