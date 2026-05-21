"""
私信/通知路由
SCALE OS v10.0
"""

from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query

from app.database import get_db
from app.schemas.message import (
    MessageCreate, MessageResponse, MessageListResponse,
    NotificationResponse, NotificationListResponse
)
from app.services.message import MessageService, NotificationService
from app.services.user import UserService
from app.routers.users import get_current_user, UserResponse

router = APIRouter()


@router.post("/message", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def send_message(
    message_in: MessageCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user)],
):
    """发送私信"""
    user_service = UserService(db)
    user = await user_service.get_by_id(message_in.receiver_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="用户不存在")

    service = MessageService(db)
    message = await service.create(current_user.id, message_in)
    return MessageResponse.model_validate(message)


@router.get("/messages/{user_id}", response_model=MessageListResponse)
async def get_conversation(
    user_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user)],
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
):
    """获取对话记录"""
    service = MessageService(db)
    messages, total = await service.get_conversation(current_user.id, user_id, skip, limit)
    return MessageListResponse(total=total, items=[MessageResponse.model_validate(m) for m in messages])


@router.post("/messages/read", status_code=status.HTTP_204_NO_CONTENT)
async def mark_messages_read(
    message_ids: list[int],
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user)],
):
    """标记消息已读"""
    service = MessageService(db)
    await service.mark_read(current_user.id, message_ids)


@router.get("/messages/unread")
async def get_unread_count(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user)],
):
    """获取未读消息数"""
    service = MessageService(db)
    count = await service.get_unread_count(current_user.id)
    return {"unread": count}


@router.get("/notifications", response_model=NotificationListResponse)
async def get_notifications(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user)],
    notification_type: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
):
    """获取通知列表"""
    service = NotificationService(db)
    notifications, total, unread = await service.get_list(current_user.id, notification_type, skip, limit)
    return NotificationListResponse(
        total=total,
        unread=unread,
        items=[NotificationResponse.model_validate(n) for n in notifications],
    )


@router.post("/notifications/read", status_code=status.HTTP_204_NO_CONTENT)
async def mark_notifications_read(
    notification_ids: list[int],
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user)],
):
    """标记通知已读"""
    service = NotificationService(db)
    await service.mark_read(current_user.id, notification_ids)


@router.post("/notifications/read-all", status_code=status.HTTP_204_NO_CONTENT)
async def mark_all_notifications_read(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user)],
):
    """全部标记已读"""
    service = NotificationService(db)
    await service.mark_all_read(current_user.id)