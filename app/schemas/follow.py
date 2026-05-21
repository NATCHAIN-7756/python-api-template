"""
关注/好友 Schemas
SCALE OS v10.0
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class FollowBase(BaseModel):
    """关注基础模型"""
    following_id: int = Field(..., description="被关注用户ID")


class FollowCreate(FollowBase):
    """关注创建模型"""
    pass


class FollowResponse(FollowBase):
    """关注响应模型"""
    id: int
    follower_id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class FollowListResponse(BaseModel):
    """关注列表响应"""
    total: int
    followers: list[FollowResponse]
    following: list[FollowResponse]


class FriendBase(BaseModel):
    """好友基础模型"""
    friend_id: int = Field(..., description="好友用户ID")


class FriendCreate(FriendBase):
    """好友创建模型"""
    remark: Optional[str] = Field(None, max_length=50, description="备注名")


class FriendUpdate(BaseModel):
    """好友更新模型"""
    remark: Optional[str] = Field(None, max_length=50, description="备注名")


class FriendResponse(FriendBase):
    """好友响应模型"""
    id: int
    user_id: int
    status: str
    remark: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class FriendListResponse(BaseModel):
    """好友列表响应"""
    total: int
    items: list[FriendResponse]