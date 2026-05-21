"""
积分系统
SCALE OS v10.0
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import String, Integer, DateTime, Text, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from decimal import Decimal

from app.database import Base


class UserPoints(Base):
    """用户积分表"""
    __tablename__ = "user_points"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True, nullable=False)
    
    # 积分类型
    credits: Mapped[int] = mapped_column(Integer, default=0, comment="总积分")
    ext_credits_1: Mapped[int] = mapped_column(Integer, default=0, comment="扩展积分1(金币)")
    ext_credits_2: Mapped[int] = mapped_column(Integer, default=0, comment="扩展积分2(威望)")
    ext_credits_3: Mapped[int] = mapped_column(Integer, default=0, comment="扩展积分3(贡献)")
    ext_credits_4: Mapped[int] = mapped_column(Integer, default=0, comment="扩展积分4(鲜花)")
    ext_credits_5: Mapped[int] = mapped_column(Integer, default=0, comment="扩展积分5")
    
    # 统计
    posts: Mapped[int] = mapped_column(Integer, default=0, comment="发帖数")
    comments: Mapped[int] = mapped_column(Integer, default=0, comment="评论数")
    diggs: Mapped[int] = mapped_column(Integer, default=0, comment="被赞数")
    onlinetime: Mapped[int] = mapped_column(Integer, default=0, comment="在线时长(分钟)")
    
    # 时间
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联
    user: Mapped["User"] = relationship("User", back_populates="points")

    def __repr__(self) -> str:
        return f"<UserPoints user={self.user_id} credits={self.credits}>"


class PointsLog(Base):
    """积分日志表"""
    __tablename__ = "points_logs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    
    # 变动信息
    operation: Mapped[str] = mapped_column(String(50), nullable=False, comment="操作类型")
    related_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, comment="关联ID")
    amount: Mapped[int] = mapped_column(Integer, nullable=False, comment="变动数量")
    balance: Mapped[int] = mapped_column(Integer, nullable=False, comment="变动后余额")
    
    # 描述
    description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, comment="描述")
    
    # 时间
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<PointsLog user={self.user_id} op={self.operation} amount={self.amount}>"
