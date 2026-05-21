"""
动态菜单系统
SCALE OS v10.0

支持插件注册菜单、多租户菜单配置
"""

from datetime import datetime
from typing import Optional, List

from sqlalchemy import String, Integer, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Menu(Base):
    """菜单表"""
    __tablename__ = "menus"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    
    # 基本信息
    name: Mapped[str] = mapped_column(String(100), nullable=False, comment="菜单名称")
    identifier: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, comment="菜单标识")
    icon: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, comment="图标")
    path: Mapped[Optional[str]] = mapped_column(String(200), nullable=True, comment="路径/路由")
    
    # 层级结构
    parent_id: Mapped[Optional[int]] = mapped_column(ForeignKey("menus.id"), nullable=True, comment="父菜单ID")
    level: Mapped[int] = mapped_column(Integer, default=0, comment="层级 0/1/2")
    sort: Mapped[int] = mapped_column(Integer, default=0, comment="排序")
    
    # 类型
    type: Mapped[str] = mapped_column(String(20), default="link", comment="类型: link/click/group")
    target: Mapped[str] = mapped_column(String(20), default="_self", comment="打开方式: _self/_blank")
    
    # 权限
    permission: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, comment="权限标识")
    is_public: Mapped[bool] = mapped_column(Boolean, default=True, comment="是否公开")
    
    # 来源（系统/插件）
    source: Mapped[str] = mapped_column(String(50), default="system", comment="来源: system/addon标识")
    
    # 状态
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, comment="是否启用")
    
    # 租户（null 表示全局菜单）
    tenant_id: Mapped[Optional[int]] = mapped_column(ForeignKey("tenants.id"), nullable=True, comment="租户ID")
    
    # 扩展配置
    config: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="扩展配置JSON")
    
    # 时间
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    parent: Mapped[Optional["Menu"]] = relationship("Menu", remote_side=[id], back_populates="children")
    children: Mapped[List["Menu"]] = relationship("Menu", back_populates="parent", order_by="Menu.sort")
    
    def __repr__(self) -> str:
        return f"<Menu {self.identifier}>"


class MenuItem(Base):
    """菜单项（用于复杂菜单结构）"""
    __tablename__ = "menu_items"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    menu_id: Mapped[int] = mapped_column(ForeignKey("menus.id"), nullable=False)
    
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    icon: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    path: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    sort: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    menu: Mapped["Menu"] = relationship("Menu")
    
    def __repr__(self) -> str:
        return f"<MenuItem {self.name}>"


class UserMenu(Base):
    """用户自定义菜单"""
    __tablename__ = "user_menus"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    menu_id: Mapped[int] = mapped_column(ForeignKey("menus.id"), nullable=False)
    
    is_visible: Mapped[bool] = mapped_column(Boolean, default=True, comment="是否显示")
    sort: Mapped[int] = mapped_column(Integer, default=0, comment="自定义排序")
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    user: Mapped["User"] = relationship("User")
    menu: Mapped["Menu"] = relationship("Menu")
    
    def __repr__(self) -> str:
        return f"<UserMenu user={self.user_id} menu={self.menu_id}>"
