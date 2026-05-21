"""
用户等级系统
SCALE OS v10.0
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import String, Integer, DateTime, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class UserLevel(Base):
    """用户等级表"""
    __tablename__ = "user_levels"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    
    # 等级信息
    level: Mapped[int] = mapped_column(Integer, unique=True, nullable=False, comment="等级")
    name: Mapped[str] = mapped_column(String(50), nullable=False, comment="等级名称")
    title: Mapped[str] = mapped_column(String(100), nullable=False, comment="等级标题")
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="描述")
    
    # 升级条件
    min_credits: Mapped[int] = mapped_column(Integer, default=0, comment="最低积分")
    max_credits: Mapped[int] = mapped_column(Integer, default=0, comment="最高积分")
    
    # 显示
    icon: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, comment="等级图标")
    color: Mapped[Optional[str]] = mapped_column(String(20), nullable=True, comment="等级颜色")
    stars: Mapped[int] = mapped_column(Integer, default=0, comment="星星数")
    
    # 权限加成
    bonus_posts: Mapped[int] = mapped_column(Integer, default=0, comment="发帖积分加成")
    bonus_comments: Mapped[int] = mapped_column(Integer, default=0, comment="评论积分加成")
    
    # 时间
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<UserLevel {self.level} - {self.name}>"


class UserOnline(Base):
    """用户在线状态表"""
    __tablename__ = "user_onlines"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True, nullable=False)
    
    # 在线状态
    is_online: Mapped[bool] = mapped_column(default=False, comment="是否在线")
    last_ip: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, comment="最后IP")
    last_action: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, comment="最后操作")
    
    # 时间统计
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, comment="最后登录")
    last_logout: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, comment="最后登出")
    total_online: Mapped[int] = mapped_column(Integer, default=0, comment="总在线时长(分钟)")
    today_online: Mapped[int] = mapped_column(Integer, default=0, comment="今日在线时长(分钟)")
    
    # 时间
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联
    user: Mapped["User"] = relationship("User", back_populates="online")

    def __repr__(self) -> str:
        return f"<UserOnline user={self.user_id} online={self.is_online}>"
