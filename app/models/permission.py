"""
权限模型
SCALE OS v10.0
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import String, Boolean, Integer, DateTime, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Permission(Base):
    """权限表"""
    __tablename__ = "permissions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, comment="权限名称")
    code: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, comment="权限代码")
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="描述")
    
    # 分组
    module: Mapped[str] = mapped_column(String(50), default="system", comment="所属模块")
    
    # 时间
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<Permission {self.code}>"


class GroupPermission(Base):
    """用户组权限关联表"""
    __tablename__ = "group_permissions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    group_id: Mapped[int] = mapped_column(ForeignKey("user_groups.id"), nullable=False)
    permission_id: Mapped[int] = mapped_column(ForeignKey("permissions.id"), nullable=False)
    
    # 是否拥有该权限
    is_granted: Mapped[bool] = mapped_column(default=True, comment="是否授权")
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<GroupPermission group={self.group_id} perm={self.permission_id}>"
