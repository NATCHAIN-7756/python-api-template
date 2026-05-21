"""
积分系统服务
SCALE OS v10.0
"""

from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user_points import UserPoints, PointsLog
from app.models.user_level import UserLevel
from app.schemas.user_points import PointsLogCreate


class UserPointsService:
    """用户积分服务"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, user_id: int) -> UserPoints:
        """创建用户积分记录"""
        points = UserPoints(user_id=user_id)
        self.db.add(points)
        await self.db.flush()
        await self.db.refresh(points)
        return points

    async def get_by_user_id(self, user_id: int) -> Optional[UserPoints]:
        """根据用户 ID 获取积分"""
        result = await self.db.execute(select(UserPoints).where(UserPoints.user_id == user_id))
        return result.scalar_one_or_none()

    async def add_credits(
        self,
        user_id: int,
        amount: int,
        operation: str,
        related_id: Optional[int] = None,
        description: Optional[str] = None,
    ) -> Optional[UserPoints]:
        """增加积分"""
        points = await self.get_by_user_id(user_id)
        if not points:
            points = await self.create(user_id)

        # 更新积分
        points.credits += amount
        balance = points.credits

        # 记录日志
        log = PointsLog(
            user_id=user_id,
            operation=operation,
            related_id=related_id,
            amount=amount,
            balance=balance,
            description=description,
        )
        self.db.add(log)

        await self.db.flush()
        await self.db.refresh(points)
        return points

    async def deduct_credits(
        self,
        user_id: int,
        amount: int,
        operation: str,
        related_id: Optional[int] = None,
        description: Optional[str] = None,
    ) -> Optional[UserPoints]:
        """扣除积分"""
        points = await self.get_by_user_id(user_id)
        if not points or points.credits < amount:
            return None

        points.credits -= amount
        balance = points.credits

        log = PointsLog(
            user_id=user_id,
            operation=operation,
            related_id=related_id,
            amount=-amount,
            balance=balance,
            description=description,
        )
        self.db.add(log)

        await self.db.flush()
        await self.db.refresh(points)
        return points

    async def get_level(self, credits: int) -> Optional[UserLevel]:
        """根据积分获取等级"""
        result = await self.db.execute(
            select(UserLevel)
            .where(UserLevel.min_credits <= credits)
            .order_by(UserLevel.level.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def get_logs(self, user_id: int, skip: int = 0, limit: int = 50) -> list[PointsLog]:
        """获取积分日志"""
        result = await self.db.execute(
            select(PointsLog)
            .where(PointsLog.user_id == user_id)
            .order_by(PointsLog.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())


class UserLevelService:
    """用户等级服务"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, level_in) -> UserLevel:
        """创建等级"""
        level = UserLevel(**level_in.model_dump())
        self.db.add(level)
        await self.db.flush()
        await self.db.refresh(level)
        return level

    async def get_list(self) -> list[UserLevel]:
        """获取所有等级"""
        result = await self.db.execute(select(UserLevel).order_by(UserLevel.level))
        return list(result.scalars().all())

    async def get_by_level(self, level: int) -> Optional[UserLevel]:
        """根据等级获取"""
        result = await self.db.execute(select(UserLevel).where(UserLevel.level == level))
        return result.scalar_one_or_none()
