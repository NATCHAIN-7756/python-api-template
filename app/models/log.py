"""
结构化日志系统
SCALE OS v10.0

支持日志分级、结构化存储、请求追踪、审计日志
"""

from datetime import datetime
from typing import Optional, Any
from enum import Enum
import json
import traceback

from sqlalchemy import String, Integer, DateTime, ForeignKey, Boolean, Text, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class LogLevel(Enum):
    """日志级别"""
    DEBUG = 10
    INFO = 20
    WARNING = 30
    ERROR = 40
    CRITICAL = 50


class LogType(Enum):
    """日志类型"""
    SYSTEM = "system"           # 系统日志
    REQUEST = "request"         # 请求日志
    AUDIT = "audit"             # 审计日志
    ERROR = "error"             # 错误日志
    SECURITY = "security"       # 安全日志
    BUSINESS = "business"       # 业务日志
    ADDON = "addon"             # 插件日志


class Log(Base):
    """日志表"""
    __tablename__ = "logs"
    __table_args__ = (
        Index("idx_logs_created_at", "created_at"),
        Index("idx_logs_level", "level"),
        Index("idx_logs_type", "type"),
        Index("idx_logs_source", "source"),
        Index("idx_logs_user_id", "user_id"),
        Index("idx_logs_tenant_id", "tenant_id"),
        Index("idx_logs_request_id", "request_id"),
    )
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    
    # 基本信息
    level: Mapped[int] = mapped_column(Integer, nullable=False, comment="日志级别")
    type: Mapped[str] = mapped_column(String(20), default="system", comment="日志类型")
    message: Mapped[str] = mapped_column(Text, nullable=False, comment="日志消息")
    
    # 来源
    source: Mapped[str] = mapped_column(String(50), default="app", comment="来源模块")
    action: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, comment="操作动作")
    
    # 上下文
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)
    tenant_id: Mapped[Optional[int]] = mapped_column(ForeignKey("tenants.id"), nullable=True)
    request_id: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, comment="请求ID")
    
    # 请求信息
    ip: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, comment="IP地址")
    method: Mapped[Optional[str]] = mapped_column(String(10), nullable=True, comment="HTTP方法")
    path: Mapped[Optional[str]] = mapped_column(String(200), nullable=True, comment="请求路径")
    status_code: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, comment="响应状态码")
    
    # 扩展数据
    data: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="扩展数据JSON")
    extra: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="额外信息JSON")
    
    # 错误信息
    exception: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="异常信息")
    stack_trace: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="堆栈追踪")
    
    # 时间
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    
    # 关系
    user: Mapped[Optional["User"]] = relationship("User")
    tenant: Mapped[Optional["Tenant"]] = relationship("Tenant")
    
    def __repr__(self) -> str:
        return f"<Log {self.id} level={self.level} type={self.type}>"


class AuditLog(Base):
    """审计日志表（重要操作单独记录）"""
    __tablename__ = "audit_logs"
    __table_args__ = (
        Index("idx_audit_logs_created_at", "created_at"),
        Index("idx_audit_logs_user_id", "user_id"),
        Index("idx_audit_logs_action", "action"),
    )
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    
    # 操作信息
    action: Mapped[str] = mapped_column(String(100), nullable=False, comment="操作动作")
    resource_type: Mapped[str] = mapped_column(String(50), nullable=False, comment="资源类型")
    resource_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, comment="资源ID")
    
    # 变更详情
    old_value: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="变更前值JSON")
    new_value: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="变更后值JSON")
    
    # 操作者
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)
    tenant_id: Mapped[Optional[int]] = mapped_column(ForeignKey("tenants.id"), nullable=True)
    
    # 请求信息
    ip: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    request_id: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # 结果
    success: Mapped[bool] = mapped_column(Boolean, default=True, comment="是否成功")
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # 时间
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # 关系
    user: Mapped[Optional["User"]] = relationship("User")
    tenant: Mapped[Optional["Tenant"]] = relationship("Tenant")
    
    def __repr__(self) -> str:
        return f"<AuditLog {self.id} action={self.action}>"


class RequestLog(Base):
    """请求日志表（API请求追踪）"""
    __tablename__ = "request_logs"
    __table_args__ = (
        Index("idx_request_logs_created_at", "created_at"),
        Index("idx_request_logs_request_id", "request_id"),
        Index("idx_request_logs_path", "path"),
    )
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    
    # 请求标识
    request_id: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    
    # 请求信息
    method: Mapped[str] = mapped_column(String(10), nullable=False)
    path: Mapped[str] = mapped_column(String(200), nullable=False)
    query: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="查询参数")
    headers: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="请求头JSON")
    body: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="请求体")
    
    # 响应信息
    status_code: Mapped[int] = mapped_column(Integer, nullable=False)
    response_time: Mapped[int] = mapped_column(Integer, nullable=False, comment="响应时间(ms)")
    response_size: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, comment="响应大小")
    
    # 客户端
    ip: Mapped[str] = mapped_column(String(50), nullable=False)
    user_agent: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    
    # 用户
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)
    tenant_id: Mapped[Optional[int]] = mapped_column(ForeignKey("tenants.id"), nullable=True)
    
    # 时间
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # 关系
    user: Mapped[Optional["User"]] = relationship("User")
    tenant: Mapped[Optional["Tenant"]] = relationship("Tenant")
    
    def __repr__(self) -> str:
        return f"<RequestLog {self.request_id} {self.method} {self.path}>"