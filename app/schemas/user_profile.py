"""
用户资料 Schemas
SCALE OS v10.0
"""

from datetime import datetime, date
from typing import Optional

from pydantic import BaseModel, Field


class UserProfileBase(BaseModel):
    """用户资料基础模型"""
    nickname: Optional[str] = Field(None, max_length=50, description="昵称")
    realname: Optional[str] = Field(None, max_length=50, description="真实姓名")
    gender: Optional[str] = Field(None, description="性别")
    signature: Optional[str] = Field(None, max_length=255, description="个性签名")
    bio: Optional[str] = Field(None, description="个人简介")


class UserProfileCreate(UserProfileBase):
    """用户资料创建模型"""
    phone: Optional[str] = Field(None, max_length=20, description="手机号")
    qq: Optional[str] = Field(None, max_length=20, description="QQ")
    wechat: Optional[str] = Field(None, max_length=50, description="微信")
    birthday: Optional[date] = Field(None, description="生日")
    province: Optional[str] = Field(None, description="省份")
    city: Optional[str] = Field(None, description="城市")
    company: Optional[str] = Field(None, description="公司")
    position: Optional[str] = Field(None, description="职位")


class UserProfileUpdate(BaseModel):
    """用户资料更新模型"""
    nickname: Optional[str] = Field(None, max_length=50)
    realname: Optional[str] = Field(None, max_length=50)
    gender: Optional[str] = None
    birthday: Optional[date] = None
    phone: Optional[str] = Field(None, max_length=20)
    qq: Optional[str] = Field(None, max_length=20)
    wechat: Optional[str] = Field(None, max_length=50)
    address: Optional[str] = Field(None, max_length=255)
    avatar: Optional[str] = Field(None, max_length=255)
    cover: Optional[str] = Field(None, max_length=255)
    signature: Optional[str] = Field(None, max_length=255)
    bio: Optional[str] = None
    website: Optional[str] = Field(None, max_length=255)
    province: Optional[str] = None
    city: Optional[str] = None
    district: Optional[str] = None
    company: Optional[str] = None
    position: Optional[str] = None
    industry: Optional[str] = None


class UserProfileResponse(UserProfileBase):
    """用户资料响应模型"""
    id: int
    user_id: int
    avatar: Optional[str]
    cover: Optional[str]
    phone: Optional[str]
    qq: Optional[str]
    wechat: Optional[str]
    province: Optional[str]
    city: Optional[str]
    company: Optional[str]
    position: Optional[str]
    posts_count: int
    comments_count: int
    followers_count: int
    following_count: int
    likes_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
