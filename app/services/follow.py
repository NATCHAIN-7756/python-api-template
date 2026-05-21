"""
关注/好友服务
SCALE OS v10.0
"""

from typing import Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.follow import Follow, Friend
from app.schemas.follow import FollowCreate, FriendCreate, FriendUpdate


class FollowService:
    """关注服务"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def toggle(self, user_id: int, follow_in: FollowCreate) -> tuple[Follow, bool]:
        """切换关注状态"""
        if user_id == follow_in.following_id:
            raise ValueError("不能关注自己")

        result = await self.db.execute(
            select(Follow).where(
                Follow.follower_id == user_id,
                Follow.following_id == follow_in.following_id,
            )
        )
        follow = result.scalar_one_or_none()

        if follow:
            follow.is_active = not follow.is_active
            await self.db.flush()
            return follow, follow.is_active
        else:
            follow = Follow(follower_id=user_id, **follow_in.model_dump())
            self.db.add(follow)
            await self.db.flush()
            await self.db.refresh(follow)
            return follow, True

    async def get_followers(self, user_id: int, skip: int = 0, limit: int = 50) -> tuple[list[Follow], int]:
        """获取粉丝列表"""
        query = select(Follow).where(Follow.following_id == user_id, Follow.is_active == True)
        count_result = await self.db.execute(select(func.count()).select_from(query.subquery()))
        total = count_result.scalar() or 0
        result = await self.db.execute(query.offset(skip).limit(limit).order_by(Follow.created_at.desc()))
        return list(result.scalars().all()), total

    async def get_following(self, user_id: int, skip: int = 0, limit: int = 50) -> tuple[list[Follow], int]:
        """获取关注列表"""
        query = select(Follow).where(Follow.follower_id == user_id, Follow.is_active == True)
        count_result = await self.db.execute(select(func.count()).select_from(query.subquery()))
        total = count_result.scalar() or 0
        result = await self.db.execute(query.offset(skip).limit(limit).order_by(Follow.created_at.desc()))
        return list(result.scalars().all()), total

    async def is_following(self, follower_id: int, following_id: int) -> bool:
        """检查是否已关注"""
        result = await self.db.execute(
            select(Follow).where(
                Follow.follower_id == follower_id,
                Follow.following_id == following_id,
                Follow.is_active == True,
            )
        )
        return result.scalar_one_or_none() is not None


class FriendService:
    """好友服务"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def request(self, user_id: int, friend_in: FriendCreate) -> Friend:
        """发送好友请求"""
        if user_id == friend_in.friend_id:
            raise ValueError("不能添加自己为好友")

        result = await self.db.execute(
            select(Friend).where(
                Friend.user_id == user_id,
                Friend.friend_id == friend_in.friend_id,
            )
        )
        friend = result.scalar_one_or_none()

        if friend:
            if friend.status == "rejected":
                friend.status = "pending"
                await self.db.flush()
            return friend

        friend = Friend(user_id=user_id, **friend_in.model_dump())
        self.db.add(friend)
        await self.db.flush()
        await self.db.refresh(friend)
        return friend

    async def accept(self, user_id: int, friend_id: int) -> Optional[Friend]:
        """接受好友请求"""
        result = await self.db.execute(
            select(Friend).where(
                Friend.user_id == friend_id,
                Friend.friend_id == user_id,
                Friend.status == "pending",
            )
        )
        friend = result.scalar_one_or_none()
        if not friend:
            return None

        friend.status = "accepted"
        # 创建双向好友关系
        new_friend = Friend(user_id=user_id, friend_id=friend_id, status="accepted")
        self.db.add(new_friend)
        await self.db.flush()
        return friend

    async def reject(self, user_id: int, friend_id: int) -> bool:
        """拒绝好友请求"""
        result = await self.db.execute(
            select(Friend).where(
                Friend.user_id == friend_id,
                Friend.friend_id == user_id,
                Friend.status == "pending",
            )
        )
        friend = result.scalar_one_or_none()
        if not friend:
            return False
        friend.status = "rejected"
        await self.db.flush()
        return True

    async def get_list(self, user_id: int, skip: int = 0, limit: int = 50) -> tuple[list[Friend], int]:
        """获取好友列表"""
        query = select(Friend).where(Friend.user_id == user_id, Friend.status == "accepted")
        count_result = await self.db.execute(select(func.count()).select_from(query.subquery()))
        total = count_result.scalar() or 0
        result = await self.db.execute(query.offset(skip).limit(limit).order_by(Friend.created_at.desc()))
        return list(result.scalars().all()), total

    async def get_requests(self, user_id: int) -> list[Friend]:
        """获取好友请求列表"""
        result = await self.db.execute(
            select(Friend).where(Friend.friend_id == user_id, Friend.status == "pending")
        )
        return list(result.scalars().all())