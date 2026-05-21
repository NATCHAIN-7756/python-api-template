"""
用户组 Schemas
SCALE OS v10.0
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class UserGroupBase(BaseModel):
    """用户组基础模型"""
    name: str = Field(..., min_length=2, max_length=50, description="用户组名称")
    title: str = Field(..., min_length=2, max_length=100, description="显示标题")
    description: Optional[str] = Field(None, description="描述")
    type: str = Field(default="user", description="类型")


class UserGroupCreate(UserGroupBase):
    """用户组创建模型"""
    min_credits: int = Field(default=0, description="最低积分")
    max_credits: int = Field(default=0, description="最高积分")
    is_admin: bool = Field(default=False, description="是否管理员")
    color: Optional[str] = Field(None, description="颜色")
    icon: Optional[str] = Field(None, description="图标")
    stars: int = Field(default=0, description="星星数")


class UserGroupUpdate(BaseModel):
    """用户组更新模型"""
    name: Optional[str] = Field(None, min_length=2, max_length=50)
    title: Optional[str] = Field(None, min_length=2, max_length=100)
    description: Optional[str] = None
    type: Optional[str] = None
    min_credits: Optional[int] = None
    max_credits: Optional[int] = None
    is_admin: Optional[bool] = None
    is_super_admin: Optional[bool] = None
    allow_visit: Optional[bool] = None
    allow_post: Optional[bool] = None
    allow_reply: Optional[bool] = None
    color: Optional[str] = None
    icon: Optional[str] = None
    stars: Optional[int] = None


class UserGroupResponse(UserGroupBase):
    """用户组响应模型"""
    id: int
    min_credits: int
    max_credits: int
    is_admin: bool
    is_super_admin: bool
    allow_visit: bool
    allow_post: bool
    allow_reply: bool
    color: Optional[str]
    icon: Optional[str]
    stars: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PermissionBase(BaseModel):
    """权限基础模型"""
    name: str = Field(..., description="权限名称")
    code: str = Field(..., description="权限代码")
    description: Optional[str] = Field(None, description="描述")
    module: str = Field(default="system", description="所属模块")


class PermissionCreate(PermissionBase):
    """权限创建模型"""
    pass


class PermissionResponse(PermissionBase):
    """权限响应模型"""
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
