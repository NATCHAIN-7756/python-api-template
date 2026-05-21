"""
用户资料服务
SCALE OS v10.0
"""

from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user_profile import UserProfile
from app.schemas.user_profile import UserProfileCreate, UserProfileUpdate


class UserProfileService:
    """用户资料服务"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, user_id: int, profile_in: UserProfileCreate) -> UserProfile:
        """创建用户资料"""
        profile = UserProfile(user_id=user_id, **profile_in.model_dump())
        self.db.add(profile)
        await self.db.flush()
        await self.db.refresh(profile)
        return profile

    async def get_by_user_id(self, user_id: int) -> Optional[UserProfile]:
        """根据用户 ID 获取资料"""
        result = await self.db.execute(select(UserProfile).where(UserProfile.user_id == user_id))
        return result.scalar_one_or_none()

    async def update(self, user_id: int, profile_in: UserProfileUpdate) -> Optional[UserProfile]:
        """更新用户资料"""
        profile = await self.get_by_user_id(user_id)
        if not profile:
            # 如果不存在则创建
            profile = await self.create(user_id, UserProfileCreate(**profile_in.model_dump(exclude_unset=True)))
            return profile

        update_data = profile_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(profile, field, value)

        await self.db.flush()
        await self.db.refresh(profile)
        return profile

    async def increment(self, user_id: int, field: str, amount: int = 1) -> bool:
        """增加统计字段"""
        profile = await self.get_by_user_id(user_id)
        if not profile:
            return False

        current = getattr(profile, field, 0) or 0
        setattr(profile, field, current + amount)
        await self.db.flush()
        return True
