"""
日志路由
SCALE OS v10.0
"""

from typing import Annotated, Optional
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status, Query

from app.database import get_db
from app.schemas.log import (
    LogResponse, AuditLogResponse, RequestLogResponse,
    LogStatsResponse
)
from app.services.log import LogService
from app.routers.users import get_current_user, UserResponse

router = APIRouter()


@router.get("/", response_model=dict)
async def list_logs(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user)],
    level: Optional[int] = Query(None, ge=10, le=50),
    type: Optional[str] = None,
    source: Optional[str] = None,
    user_id: Optional[int] = None,
    tenant_id: Optional[int] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
):
    """获取日志列表（管理员）"""
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="需要管理员权限")
    
    service = LogService(db)
    logs, total = await service.list(
        level=level,
        type=type,
        source=source,
        user_id=user_id,
        tenant_id=tenant_id,
        start_time=start_time,
        end_time=end_time,
        skip=skip,
        limit=limit,
    )
    
    return {
        "total": total,
        "items": [LogResponse.model_validate(log) for log in logs],
    }


@router.get("/stats", response_model=LogStatsResponse)
async def get_log_stats(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user)],
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    tenant_id: Optional[int] = None,
):
    """获取日志统计（管理员）"""
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="需要管理员权限")
    
    service = LogService(db)
    stats = await service.get_stats(
        start_time=start_time,
        end_time=end_time,
        tenant_id=tenant_id,
    )
    
    return stats


@router.get("/my", response_model=dict)
async def get_my_logs(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user)],
    level: Optional[int] = Query(None, ge=10, le=50),
    type: Optional[str] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
):
    """获取当前用户的日志"""
    service = LogService(db)
    logs, total = await service.list(
        level=level,
        type=type,
        user_id=current_user.id,
        start_time=start_time,
        end_time=end_time,
        skip=skip,
        limit=limit,
    )
    
    return {
        "total": total,
        "items": [LogResponse.model_validate(log) for log in logs],
    }


@router.get("/{log_id}", response_model=LogResponse)
async def get_log(
    log_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user)],
):
    """获取日志详情"""
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="需要管理员权限")
    
    service = LogService(db)
    logs, _ = await service.list(skip=0, limit=1)
    
    # 直接查询
    from sqlalchemy import select
    from app.models.log import Log
    
    result = await db.execute(select(Log).where(Log.id == log_id))
    log = result.scalar_one_or_none()
    
    if not log:
        raise HTTPException(status_code=404, detail="日志不存在")
    
    return log


@router.delete("/clean", response_model=dict)
async def clean_old_logs(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user)],
    days: int = Query(30, ge=1, le=365),
):
    """清理旧日志（管理员）"""
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="需要管理员权限")
    
    service = LogService(db)
    count = await service.clean_old_logs(days=days)
    
    return {"message": f"已清理 {count} 条日志", "deleted_count": count}
