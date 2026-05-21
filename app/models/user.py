"""
用户模型
SCALE OS v10.0
"""

from datetime import datetime
from typing import Optional, TYPE_CHECKING

from sqlalchemy import String, Boolean, DateTime, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.user_group import UserGroup
    from app.models.user_profile import UserProfile
    from app.models.user_points import UserPoints
    from app.models.user_level import UserOnline
    from app.models.post import Post
    from app.models.comment import Comment
    from app.models.follow import Follow


class User(Base):
    """用户表"""
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # 用户组
    group_id: Mapped[Optional[int]] = mapped_column(ForeignKey("user_groups.id"), nullable=True)
    
    # 状态
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, comment="是否已验证")
    
    # 等级积分
    level: Mapped[int] = mapped_column(Integer, default=1, comment="等级")
    credits: Mapped[int] = mapped_column(Integer, default=0, comment="积分")
    
    # 时间
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # 关联
    group: Mapped[Optional["UserGroup"]] = relationship("UserGroup", back_populates="users")
    profile: Mapped[Optional["UserProfile"]] = relationship("UserProfile", back_populates="user", uselist=False)
    points: Mapped[Optional["UserPoints"]] = relationship("UserPoints", back_populates="user", uselist=False)
    online: Mapped[Optional["UserOnline"]] = relationship("UserOnline", back_populates="user", uselist=False)
    posts: Mapped[list["Post"]] = relationship("Post", back_populates="author")
    comments: Mapped[list["Comment"]] = relationship("Comment", foreign_keys="Comment.author_id", back_populates="author")
    followers: Mapped[list["Follow"]] = relationship("Follow", foreign_keys="Follow.following_id", back_populates="following")
    following: Mapped[list["Follow"]] = relationship("Follow", foreign_keys="Follow.follower_id", back_populates="follower")

    def __repr__(self) -> str:
        return f"<User {self.username}>"