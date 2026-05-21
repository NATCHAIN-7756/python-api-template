"""
用户服务
SCALE OS v10.0
"""

from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate

# 密码加密
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserService:
    """用户服务"""

    def __init__(self, db: AsyncSession):
        self.db = db

    def _hash_password(self, password: str) -> str:
        """加密密码"""
        return pwd_context.hash(password)

    def _verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """验证密码"""
        return pwd_context.verify(plain_password, hashed_password)

    async def create(self, user_in: UserCreate) -> User:
        """创建用户"""
        user = User(
            username=user_in.username,
            email=user_in.email,
            hashed_password=self._hash_password(user_in.password),
        )
        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)
        return user

    async def get_by_id(self, user_id: int) -> Optional[User]:
        """根据 ID 获取用户"""
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> Optional[User]:
        """根据用户名获取用户"""
        result = await self.db.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[User]:
        """根据邮箱获取用户"""
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_list(self, skip: int = 0, limit: int = 100) -> tuple[list[User], int]:
        """获取用户列表"""
        # 总数
        count_result = await self.db.execute(select(User))
        total = len(count_result.scalars().all())

        # 列表
        result = await self.db.execute(select(User).offset(skip).limit(limit))
        users = list(result.scalars().all())

        return users, total

    async def update(self, user_id: int, user_in: UserUpdate) -> Optional[User]:
        """更新用户"""
        user = await self.get_by_id(user_id)
        if not user:
            return None

        update_data = user_in.model_dump(exclude_unset=True)
        if "password" in update_data:
            update_data["hashed_password"] = self._hash_password(update_data.pop("password"))

        for field, value in update_data.items():
            setattr(user, field, value)

        await self.db.flush()
        await self.db.refresh(user)
        return user

    async def delete(self, user_id: int) -> bool:
        """删除用户"""
        user = await self.get_by_id(user_id)
        if not user:
            return False
        await self.db.delete(user)
        await self.db.flush()
        return True

    async def authenticate(self, username: str, password: str) -> Optional[User]:
        """验证用户"""
        user = await self.get_by_username(username)
        if not user:
            return None
        if not self._verify_password(password, user.hashed_password):
            return None
        return user
