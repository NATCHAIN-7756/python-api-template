"""
菜单 Schemas
SCALE OS v10.0
"""

from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field


class MenuBase(BaseModel):
    """菜单基础"""
    name: str = Field(..., min_length=1, max_length=100)
    identifier: str = Field(..., min_length=1, max_length=50, pattern=r"^[a-z][a-z0-9_]*$")
    icon: Optional[str] = None
    path: Optional[str] = None


class MenuCreate(MenuBase):
    """创建菜单"""
    parent_id: Optional[int] = None
    sort: int = Field(default=0, ge=0)
    type: str = Field(default="link", pattern=r"^(link|click|group)$")
    target: str = Field(default="_self", pattern=r"^(_self|_blank)$")
    permission: Optional[str] = None
    is_public: bool = True
    source: str = "system"
    config: Optional[dict] = None


class MenuUpdate(BaseModel):
    """更新菜单"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    icon: Optional[str] = None
    path: Optional[str] = None
    parent_id: Optional[int] = None
    sort: Optional[int] = Field(None, ge=0)
    type: Optional[str] = Field(None, pattern=r"^(link|click|group)$")
    target: Optional[str] = Field(None, pattern=r"^(_self|_blank)$")
    permission: Optional[str] = None
    is_public: Optional[bool] = None
    is_active: Optional[bool] = None
    config: Optional[dict] = None


class MenuResponse(BaseModel):
    """菜单响应"""
    id: int
    name: str
    identifier: str
    icon: Optional[str] = None
    path: Optional[str] = None
    parent_id: Optional[int] = None
    level: int
    sort: int
    type: str
    target: str
    permission: Optional[str] = None
    is_public: bool
    is_active: bool
    source: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class MenuTreeResponse(MenuResponse):
    """菜单树响应"""
    children: List["MenuTreeResponse"] = []


class MenuItemResponse(BaseModel):
    """菜单项响应"""
    id: int
    name: str
    icon: Optional[str] = None
    path: Optional[str] = None
    sort: int
    is_active: bool
    
    class Config:
        from_attributes = True


class UserMenuResponse(BaseModel):
    """用户菜单响应"""
    id: int
    menu_id: int
    is_visible: bool
    sort: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# 解决循环引用
MenuTreeResponse.model_rebuild()