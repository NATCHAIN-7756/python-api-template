"""
私信/通知 Schemas
SCALE OS v10.0
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class MessageBase(BaseModel):
    """私信基础模型"""
    content: str = Field(..., min_length=1, max_length=5000, description="消息内容")


class MessageCreate(MessageBase):
    """私信创建模型"""
    receiver_id: int = Field(..., description="接收者ID")


class MessageResponse(MessageBase):
    """私信响应模型"""
    id: int
    sender_id: int
    receiver_id: int
    is_read: bool
    read_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class MessageListResponse(BaseModel):
    """私信列表响应"""
    total: int
    items: list[MessageResponse]


class NotificationBase(BaseModel):
    """通知基础模型"""
    type: str = Field(..., description="通知类型")
    title: str = Field(..., max_length=200, description="标题")


class NotificationCreate(NotificationBase):
    """通知创建模型"""
    content: Optional[str] = Field(None, description="内容")
    related_type: Optional[str] = Field(None, description="关联类型")
    related_id: Optional[int] = Field(None, description="关联ID")
    sender_id: Optional[int] = Field(None, description="发送者ID")


class NotificationResponse(NotificationBase):
    """通知响应模型"""
    id: int
    user_id: int
    content: Optional[str]
    related_type: Optional[str]
    related_id: Optional[int]
    sender_id: Optional[int]
    is_read: bool
    read_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class NotificationListResponse(BaseModel):
    """通知列表响应"""
    total: int
    unread: int
    items: list[NotificationResponse]