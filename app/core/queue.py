"""
消息队列 / 异步任务系统
SCALE OS v10.0

支持后台任务处理、延迟任务、定时任务
"""

from typing import Optional, Callable, Any, ParamSpec, TypeVar
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import asyncio
import json
from collections import defaultdict
import heapq

P = ParamSpec("P")
T = TypeVar("T")


class TaskStatus(Enum):
    """任务状态"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRY = "retry"


class TaskPriority(Enum):
    """任务优先级"""
    LOW = 10
    NORMAL = 5
    HIGH = 1
    URGENT = 0


@dataclass(order=True)
class Task:
    """任务对象"""
    priority: int
    id: str = field(compare=False)
    name: str = field(compare=False)
    func_name: str = field(compare=False)
    args: tuple = field(compare=False, default_factory=tuple)
    kwargs: dict = field(compare=False, default_factory=dict)
    status: TaskStatus = field(compare=False, default=TaskStatus.PENDING)
    result: Any = field(compare=False, default=None)
    error: Optional[str] = field(compare=False, default=None)
    retries: int = field(compare=False, default=0)
    max_retries: int = field(compare=False, default=3)
    created_at: datetime = field(compare=False, default_factory=datetime.utcnow)
    started_at: Optional[datetime] = field(compare=False, default=None)
    completed_at: Optional[datetime] = field(compare=False, default=None)
    delay_seconds: int = field(compare=False, default=0)


class TaskQueue:
    """任务队列"""
    
    def __init__(self, max_workers: int = 4):
        self._queue: list[Task] = []
        self._workers: int = max_workers
        self._running: bool = False
        self._tasks: dict[str, Task] = {}
        self._handlers: dict[str, Callable] = {}
        self._task_counter: int = 0
    
    def register(self, name: str, handler: Callable):
        """注册任务处理器"""
        self._handlers[name] = handler
    
    def unregister(self, name: str):
        """注销任务处理器"""
        self._handlers.pop(name, None)
    
    async def enqueue(
        self,
        name: str,
        *args,
        priority: TaskPriority = TaskPriority.NORMAL,
        delay_seconds: int = 0,
        max_retries: int = 3,
        **kwargs
    ) -> str:
        """
        添加任务到队列
        
        Returns:
            task_id: 任务ID
        """
        self._task_counter += 1
        task_id = f"task_{self._task_counter}_{datetime.utcnow().timestamp()}"
        
        task = Task(
            priority=priority.value,
            id=task_id,
            name=name,
            func_name=name,
            args=args,
            kwargs=kwargs,
            max_retries=max_retries,
            delay_seconds=delay_seconds,
        )
        
        heapq.heappush(self._queue, task)
        self._tasks[task_id] = task
        
        return task_id
    
    async def get_task(self, task_id: str) -> Optional[Task]:
        """获取任务状态"""
        return self._tasks.get(task_id)
    
    async def cancel(self, task_id: str) -> bool:
        """取消任务"""
        task = self._tasks.get(task_id)
        if task and task.status == TaskStatus.PENDING:
            task.status = TaskStatus.FAILED
            task.error = "Cancelled"
            return True
        return False
    
    async def _process_task(self, task: Task):
        """处理单个任务"""
        handler = self._handlers.get(task.func_name)
        
        if not handler:
            task.status = TaskStatus.FAILED
            task.error = f"Handler not found: {task.func_name}"
            return
        
        task.status = TaskStatus.RUNNING
        task.started_at = datetime.utcnow()
        
        try:
            if asyncio.iscoroutinefunction(handler):
                result = await handler(*task.args, **task.kwargs)
            else:
                result = handler(*task.args, **task.kwargs)
            
            task.result = result
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.utcnow()
            
        except Exception as e:
            task.error = str(e)
            task.retries += 1
            
            if task.retries < task.max_retries:
                task.status = TaskStatus.RETRY
                # 重新加入队列
                heapq.heappush(self._queue, task)
            else:
                task.status = TaskStatus.FAILED
                task.completed_at = datetime.utcnow()
    
    async def _worker(self, worker_id: int):
        """工作协程"""
        while self._running:
            try:
                if not self._queue:
                    await asyncio.sleep(0.1)
                    continue
                
                task = heapq.heappop(self._queue)
                
                # 检查延迟
                if task.delay_seconds > 0:
                    elapsed = (datetime.utcnow() - task.created_at).total_seconds()
                    if elapsed < task.delay_seconds:
                        # 放回队列
                        heapq.heappush(self._queue, task)
                        await asyncio.sleep(0.1)
                        continue
                
                # 处理任务
                if task.status == TaskStatus.PENDING:
                    await self._process_task(task)
                
            except Exception as e:
                print(f"Worker {worker_id} error: {e}")
                await asyncio.sleep(0.1)
    
    async def start(self):
        """启动任务队列"""
        self._running = True
        
        # 启动工作协程
        workers = [
            asyncio.create_task(self._worker(i))
            for i in range(self._workers)
        ]
        
        return workers
    
    async def stop(self):
        """停止任务队列"""
        self._running = False
    
    def get_stats(self) -> dict:
        """获取队列统计"""
        pending = sum(1 for t in self._tasks.values() if t.status == TaskStatus.PENDING)
        running = sum(1 for t in self._tasks.values() if t.status == TaskStatus.RUNNING)
        completed = sum(1 for t in self._tasks.values() if t.status == TaskStatus.COMPLETED)
        failed = sum(1 for t in self._tasks.values() if t.status == TaskStatus.FAILED)
        
        return {
            "pending": pending,
            "running": running,
            "completed": completed,
            "failed": failed,
            "total": len(self._tasks),
        }


# 全局任务队列
task_queue = TaskQueue()


# ============ 任务装饰器 ============

def task(name: str, max_retries: int = 3):
    """
    任务装饰器
    
    @task("send_email", max_retries=5)
    async def send_email(to: str, subject: str, body: str):
        ...
    
    # 调用
    await send_email.delay("user@example.com", "Hello", "World")
    """
    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        # 注册处理器
        task_queue.register(name, func)
        
        # 添加 delay 方法
        async def delay(*args: P.args, **kwargs: P.kwargs) -> str:
            return await task_queue.enqueue(name, *args, max_retries=max_retries, **kwargs)
        
        func.delay = delay  # type: ignore
        return func
    
    return decorator


def periodic_task(interval_seconds: int):
    """
    定时任务装饰器
    
    @periodic_task(3600)  # 每小时执行
    async def cleanup_expired_sessions():
        ...
    """
    def decorator(func: Callable):
        task_queue.register(f"periodic_{func.__name__}", func)
        
        async def run_periodic():
            while True:
                try:
                    await func()
                except Exception as e:
                    print(f"Periodic task error: {e}")
                
                await asyncio.sleep(interval_seconds)
        
        # 启动定时任务
        asyncio.create_task(run_periodic())
        
        return func
    
    return decorator


# ============ 常用任务 ============

@task("send_notification")
async def send_notification(user_id: int, title: str, content: str):
    """发送通知任务"""
    # 这里可以集成实际的通知发送逻辑
    print(f"Sending notification to user {user_id}: {title}")
    return {"user_id": user_id, "title": title, "sent": True}


@task("send_email")
async def send_email(to: str, subject: str, body: str):
    """发送邮件任务"""
    print(f"Sending email to {to}: {subject}")
    return {"to": to, "subject": subject, "sent": True}


@task("process_file")
async def process_file(file_id: int, operation: str):
    """文件处理任务"""
    print(f"Processing file {file_id}: {operation}")
    return {"file_id": file_id, "operation": operation, "processed": True}


@task("generate_report")
async def generate_report(report_type: str, params: dict):
    """生成报告任务"""
    print(f"Generating {report_type} report")
    await asyncio.sleep(2)  # 模拟耗时操作
    return {"report_type": report_type, "generated": True}
