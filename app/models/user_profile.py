"""
用户资料扩展
SCALE OS v10.0
"""

from datetime import datetime, date
from typing import Optional

from sqlalchemy import String, Integer, DateTime, Text, Date, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class UserProfile(Base):
    """用户资料表"""
    __tablename__ = "user_profiles"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True, nullable=False)
    
    # 基本信息
    nickname: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, comment="昵称")
    realname: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, comment="真实姓名")
    gender: Mapped[Optional[str]] = mapped_column(String(10), nullable=True, comment="性别")
    birthday: Mapped[Optional[date]] = mapped_column(Date, nullable=True, comment="生日")
    idcard: Mapped[Optional[str]] = mapped_column(String(20), nullable=True, comment="身份证")
    
    # 联系方式
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True, comment="手机号")
    qq: Mapped[Optional[str]] = mapped_column(String(20), nullable=True, comment="QQ")
    wechat: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, comment="微信")
    address: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, comment="地址")
    
    # 个人展示
    avatar: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, comment="头像URL")
    cover: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, comment="封面URL")
    signature: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, comment="个性签名")
    bio: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="个人简介")
    website: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, comment="个人网站")
    
    # 地区
    province: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, comment="省份")
    city: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, comment="城市")
    district: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, comment="区县")
    
    # 职业
    company: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, comment="公司")
    position: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, comment="职位")
    industry: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, comment="行业")
    
    # 统计
    posts_count: Mapped[int] = mapped_column(Integer, default=0, comment="发帖数")
    comments_count: Mapped[int] = mapped_column(Integer, default=0, comment="评论数")
    followers_count: Mapped[int] = mapped_column(Integer, default=0, comment="粉丝数")
    following_count: Mapped[int] = mapped_column(Integer, default=0, comment="关注数")
    likes_count: Mapped[int] = mapped_column(Integer, default=0, comment="获赞数")
    
    # 时间
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联
    user: Mapped["User"] = relationship("User", back_populates="profile")

    def __repr__(self) -> str:
        return f"<UserProfile user={self.user_id}>"
