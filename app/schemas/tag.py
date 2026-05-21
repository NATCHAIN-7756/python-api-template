"""
标签 Schemas
SCALE OS v10.0
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class TagBase(BaseModel):
    """标签基础模型"""
    name: str = Field(..., min_length=1, max_length=50, description="标签名称")
    slug: str = Field(..., min_length=1, max_length=50, description="URL别名")


class TagCreate(TagBase):
    """标签创建模型"""
    description: Optional[str] = Field(None, max_length=200, description="描述")
    color: Optional[str] = Field(None, description="颜色")
    icon: Optional[str] = Field(None, description="图标")


class TagUpdate(BaseModel):
    """标签更新模型"""
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    slug: Optional[str] = Field(None, min_length=1, max_length=50)
    description: Optional[str] = Field(None, max_length=200)
    color: Optional[str] = None
    icon: Optional[str] = None
    is_hot: Optional[bool] = None


class TagResponse(TagBase):
    """标签响应模型"""
    id: int
    description: Optional[str]
    color: Optional[str]
    icon: Optional[str]
    posts_count: int
    is_hot: bool
    created_at: datetime

    class Config:
        from_attributes = True


class TagSimple(BaseModel):
    """标签简单模型"""
    id: int
    name: str
    slug: str

    class Config:
        from_attributes = True