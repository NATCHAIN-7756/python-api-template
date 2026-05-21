"""
插件管理路由
SCALE OS v10.0
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.database import get_db
from app.core.addon_loader import addon_loader
from app.core.addon import AddonInfo
from app.routers.users import get_current_user, UserResponse

router = APIRouter()


@router.get("/", response_model=list[dict])
async def list_addons(
    current_user: Annotated[UserResponse, Depends(get_current_user)],
):
    """获取插件列表"""
    # 扫描插件
    addons = addon_loader.scan()
    return [a.to_dict() for a in addons]


@router.get("/{identifier}", response_model=dict)
async def get_addon(
    identifier: str,
    current_user: Annotated[UserResponse, Depends(get_current_user)],
):
    """获取插件详情"""
    addon = addon_loader.load(identifier)
    
    if addon is None:
        raise HTTPException(status_code=404, detail="插件不存在")
    
    return {
        **addon.get_manifest(),
        "enabled": addon.enabled,
        "installed": addon.installed,
    }


@router.post("/{identifier}/install", response_model=dict)
async def install_addon(
    identifier: str,
    current_user: Annotated[UserResponse, Depends(get_current_user)],
):
    """安装插件"""
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="需要管理员权限")
    
    success = addon_loader.install(identifier)
    
    if not success:
        raise HTTPException(status_code=400, detail="安装失败")
    
    return {"message": "安装成功", "identifier": identifier}


@router.post("/{identifier}/uninstall", response_model=dict)
async def uninstall_addon(
    identifier: str,
    current_user: Annotated[UserResponse, Depends(get_current_user)],
):
    """卸载插件"""
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="需要管理员权限")
    
    success = addon_loader.uninstall(identifier)
    
    if not success:
        raise HTTPException(status_code=400, detail="卸载失败")
    
    return {"message": "卸载成功", "identifier": identifier}


@router.post("/{identifier}/enable", response_model=dict)
async def enable_addon(
    identifier: str,
    current_user: Annotated[UserResponse, Depends(get_current_user)],
):
    """启用插件"""
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="需要管理员权限")
    
    success = addon_loader.enable(identifier)
    
    if not success:
        raise HTTPException(status_code=400, detail="启用失败")
    
    return {"message": "启用成功", "identifier": identifier}


@router.post("/{identifier}/disable", response_model=dict)
async def disable_addon(
    identifier: str,
    current_user: Annotated[UserResponse, Depends(get_current_user)],
):
    """禁用插件"""
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="需要管理员权限")
    
    success = addon_loader.disable(identifier)
    
    if not success:
        raise HTTPException(status_code=400, detail="禁用失败")
    
    return {"message": "禁用成功", "identifier": identifier}
