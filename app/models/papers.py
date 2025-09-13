"""
文献表模型

存储文献的基本信息
"""

from sqlalchemy import Column, String, Text
from sqlalchemy.orm import relationship
from app.database.base import BaseModel


class Paper(BaseModel):
    """
    文献表
    
    存储文献的基本信息，使用DOI作为唯一标识
    """
    __tablename__ = "papers"
    
    doi = Column(String(255), unique=True, index=True, nullable=False, comment="DOI唯一标识")
    
    # 关系定义
    growth_methods = relationship("GrowthMethod", back_populates="paper")
    
    def __repr__(self):
        return f"<Paper(id={self.id}, doi='{self.doi}')>"
