"""
晶体材料表模型

存储晶体材料的基本信息
"""

from sqlalchemy import Column, String, Text, JSON
from sqlalchemy.orm import relationship
from app.database.base import BaseModel


class CrystalMaterial(BaseModel):
    """
    晶体材料表
    
    存储晶体材料的基本信息
    """
    __tablename__ = "crystal_materials"
    
    chemical_formula = Column(String(255), nullable=False, comment="化学式")
    crystal_system = Column(String(100), comment="晶系")
    space_group = Column(String(50), comment="空间群")
    lattice_parameters = Column(JSON, comment="晶格参数，JSON格式")
    
    # 关系定义
    growth_methods = relationship("GrowthMethod", back_populates="material")
    
    def __repr__(self):
        return f"<CrystalMaterial(id={self.id}, formula='{self.chemical_formula}')>"
