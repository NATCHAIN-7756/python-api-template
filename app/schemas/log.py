"""
日志 Schemas
SCALE OS v10.0
"""

from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field


class LogBase(BaseModel):
    """日志基础"""
    level: int
    type: str
    message: str


class LogResponse(BaseModel):
    """日志响应"""
    id: int
    level: int
    type: str
    message: str
    source: str
    action: Optional[str] = None
    user_id: Optional[int] = None
    tenant_id: Optional[int] = None
    request_id: Optional[str] = None
    ip: Optional[str] = None
    method: Optional[str] = None
    path: Optional[str] = None
    status_code: Optional[int] = None
    data: Optional[dict] = None
    exception: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class AuditLogResponse(BaseModel):
    """审计日志响应"""
    id: int
    action: str
    resource_type: str
    resource_id: Optional[int] = None
    old_value: Optional[dict] = None
    new_value: Optional[dict] = None
    user_id: Optional[int] = None
    tenant_id: Optional[int] = None
    ip: Optional[str] = None
    success: bool
    error_message: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class RequestLogResponse(BaseModel):
    """请求日志响应"""
    id: int
    request_id: str
    method: str
    path: str
    query: Optional[str] = None
    status_code: int
    response_time: int
    response_size: Optional[int] = None
    ip: str
    user_agent: Optional[str] = None
    user_id: Optional[int] = None
    tenant_id: Optional[int] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class LogStatsResponse(BaseModel):
    """日志统计响应"""
    total: int
    by_level: dict
    by_type: dict
    start_time: datetime
    end_time: datetime


class LogQuery(BaseModel):
    """日志查询参数"""
    level: Optional[int] = None
    type: Optional[str] = None
    source: Optional[str] = None
    user_id: Optional[int] = None
    tenant_id: Optional[int] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    skip: int = Field(default=0, ge=0)
    limit: int = Field(default=100, ge=1, le=1000)
