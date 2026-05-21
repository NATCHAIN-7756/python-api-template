"""
积分系统 Schemas
SCALE OS v10.0
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class UserPointsBase(BaseModel):
    """用户积分基础模型"""
    credits: int = Field(default=0, description="总积分")
    ext_credits_1: int = Field(default=0, description="金币")
    ext_credits_2: int = Field(default=0, description="威望")
    ext_credits_3: int = Field(default=0, description="贡献")
    ext_credits_4: int = Field(default=0, description="鲜花")


class UserPointsResponse(UserPointsBase):
    """用户积分响应模型"""
    id: int
    user_id: int
    posts: int
    comments: int
    diggs: int
    onlinetime: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PointsLogCreate(BaseModel):
    """积分日志创建模型"""
    user_id: int
    operation: str = Field(..., description="操作类型")
    related_id: Optional[int] = Field(None, description="关联ID")
    amount: int = Field(..., description="变动数量")
    description: Optional[str] = Field(None, description="描述")


class PointsLogResponse(BaseModel):
    """积分日志响应模型"""
    id: int
    user_id: int
    operation: str
    related_id: Optional[int]
    amount: int
    balance: int
    description: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class UserLevelBase(BaseModel):
    """用户等级基础模型"""
    level: int = Field(..., description="等级")
    name: str = Field(..., description="等级名称")
    title: str = Field(..., description="等级标题")


class UserLevelCreate(UserLevelBase):
    """用户等级创建模型"""
    description: Optional[str] = Field(None, description="描述")
    min_credits: int = Field(default=0, description="最低积分")
    max_credits: int = Field(default=0, description="最高积分")
    icon: Optional[str] = Field(None, description="图标")
    color: Optional[str] = Field(None, description="颜色")
    stars: int = Field(default=0, description="星星数")


class UserLevelResponse(UserLevelBase):
    """用户等级响应模型"""
    id: int
    description: Optional[str]
    min_credits: int
    max_credits: int
    icon: Optional[str]
    color: Optional[str]
    stars: int
    created_at: datetime

    class Config:
        from_attributes = True
