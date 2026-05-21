"""
测试模型文件 - 验证修复后的文件写入权限
SCALE OS v10.0
Created: Thu May 21 01:07:32 PM CST 2026
"""

from datetime import datetime
from sqlalchemy import String, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base

class TestModel(Base):
    """测试模型"""
    __tablename__ = "test_models"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    def __repr__(self) -> str:
        return f"<TestModel id={self.id} name={self.name}>"
    
print('✅ 模型文件创建成功！')
