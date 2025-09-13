"""
数据库基础模型

定义所有数据库模型的基类和通用字段
"""

from sqlalchemy import Column, Integer, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

# 创建基础模型类
Base = declarative_base()


class BaseModel(Base):
    """
    基础模型类
    
    包含所有表的通用字段：
    - id: 主键
    - created_at: 创建时间
    - updated_at: 更新时间
    """
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<{self.__class__.__name__}(id={self.id})>"
