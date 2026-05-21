"""
日志服务
SCALE OS v10.0
"""

from typing import Optional, List, Any, Callable
from datetime import datetime, timedelta
import json
import uuid
import traceback
import asyncio
from functools import wraps

from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.log import Log, AuditLog, RequestLog, LogLevel, LogType


class LogService:
    """日志服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def write(
        self,
        level: int,
        message: str,
        type: str = "system",
        source: str = "app",
        action: Optional[str] = None,
        user_id: Optional[int] = None,
        tenant_id: Optional[int] = None,
        request_id: Optional[str] = None,
        ip: Optional[str] = None,
        method: Optional[str] = None,
        path: Optional[str] = None,
        status_code: Optional[int] = None,
        data: Optional[dict] = None,
        extra: Optional[dict] = None,
        exception: Optional[Exception] = None,
    ) -> Log:
        """写入日志"""
        log = Log(
            level=level,
            type=type,
            message=message,
            source=source,
            action=action,
            user_id=user_id,
            tenant_id=tenant_id,
            request_id=request_id,
            ip=ip,
            method=method,
            path=path,
            status_code=status_code,
            data=json.dumps(data, default=str) if data else None,
            extra=json.dumps(extra, default=str) if extra else None,
        )
        
        if exception:
            log.exception = str(exception)
            log.stack_trace = traceback.format_exc()
        
        self.db.add(log)
        await self.db.flush()
        
        return log
    
    async def info(self, message: str, **kwargs) -> Log:
        """记录 INFO 日志"""
        return await self.write(LogLevel.INFO.value, message, **kwargs)
    
    async def warning(self, message: str, **kwargs) -> Log:
        """记录 WARNING 日志"""
        return await self.write(LogLevel.WARNING.value, message, **kwargs)
    
    async def error(self, message: str, exception: Optional[Exception] = None, **kwargs) -> Log:
        """记录 ERROR 日志"""
        return await self.write(LogLevel.ERROR.value, message, exception=exception, **kwargs)
    
    async def critical(self, message: str, exception: Optional[Exception] = None, **kwargs) -> Log:
        """记录 CRITICAL 日志"""
        return await self.write(LogLevel.CRITICAL.value, message, exception=exception, **kwargs)
    
    async def audit(
        self,
        action: str,
        resource_type: str,
        resource_id: Optional[int] = None,
        old_value: Optional[dict] = None,
        new_value: Optional[dict] = None,
        user_id: Optional[int] = None,
        tenant_id: Optional[int] = None,
        ip: Optional[str] = None,
        request_id: Optional[str] = None,
        success: bool = True,
        error_message: Optional[str] = None,
    ) -> AuditLog:
        """写入审计日志"""
        audit_log = AuditLog(
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            old_value=json.dumps(old_value, default=str) if old_value else None,
            new_value=json.dumps(new_value, default=str) if new_value else None,
            user_id=user_id,
            tenant_id=tenant_id,
            ip=ip,
            request_id=request_id,
            success=success,
            error_message=error_message,
        )
        
        self.db.add(audit_log)
        await self.db.flush()
        
        return audit_log
    
    async def request(
        self,
        request_id: str,
        method: str,
        path: str,
        status_code: int,
        response_time: int,
        ip: str,
        query: Optional[str] = None,
        headers: Optional[dict] = None,
        body: Optional[str] = None,
        response_size: Optional[int] = None,
        user_agent: Optional[str] = None,
        user_id: Optional[int] = None,
        tenant_id: Optional[int] = None,
    ) -> RequestLog:
        """写入请求日志"""
        request_log = RequestLog(
            request_id=request_id,
            method=method,
            path=path,
            query=query,
            headers=json.dumps(headers, default=str) if headers else None,
            body=body,
            status_code=status_code,
            response_time=response_time,
            response_size=response_size,
            ip=ip,
            user_agent=user_agent,
            user_id=user_id,
            tenant_id=tenant_id,
        )
        
        self.db.add(request_log)
        await self.db.flush()
        
        return request_log
    
    async def list(
        self,
        level: Optional[int] = None,
        type: Optional[str] = None,
        source: Optional[str] = None,
        user_id: Optional[int] = None,
        tenant_id: Optional[int] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[List[Log], int]:
        """查询日志列表"""
        query = select(Log)
        
        if level is not None:
            query = query.where(Log.level >= level)
        
        if type:
            query = query.where(Log.type == type)
        
        if source:
            query = query.where(Log.source == source)
        
        if user_id:
            query = query.where(Log.user_id == user_id)
        
        if tenant_id:
            query = query.where(Log.tenant_id == tenant_id)
        
        if start_time:
            query = query.where(Log.created_at >= start_time)
        
        if end_time:
            query = query.where(Log.created_at <= end_time)
        
        # 计数
        count_query = select(func.count()).select_from(query.subquery())
        count_result = await self.db.execute(count_query)
        total = count_result.scalar() or 0
        
        # 查询
        query = query.offset(skip).limit(limit).order_by(Log.created_at.desc())
        result = await self.db.execute(query)
        logs = list(result.scalars().all())
        
        return logs, total
    
    async def get_stats(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        tenant_id: Optional[int] = None,
    ) -> dict:
        """获取日志统计"""
        if not start_time:
            start_time = datetime.utcnow() - timedelta(days=7)
        
        if not end_time:
            end_time = datetime.utcnow()
        
        # 按级别统计
        level_stats = {}
        for level in LogLevel:
            result = await self.db.execute(
                select(func.count()).where(
                    and_(
                        Log.level == level.value,
                        Log.created_at >= start_time,
                        Log.created_at <= end_time,
                    )
                )
            )
            level_stats[level.name] = count if (count := result.scalar()) else 0
        
        # 按类型统计
        type_result = await self.db.execute(
            select(Log.type, func.count().label("count")).where(
                and_(
                    Log.created_at >= start_time,
                    Log.created_at <= end_time,
                )
            ).group_by(Log.type)
        )
        type_stats = {row.type: row.count for row in type_result}
        
        # 总数
        total_result = await self.db.execute(
            select(func.count()).where(
                and_(
                    Log.created_at >= start_time,
                    Log.created_at <= end_time,
                )
            )
        )
        total = total_result.scalar() or 0
        
        return {
            "total": total,
            "by_level": level_stats,
            "by_type": type_stats,
            "start_time": start_time,
            "end_time": end_time,
        }
    
    async def clean_old_logs(self, days: int = 30) -> int:
        """清理旧日志"""
        cutoff = datetime.utcnow() - timedelta(days=days)
        
        result = await self.db.execute(
            select(Log).where(Log.created_at < cutoff)
        )
        logs = result.scalars().all()
        
        count = len(logs)
        for log in logs:
            await self.db.delete(log)
        
        await self.db.flush()
        return count


# ============ 日志中间件 ============

class LoggingMiddleware:
    """日志中间件"""
    
    def __init__(self, app, db_session_factory):
        self.app = app
        self.db_session_factory = db_session_factory
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        # 生成请求ID
        request_id = str(uuid.uuid4())
        start_time = datetime.utcnow()
        
        # 记录请求
        method = scope["method"]
        path = scope["path"]
        ip = self._get_client_ip(scope)
        
        # 存储响应信息
        status_code = 500
        response_size = 0
        
        async def send_wrapper(message):
            nonlocal status_code, response_size
            
            if message["type"] == "http.response.start":
                status_code = message["status"]
            
            if message["type"] == "http.response.body":
                response_size += len(message.get("body", b""))
            
            await send(message)
        
        try:
            await self.app(scope, receive, send_wrapper)
        except Exception as e:
            status_code = 500
            raise
        finally:
            # 计算响应时间
            response_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            
            # 异步写入请求日志
            async with self.db_session_factory() as db:
                service = LogService(db)
                await service.request(
                    request_id=request_id,
                    method=method,
                    path=path,
                    status_code=status_code,
                    response_time=response_time,
                    ip=ip,
                )
                await db.commit()
    
    def _get_client_ip(self, scope) -> str:
        """获取客户端IP"""
        headers = dict(scope.get("headers", []))
        
        # 检查代理头
        if b"x-forwarded-for" in headers:
            return headers[b"x-forwarded-for"].decode().split(",")[0].strip()
        
        if b"x-real-ip" in headers:
            return headers[b"x-real-ip"].decode()
        
        # 直接连接
        if scope.get("client"):
            return scope["client"][0]
        
        return "unknown"


# ============ 日志装饰器 ============

def audit_log(action: str, resource_type: str):
    """
    审计日志装饰器
    
    @audit_log("update_user", "user")
    async def update_user(user_id: int, data: dict):
        ...
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 获取资源ID
            resource_id = kwargs.get("id") or kwargs.get("user_id") or kwargs.get("post_id") or args[0] if args else None
            
            # 获取用户信息
            user_id = kwargs.get("current_user").id if "current_user" in kwargs else None
            tenant_id = kwargs.get("tenant_id")
            
            try:
                result = await func(*args, **kwargs)
                
                # 记录成功审计日志
                # 这里需要 db session，实际使用时需要注入
                
                return result
            
            except Exception as e:
                # 记录失败审计日志
                raise
        
        return wrapper
    return decorator
