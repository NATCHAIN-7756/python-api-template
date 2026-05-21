"""
用户组模型
SCALE OS v10.0
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import String, Boolean, Integer, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class UserGroup(Base):
    """用户组表"""
    __tablename__ = "user_groups"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, comment="用户组名称")
    title: Mapped[str] = mapped_column(String(100), nullable=False, comment="显示标题")
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="描述")
    
    # 类型: system=系统组, special=特殊组, user=用户组
    type: Mapped[str] = mapped_column(String(20), default="user", comment="类型")
    
    # 等级相关
    min_credits: Mapped[int] = mapped_column(Integer, default=0, comment="最低积分")
    max_credits: Mapped[int] = mapped_column(Integer, default=0, comment="最高积分")
    
    # 权限相关
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, comment="是否管理员")
    is_super_admin: Mapped[bool] = mapped_column(Boolean, default=False, comment="是否超级管理员")
    allow_visit: Mapped[bool] = mapped_column(Boolean, default=True, comment="允许访问")
    allow_post: Mapped[bool] = mapped_column(Boolean, default=True, comment="允许发帖")
    allow_reply: Mapped[bool] = mapped_column(Boolean, default=True, comment="允许回复")
    allow_upload: Mapped[bool] = mapped_column(Boolean, default=True, comment="允许上传")
    allow_download: Mapped[bool] = mapped_column(Boolean, default=True, comment="允许下载")
    
    # 显示设置
    color: Mapped[Optional[str]] = mapped_column(String(20), nullable=True, comment="用户组颜色")
    icon: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, comment="用户组图标")
    stars: Mapped[int] = mapped_column(Integer, default=0, comment="星星数量")
    
    # 时间
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联用户
    users: Mapped[list["User"]] = relationship("User", back_populates="group")

    def __repr__(self) -> str:
        return f"<UserGroup {self.name}>"
