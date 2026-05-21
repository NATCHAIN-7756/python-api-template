"""
租户路由
SCALE OS v10.0
"""

from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query

from app.database import get_db
from app.models.tenant import TenantContext
from app.schemas.tenant import (
    TenantCreate, TenantUpdate, TenantResponse, TenantDetailResponse,
    TenantAddonResponse, TenantUserResponse
)
from app.services.tenant import TenantService
from app.routers.users import get_current_user, UserResponse

router = APIRouter()


@router.post("/", response_model=TenantResponse, status_code=status.HTTP_201_CREATED)
async def create_tenant(
    data: TenantCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user)],
):
    """创建租户"""
    service = TenantService(db)
    
    # 检查标识是否已存在
    existing = await service.get_by_identifier(data.identifier)
    if existing:
        raise HTTPException(status_code=400, detail="租户标识已存在")
    
    tenant = await service.create(
        name=data.name,
        identifier=data.identifier,
        owner_id=current_user.id,
        type=data.type,
        appid=data.appid,
        appsecret=data.appsecret,
        token=data.token,
        config=data.config,
    )
    
    return tenant


@router.get("/", response_model=dict)
async def list_tenants(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user)],
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
):
    """获取租户列表"""
    service = TenantService(db)
    tenants, total = await service.list(owner_id=current_user.id, skip=skip, limit=limit)
    
    return {
        "total": total,
        "items": [TenantResponse.model_validate(t) for t in tenants],
    }


@router.get("/{tenant_id}", response_model=TenantDetailResponse)
async def get_tenant(
    tenant_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user)],
):
    """获取租户详情"""
    service = TenantService(db)
    tenant = await service.get(tenant_id)
    
    if not tenant:
        raise HTTPException(status_code=404, detail="租户不存在")
    
    # 检查权限
    if tenant.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权访问此租户")
    
    return tenant


@router.put("/{tenant_id}", response_model=TenantResponse)
async def update_tenant(
    tenant_id: int,
    data: TenantUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user)],
):
    """更新租户"""
    service = TenantService(db)
    tenant = await service.get(tenant_id)
    
    if not tenant:
        raise HTTPException(status_code=404, detail="租户不存在")
    
    if tenant.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权修改此租户")
    
    updated = await service.update(tenant_id, **data.model_dump(exclude_unset=True))
    return updated


@router.delete("/{tenant_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tenant(
    tenant_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user)],
):
    """删除租户"""
    service = TenantService(db)
    tenant = await service.get(tenant_id)
    
    if not tenant:
        raise HTTPException(status_code=404, detail="租户不存在")
    
    if tenant.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权删除此租户")
    
    await service.delete(tenant_id)


# ============ 租户插件管理 ============

@router.post("/{tenant_id}/addons/{addon_identifier}", response_model=TenantAddonResponse)
async def enable_addon(
    tenant_id: int,
    addon_identifier: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user)],
):
    """为租户启用插件"""
    service = TenantService(db)
    tenant = await service.get(tenant_id)
    
    if not tenant:
        raise HTTPException(status_code=404, detail="租户不存在")
    
    if tenant.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权操作")
    
    tenant_addon = await service.enable_addon(tenant_id, addon_identifier)
    return tenant_addon


@router.delete("/{tenant_id}/addons/{addon_identifier}", status_code=status.HTTP_204_NO_CONTENT)
async def disable_addon(
    tenant_id: int,
    addon_identifier: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user)],
):
    """为租户禁用插件"""
    service = TenantService(db)
    tenant = await service.get(tenant_id)
    
    if not tenant:
        raise HTTPException(status_code=404, detail="租户不存在")
    
    if tenant.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权操作")
    
    await service.disable_addon(tenant_id, addon_identifier)


@router.get("/{tenant_id}/addons", response_model=list[TenantAddonResponse])
async def get_tenant_addons(
    tenant_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user)],
):
    """获取租户已启用的插件"""
    service = TenantService(db)
    tenant = await service.get(tenant_id)
    
    if not tenant:
        raise HTTPException(status_code=404, detail="租户不存在")
    
    if tenant.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权访问")
    
    addons = await service.get_addons(tenant_id)
    return addons


# ============ 租户用户管理 ============

@router.post("/{tenant_id}/users/{user_id}", response_model=TenantUserResponse)
async def add_tenant_user(
    tenant_id: int,
    user_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user)],
    role: str = Query("member", pattern="^(admin|member)$"),
):
    """添加租户用户"""
    service = TenantService(db)
    tenant = await service.get(tenant_id)
    
    if not tenant:
        raise HTTPException(status_code=404, detail="租户不存在")
    
    if tenant.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权操作")
    
    tenant_user = await service.add_user(tenant_id, user_id, role)
    return tenant_user


@router.delete("/{tenant_id}/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_tenant_user(
    tenant_id: int,
    user_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user)],
):
    """移除租户用户"""
    service = TenantService(db)
    tenant = await service.get(tenant_id)
    
    if not tenant:
        raise HTTPException(status_code=404, detail="租户不存在")
    
    if tenant.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权操作")
    
    await service.remove_user(tenant_id, user_id)


@router.get("/{tenant_id}/users", response_model=list[TenantUserResponse])
async def get_tenant_users(
    tenant_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user)],
):
    """获取租户用户列表"""
    service = TenantService(db)
    tenant = await service.get(tenant_id)
    
    if not tenant:
        raise HTTPException(status_code=404, detail="租户不存在")
    
    if tenant.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权访问")
    
    users = await service.get_users(tenant_id)
    return users
