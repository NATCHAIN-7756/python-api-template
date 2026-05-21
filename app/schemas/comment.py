"""
评论 Schemas
SCALE OS v10.0
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field
from app.schemas.user import UserResponse


class CommentBase(BaseModel):
    """评论基础模型"""
    content: str = Field(..., min_length=1, max_length=5000, description="评论内容")


class CommentCreate(CommentBase):
    """评论创建模型"""
    post_id: int = Field(..., description="帖子ID")
    parent_id: Optional[int] = Field(None, description="父评论ID")
    reply_to_id: Optional[int] = Field(None, description="回复用户ID")


class CommentUpdate(BaseModel):
    """评论更新模型"""
    content: Optional[str] = Field(None, min_length=1, max_length=5000)


class CommentResponse(CommentBase):
    """评论响应模型"""
    id: int
    post_id: int
    author_id: int
    parent_id: Optional[int]
    reply_to_id: Optional[int]
    level: int
    is_hidden: bool
    likes_count: int
    replies_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CommentDetailResponse(CommentResponse):
    """评论详情响应模型"""
    author: Optional[UserResponse] = None
    reply_to: Optional[UserResponse] = None
    replies: list["CommentDetailResponse"] = []


class CommentListResponse(BaseModel):
    """评论列表响应"""
    total: int
    items: list[CommentResponse]