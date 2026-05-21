"""
点赞/收藏 Schemas
SCALE OS v10.0
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class LikeBase(BaseModel):
    """点赞基础模型"""
    target_type: str = Field(..., description="目标类型: post/comment")
    target_id: int = Field(..., description="目标ID")


class LikeCreate(LikeBase):
    """点赞创建模型"""
    pass


class LikeResponse(LikeBase):
    """点赞响应模型"""
    id: int
    user_id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class FavoriteBase(BaseModel):
    """收藏基础模型"""
    post_id: int = Field(..., description="帖子ID")


class FavoriteCreate(FavoriteBase):
    """收藏创建模型"""
    pass


class FavoriteResponse(FavoriteBase):
    """收藏响应模型"""
    id: int
    user_id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class FavoriteListResponse(BaseModel):
    """收藏列表响应"""
    total: int
    items: list[FavoriteResponse]