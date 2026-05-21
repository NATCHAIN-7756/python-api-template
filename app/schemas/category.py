"""
分类 Schemas
SCALE OS v10.0
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class CategoryBase(BaseModel):
    """分类基础模型"""
    name: str = Field(..., min_length=2, max_length=100, description="分类名称")
    slug: str = Field(..., min_length=2, max_length=100, description="URL别名")
    description: Optional[str] = Field(None, description="描述")


class CategoryCreate(CategoryBase):
    """分类创建模型"""
    parent_id: Optional[int] = Field(None, description="父分类ID")
    icon: Optional[str] = Field(None, description="图标")
    cover: Optional[str] = Field(None, description="封面")
    color: Optional[str] = Field(None, description="颜色")
    sort_order: int = Field(default=0, description="排序")
    is_public: bool = Field(default=True, description="是否公开")
    allow_post: bool = Field(default=True, description="允许发帖")
    allow_reply: bool = Field(default=True, description="允许回复")


class CategoryUpdate(BaseModel):
    """分类更新模型"""
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    slug: Optional[str] = Field(None, min_length=2, max_length=100)
    description: Optional[str] = None
    parent_id: Optional[int] = None
    icon: Optional[str] = None
    cover: Optional[str] = None
    color: Optional[str] = None
    sort_order: Optional[int] = None
    is_public: Optional[bool] = None
    allow_post: Optional[bool] = None
    allow_reply: Optional[bool] = None
    is_active: Optional[bool] = None


class CategoryResponse(CategoryBase):
    """分类响应模型"""
    id: int
    parent_id: Optional[int]
    level: int
    sort_order: int
    icon: Optional[str]
    cover: Optional[str]
    color: Optional[str]
    is_public: bool
    allow_post: bool
    allow_reply: bool
    posts_count: int
    comments_count: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CategoryTreeResponse(CategoryResponse):
    """分类树响应模型"""
    children: list["CategoryTreeResponse"] = []


class CategorySimple(BaseModel):
    """分类简单模型"""
    id: int
    name: str
    slug: str

    class Config:
        from_attributes = True