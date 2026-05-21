"""
关注/好友路由
SCALE OS v10.0
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.database import get_db
from app.schemas.follow import (
    FollowCreate, FollowResponse, FollowListResponse,
    FriendCreate, FriendUpdate, FriendResponse, FriendListResponse
)
from app.services.follow import FollowService, FriendService
from app.services.user import UserService
from app.routers.users import get_current_user, UserResponse

router = APIRouter()


@router.post("/follow", response_model=FollowResponse)
async def toggle_follow(
    follow_in: FollowCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user)],
):
    """关注/取消关注"""
    # 检查用户
    user_service = UserService(db)
    user = await user_service.get_by_id(follow_in.following_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="用户不存在")

    service = FollowService(db)
    follow, is_following = await service.toggle(current_user.id, follow_in)
    return FollowResponse.model_validate(follow)


@router.get("/followers", response_model=FollowListResponse)
async def get_followers(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user)],
    skip: int = 0,
    limit: int = 50,
):
    """获取粉丝列表"""
    service = FollowService(db)
    followers, total = await service.get_followers(current_user.id, skip, limit)
    return FollowListResponse(
        total=total,
        followers=[FollowResponse.model_validate(f) for f in followers],
        following=[],
    )


@router.get("/following", response_model=FollowListResponse)
async def get_following(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user)],
    skip: int = 0,
    limit: int = 50,
):
    """获取关注列表"""
    service = FollowService(db)
    following, total = await service.get_following(current_user.id, skip, limit)
    return FollowListResponse(
        total=total,
        followers=[],
        following=[FollowResponse.model_validate(f) for f in following],
    )


@router.post("/friend", response_model=FriendResponse)
async def request_friend(
    friend_in: FriendCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user)],
):
    """发送好友请求"""
    user_service = UserService(db)
    user = await user_service.get_by_id(friend_in.friend_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="用户不存在")

    service = FriendService(db)
    friend = await service.request(current_user.id, friend_in)
    return FriendResponse.model_validate(friend)


@router.post("/friend/{friend_id}/accept", response_model=FriendResponse)
async def accept_friend(
    friend_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user)],
):
    """接受好友请求"""
    service = FriendService(db)
    friend = await service.accept(current_user.id, friend_id)
    if not friend:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="好友请求不存在")
    return FriendResponse.model_validate(friend)


@router.post("/friend/{friend_id}/reject", status_code=status.HTTP_204_NO_CONTENT)
async def reject_friend(
    friend_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user)],
):
    """拒绝好友请求"""
    service = FriendService(db)
    if not await service.reject(current_user.id, friend_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="好友请求不存在")


@router.get("/friends", response_model=FriendListResponse)
async def get_friends(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user)],
    skip: int = 0,
    limit: int = 50,
):
    """获取好友列表"""
    service = FriendService(db)
    friends, total = await service.get_list(current_user.id, skip, limit)
    return FriendListResponse(total=total, items=[FriendResponse.model_validate(f) for f in friends])


@router.get("/friends/requests", response_model=list[FriendResponse])
async def get_friend_requests(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user)],
):
    """获取好友请求列表"""
    service = FriendService(db)
    requests = await service.get_requests(current_user.id)
    return [FriendResponse.model_validate(r) for r in requests]