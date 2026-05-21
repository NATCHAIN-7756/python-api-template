"""
分类/版块模型
SCALE OS v10.0
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import String, Integer, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Category(Base):
    """分类/版块表"""
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    
    # 基本信息
    name: Mapped[str] = mapped_column(String(100), nullable=False, comment="分类名称")
    slug: Mapped[str] = mapped_column(String(100), unique=True, index=True, comment="URL别名")
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="描述")
    
    # 层级结构
    parent_id: Mapped[Optional[int]] = mapped_column(ForeignKey("categories.id"), nullable=True, comment="父分类ID")
    level: Mapped[int] = mapped_column(Integer, default=1, comment="层级")
    sort_order: Mapped[int] = mapped_column(Integer, default=0, comment="排序")
    
    # 显示设置
    icon: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, comment="图标")
    cover: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, comment="封面")
    color: Mapped[Optional[str]] = mapped_column(String(20), nullable=True, comment="颜色")
    
    # 权限设置
    is_public: Mapped[bool] = mapped_column(Boolean, default=True, comment="是否公开")
    allow_post: Mapped[bool] = mapped_column(Boolean, default=True, comment="允许发帖")
    allow_reply: Mapped[bool] = mapped_column(Boolean, default=True, comment="允许回复")
    allow_upload: Mapped[bool] = mapped_column(Boolean, default=True, comment="允许上传")
    
    # 需要权限
    min_credits_to_view: Mapped[int] = mapped_column(Integer, default=0, comment="查看所需积分")
    min_credits_to_post: Mapped[int] = mapped_column(Integer, default=0, comment="发帖所需积分")
    
    # 统计
    posts_count: Mapped[int] = mapped_column(Integer, default=0, comment="帖子数")
    comments_count: Mapped[int] = mapped_column(Integer, default=0, comment="评论数")
    
    # 状态
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, comment="是否启用")
    
    # 时间
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联
    parent: Mapped[Optional["Category"]] = relationship("Category", remote_side=[id], back_populates="children")
    children: Mapped[list["Category"]] = relationship("Category", back_populates="parent")
    posts: Mapped[list["Post"]] = relationship("Post", back_populates="category")

    def __repr__(self) -> str:
        return f"<Category {self.name}>"