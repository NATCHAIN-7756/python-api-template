"""
用户组服务
SCALE OS v10.0
"""

from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user_group import UserGroup
from app.schemas.user_group import UserGroupCreate, UserGroupUpdate


class UserGroupService:
    """用户组服务"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, group_in: UserGroupCreate) -> UserGroup:
        """创建用户组"""
        group = UserGroup(**group_in.model_dump())
        self.db.add(group)
        await self.db.flush()
        await self.db.refresh(group)
        return group

    async def get_by_id(self, group_id: int) -> Optional[UserGroup]:
        """根据 ID 获取用户组"""
        result = await self.db.execute(select(UserGroup).where(UserGroup.id == group_id))
        return result.scalar_one_or_none()

    async def get_by_name(self, name: str) -> Optional[UserGroup]:
        """根据名称获取用户组"""
        result = await self.db.execute(select(UserGroup).where(UserGroup.name == name))
        return result.scalar_one_or_none()

    async def get_list(self, skip: int = 0, limit: int = 100) -> list[UserGroup]:
        """获取用户组列表"""
        result = await self.db.execute(select(UserGroup).offset(skip).limit(limit))
        return list(result.scalars().all())

    async def update(self, group_id: int, group_in: UserGroupUpdate) -> Optional[UserGroup]:
        """更新用户组"""
        group = await self.get_by_id(group_id)
        if not group:
            return None

        update_data = group_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(group, field, value)

        await self.db.flush()
        await self.db.refresh(group)
        return group

    async def delete(self, group_id: int) -> bool:
        """删除用户组"""
        group = await self.get_by_id(group_id)
        if not group:
            return False
        await self.db.delete(group)
        await self.db.flush()
        return True

    async def get_by_credits(self, credits: int) -> Optional[UserGroup]:
        """根据积分获取对应的用户组"""
        result = await self.db.execute(
            select(UserGroup)
            .where(UserGroup.min_credits <= credits)
            .where(UserGroup.max_credits >= credits)
            .where(UserGroup.type == "user")
        )
        return result.scalar_one_or_none()
