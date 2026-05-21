"""
菜单路由
SCALE OS v10.0
"""

from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query

from app.database import get_db
from app.schemas.menu import (
    MenuCreate, MenuUpdate, MenuResponse, MenuTreeResponse,
    UserMenuResponse
)
from app.services.menu import MenuService
from app.routers.users import get_current_user, UserResponse

router = APIRouter()


@router.post("/", response_model=MenuResponse, status_code=status.HTTP_201_CREATED)
async def create_menu(
    data: MenuCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user)],
):
    """创建菜单"""
    service = MenuService(db)
    
    # 检查标识是否已存在
    existing = await service.get_by_identifier(data.identifier)
    if existing:
        raise HTTPException(status_code=400, detail="菜单标识已存在")
    
    menu = await service.create(
        name=data.name,
        identifier=data.identifier,
        path=data.path,
        icon=data.icon,
        parent_id=data.parent_id,
        sort=data.sort,
        type=data.type,
        target=data.target,
        permission=data.permission,
        is_public=data.is_public,
        source=data.source,
        config=data.config,
    )
    
    return menu


@router.get("/tree", response_model=list[MenuTreeResponse])
async def get_menu_tree(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user)],
    tenant_id: Optional[int] = None,
    is_public: Optional[bool] = None,
):
    """获取菜单树"""
    service = MenuService(db)
    menus = await service.get_tree(tenant_id=tenant_id, is_public=is_public)
    return menus


@router.get("/my", response_model=list[MenuTreeResponse])
async def get_my_menus(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user)],
    tenant_id: Optional[int] = None,
):
    """获取当前用户可见菜单"""
    service = MenuService(db)
    menus = await service.get_user_menus(current_user.id, tenant_id=tenant_id)
    return menus


@router.get("/", response_model=dict)
async def list_menus(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user)],
    source: Optional[str] = None,
    tenant_id: Optional[int] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
):
    """获取菜单列表"""
    service = MenuService(db)
    menus, total = await service.list(
        source=source,
        tenant_id=tenant_id,
        skip=skip,
        limit=limit
    )
    
    return {
        "total": total,
        "items": [MenuResponse.model_validate(m) for m in menus],
    }


@router.get("/{menu_id}", response_model=MenuResponse)
async def get_menu(
    menu_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user)],
):
    """获取菜单详情"""
    service = MenuService(db)
    menu = await service.get(menu_id)
    
    if not menu:
        raise HTTPException(status_code=404, detail="菜单不存在")
    
    return menu


@router.put("/{menu_id}", response_model=MenuResponse)
async def update_menu(
    menu_id: int,
    data: MenuUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user)],
):
    """更新菜单"""
    service = MenuService(db)
    updated = await service.update(menu_id, **data.model_dump(exclude_unset=True))
    
    if not updated:
        raise HTTPException(status_code=404, detail="菜单不存在")
    
    return updated


@router.delete("/{menu_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_menu(
    menu_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user)],
):
    """删除菜单"""
    service = MenuService(db)
    success = await service.delete(menu_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="菜单不存在")


# ============ 用户菜单 ============

@router.post("/{menu_id}/user", response_model=UserMenuResponse)
async def set_user_menu(
    menu_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user)],
    is_visible: bool = Query(True),
    sort: int = Query(0),
):
    """设置用户菜单"""
    service = MenuService(db)
    user_menu = await service.set_user_menu(
        user_id=current_user.id,
        menu_id=menu_id,
        is_visible=is_visible,
        sort=sort
    )
    return user_menu


@router.delete("/{menu_id}/user", status_code=status.HTTP_204_NO_CONTENT)
async def remove_user_menu(
    menu_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user)],
):
    """移除用户菜单"""
    service = MenuService(db)
    await service.remove_user_menu(current_user.id, menu_id)
