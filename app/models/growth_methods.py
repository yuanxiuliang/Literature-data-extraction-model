"""
生长方法表模型

存储生长方法的基本信息
"""

from sqlalchemy import Column, String, Integer, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.database.base import BaseModel
import enum


class MethodType(str, enum.Enum):
    """生长方法类型枚举"""
    FLUX_METHOD = "Flux Method/Solution Growth"
    CHEMICAL_VAPOR_TRANSPORT = "Chemical Vapor Transport"
    OTHER = "other"


class GrowthMethod(BaseModel):
    """
    生长方法表
    
    存储生长方法的基本信息
    """
    __tablename__ = "growth_methods"
    
    method_type = Column(Enum(MethodType), nullable=False, comment="方法类型")
    paper_id = Column(Integer, ForeignKey("papers.id"), nullable=False, comment="文献ID")
    material_id = Column(Integer, ForeignKey("crystal_materials.id"), nullable=False, comment="材料ID")
    
    # 关系定义
    paper = relationship("Paper", back_populates="growth_methods")
    material = relationship("CrystalMaterial", back_populates="growth_methods")
    
    def __repr__(self):
        return f"<GrowthMethod(id={self.id}, type='{self.method_type}')>"
