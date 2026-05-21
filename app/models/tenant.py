"""
多租户系统
SCALE OS v10.0

类似微擎的多公众号/小程序管理
"""

from datetime import datetime
from typing import Optional, List
from enum import Enum

from sqlalchemy import String, Integer, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class TenantType(Enum):
    """租户类型"""
    PUBLIC_ACCOUNT = "public_account"    # 公众号
    MINI_PROGRAM = "mini_program"        # 小程序
    ENTERPRISE_WECHAT = "enterprise_wechat"  # 企业微信
    WEBSITE = "website"                  # 网站
    APP = "app"                          # APP
    OTHER = "other"                      # 其他


class Tenant(Base):
    """租户模型"""
    __tablename__ = "tenants"
    __table_args__ = (
        # 索引
    )
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, comment="租户名称")
    identifier: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, comment="租户标识")
    type: Mapped[str] = mapped_column(String(20), default="website", comment="租户类型")
    
    # 配置信息
    config: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="租户配置JSON")
    
    # 微信相关
    appid: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, comment="AppID")
    appsecret: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, comment="AppSecret")
    token: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, comment="Token")
    encoding_aes_key: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, comment="EncodingAESKey")
    
    # 状态
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, comment="是否激活")
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, comment="是否验证")
    
    # 所属用户
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, comment="所属用户")
    
    # 时间
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, comment="过期时间")
    
    # 关系
    owner: Mapped["User"] = relationship("User", back_populates="tenants")
    
    def __repr__(self) -> str:
        return f"<Tenant {self.identifier}>"


class TenantConfig(Base):
    """租户配置项"""
    __tablename__ = "tenant_configs"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id"), nullable=False)
    key: Mapped[str] = mapped_column(String(100), nullable=False, comment="配置键")
    value: Mapped[str] = mapped_column(Text, nullable=True, comment="配置值")
    type: Mapped[str] = mapped_column(String(20), default="string", comment="值类型")
    
    tenant: Mapped["Tenant"] = relationship("Tenant")
    
    def __repr__(self) -> str:
        return f"<TenantConfig {self.key}>"


class TenantAddon(Base):
    """租户-插件关联"""
    __tablename__ = "tenant_addons"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id"), nullable=False)
    addon_identifier: Mapped[str] = mapped_column(String(50), nullable=False, comment="插件标识")
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True, comment="是否启用")
    config: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="插件配置")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    tenant: Mapped["Tenant"] = relationship("Tenant")
    
    def __repr__(self) -> str:
        return f"<TenantAddon tenant={self.tenant_id} addon={self.addon_identifier}>"


class TenantUser(Base):
    """租户-用户关联（多用户管理）"""
    __tablename__ = "tenant_users"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    role: Mapped[str] = mapped_column(String(20), default="member", comment="角色: owner/admin/member")
    permissions: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="权限列表JSON")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    tenant: Mapped["Tenant"] = relationship("Tenant")
    user: Mapped["User"] = relationship("User")
    
    def __repr__(self) -> str:
        return f"<TenantUser tenant={self.tenant_id} user={self.user_id}>"


class TenantDomain(Base):
    """租户域名绑定"""
    __tablename__ = "tenant_domains"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id"), nullable=False)
    domain: Mapped[str] = mapped_column(String(200), unique=True, nullable=False, comment="域名")
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False, comment="是否主域名")
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, comment="是否验证")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    tenant: Mapped["Tenant"] = relationship("Tenant")
    
    def __repr__(self) -> str:
        return f"<TenantDomain {self.domain}>"


# ============ 租户上下文管理 ============

class TenantContext:
    """租户上下文（请求级别）"""
    
    _current_tenant: Optional[Tenant] = None
    
    @classmethod
    def set(cls, tenant: Optional[Tenant]):
        """设置当前租户"""
        cls._current_tenant = tenant
    
    @classmethod
    def get(cls) -> Optional[Tenant]:
        """获取当前租户"""
        return cls._current_tenant
    
    @classmethod
    def clear(cls):
        """清除当前租户"""
        cls._current_tenant = None
    
    @classmethod
    def get_id(cls) -> Optional[int]:
        """获取当前租户ID"""
        if cls._current_tenant:
            return cls._current_tenant.id
        return None