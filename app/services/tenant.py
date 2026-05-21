"""
租户服务
SCALE OS v10.0
"""

from typing import Optional, List
from datetime import datetime
import json

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.tenant import (
    Tenant, TenantConfig, TenantAddon, TenantUser, TenantDomain,
    TenantContext
)
from app.core.hook import hooks


class TenantService:
    """租户服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(
        self,
        name: str,
        identifier: str,
        owner_id: int,
        type: str = "website",
        **kwargs
    ) -> Tenant:
        """创建租户"""
        tenant = Tenant(
            name=name,
            identifier=identifier,
            owner_id=owner_id,
            type=type,
            appid=kwargs.get("appid"),
            appsecret=kwargs.get("appsecret"),
            token=kwargs.get("token"),
            config=json.dumps(kwargs.get("config", {})) if kwargs.get("config") else None,
        )
        
        self.db.add(tenant)
        await self.db.flush()
        
        # 创建所有者关联
        tenant_user = TenantUser(
            tenant_id=tenant.id,
            user_id=owner_id,
            role="owner",
        )
        self.db.add(tenant_user)
        
        # 触发事件
        hooks.emit("tenant.create", {"tenant_id": tenant.id, "identifier": identifier})
        
        return tenant
    
    async def get(self, tenant_id: int) -> Optional[Tenant]:
        """获取租户"""
        result = await self.db.execute(
            select(Tenant).where(Tenant.id == tenant_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_identifier(self, identifier: str) -> Optional[Tenant]:
        """根据标识获取租户"""
        result = await self.db.execute(
            select(Tenant).where(Tenant.identifier == identifier)
        )
        return result.scalar_one_or_none()
    
    async def get_by_domain(self, domain: str) -> Optional[Tenant]:
        """根据域名获取租户"""
        result = await self.db.execute(
            select(TenantDomain).where(
                and_(
                    TenantDomain.domain == domain,
                    TenantDomain.is_verified == True
                )
            )
        )
        tenant_domain = result.scalar_one_or_none()
        
        if tenant_domain:
            return await self.get(tenant_domain.tenant_id)
        
        return None
    
    async def list(self, owner_id: Optional[int] = None, skip: int = 0, 
                   limit: int = 20) -> tuple[List[Tenant], int]:
        """获取租户列表"""
        query = select(Tenant)
        
        if owner_id:
            query = query.where(Tenant.owner_id == owner_id)
        
        # 计数
        from sqlalchemy import func
        count_query = select(func.count()).select_from(query.subquery())
        count_result = await self.db.execute(count_query)
        total = count_result.scalar() or 0
        
        # 查询
        query = query.offset(skip).limit(limit).order_by(Tenant.created_at.desc())
        result = await self.db.execute(query)
        tenants = list(result.scalars().all())
        
        return tenants, total
    
    async def update(self, tenant_id: int, **kwargs) -> Optional[Tenant]:
        """更新租户"""
        tenant = await self.get(tenant_id)
        if not tenant:
            return None
        
        for key, value in kwargs.items():
            if hasattr(tenant, key) and key not in ["id", "identifier"]:
                if key == "config" and isinstance(value, dict):
                    value = json.dumps(value)
                setattr(tenant, key, value)
        
        await self.db.flush()
        return tenant
    
    async def delete(self, tenant_id: int) -> bool:
        """删除租户"""
        tenant = await self.get(tenant_id)
        if not tenant:
            return False
        
        await self.db.delete(tenant)
        await self.db.flush()
        
        hooks.emit("tenant.delete", {"tenant_id": tenant_id})
        
        return True
    
    # ============ 租户配置 ============
    
    async def get_config(self, tenant_id: int, key: str) -> Optional[str]:
        """获取租户配置"""
        result = await self.db.execute(
            select(TenantConfig).where(
                and_(
                    TenantConfig.tenant_id == tenant_id,
                    TenantConfig.key == key
                )
            )
        )
        config = result.scalar_one_or_none()
        return config.value if config else None
    
    async def set_config(self, tenant_id: int, key: str, value: str, 
                         type: str = "string") -> TenantConfig:
        """设置租户配置"""
        result = await self.db.execute(
            select(TenantConfig).where(
                and_(
                    TenantConfig.tenant_id == tenant_id,
                    TenantConfig.key == key
                )
            )
        )
        config = result.scalar_one_or_none()
        
        if config:
            config.value = value
            config.type = type
        else:
            config = TenantConfig(
                tenant_id=tenant_id,
                key=key,
                value=value,
                type=type
            )
            self.db.add(config)
        
        await self.db.flush()
        return config
    
    # ============ 租户插件 ============
    
    async def enable_addon(self, tenant_id: int, addon_identifier: str, 
                           config: Optional[dict] = None) -> TenantAddon:
        """为租户启用插件"""
        result = await self.db.execute(
            select(TenantAddon).where(
                and_(
                    TenantAddon.tenant_id == tenant_id,
                    TenantAddon.addon_identifier == addon_identifier
                )
            )
        )
        tenant_addon = result.scalar_one_or_none()
        
        if tenant_addon:
            tenant_addon.is_enabled = True
            if config:
                tenant_addon.config = json.dumps(config)
        else:
            tenant_addon = TenantAddon(
                tenant_id=tenant_id,
                addon_identifier=addon_identifier,
                is_enabled=True,
                config=json.dumps(config) if config else None
            )
            self.db.add(tenant_addon)
        
        await self.db.flush()
        
        hooks.emit("tenant.addon.enable", {
            "tenant_id": tenant_id,
            "addon_identifier": addon_identifier
        })
        
        return tenant_addon
    
    async def disable_addon(self, tenant_id: int, addon_identifier: str) -> bool:
        """为租户禁用插件"""
        result = await self.db.execute(
            select(TenantAddon).where(
                and_(
                    TenantAddon.tenant_id == tenant_id,
                    TenantAddon.addon_identifier == addon_identifier
                )
            )
        )
        tenant_addon = result.scalar_one_or_none()
        
        if tenant_addon:
            tenant_addon.is_enabled = False
            await self.db.flush()
            
            hooks.emit("tenant.addon.disable", {
                "tenant_id": tenant_id,
                "addon_identifier": addon_identifier
            })
            
            return True
        
        return False
    
    async def get_addons(self, tenant_id: int) -> List[TenantAddon]:
        """获取租户已启用的插件"""
        result = await self.db.execute(
            select(TenantAddon).where(
                and_(
                    TenantAddon.tenant_id == tenant_id,
                    TenantAddon.is_enabled == True
                )
            )
        )
        return list(result.scalars().all())
    
    # ============ 租户用户 ============
    
    async def add_user(self, tenant_id: int, user_id: int, 
                       role: str = "member", permissions: Optional[List[str]] = None) -> TenantUser:
        """添加租户用户"""
        tenant_user = TenantUser(
            tenant_id=tenant_id,
            user_id=user_id,
            role=role,
            permissions=json.dumps(permissions) if permissions else None
        )
        self.db.add(tenant_user)
        await self.db.flush()
        
        return tenant_user
    
    async def remove_user(self, tenant_id: int, user_id: int) -> bool:
        """移除租户用户"""
        result = await self.db.execute(
            select(TenantUser).where(
                and_(
                    TenantUser.tenant_id == tenant_id,
                    TenantUser.user_id == user_id
                )
            )
        )
        tenant_user = result.scalar_one_or_none()
        
        if tenant_user and tenant_user.role != "owner":
            await self.db.delete(tenant_user)
            await self.db.flush()
            return True
        
        return False
    
    async def get_users(self, tenant_id: int) -> List[TenantUser]:
        """获取租户用户列表"""
        result = await self.db.execute(
            select(TenantUser).where(TenantUser.tenant_id == tenant_id)
        )
        return list(result.scalars().all())
    
    # ============ 租户域名 ============
    
    async def add_domain(self, tenant_id: int, domain: str, 
                         is_primary: bool = False) -> TenantDomain:
        """添加租户域名"""
        tenant_domain = TenantDomain(
            tenant_id=tenant_id,
            domain=domain,
            is_primary=is_primary
        )
        self.db.add(tenant_domain)
        await self.db.flush()
        
        return tenant_domain
    
    async def verify_domain(self, domain: str) -> bool:
        """验证域名"""
        result = await self.db.execute(
            select(TenantDomain).where(TenantDomain.domain == domain)
        )
        tenant_domain = result.scalar_one_or_none()
        
        if tenant_domain:
            tenant_domain.is_verified = True
            await self.db.flush()
            return True
        
        return False
