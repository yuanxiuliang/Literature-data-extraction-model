"""
Chemical Vapor Transport 相关模型

包含化学气相输运方法的所有相关表
"""

from sqlalchemy import Column, String, Integer, ForeignKey, Float, Text, Enum
from sqlalchemy.orm import relationship
from app.database.base import BaseModel
import enum


class CVTMaterialType(str, enum.Enum):
    """CVT原料类型枚举"""
    TRANSPORT_AGENT = "输运剂"
    OTHER = "其他原料"


class CVTAtmosphereType(str, enum.Enum):
    """CVT气氛类型枚举"""
    VACUUM = "真空"
    INERT_GAS = "惰性气体"
    ATMOSPHERE = "大气"
    OTHER = "其他"


class CVTStorageMethod(str, enum.Enum):
    """CVT存储方式枚举"""
    AIR_ISOLATION = "隔绝空气"
    OTHER = "其他"


class CVTMethodDetail(BaseModel):
    """
    化学气相输运方法详情表
    """
    __tablename__ = "cvt_method_details"
    
    method_id = Column(Integer, ForeignKey("growth_methods.id"), nullable=False, comment="生长方法ID")
    
    # 关系定义
    method = relationship("GrowthMethod")
    raw_materials = relationship("CVTRawMaterial", back_populates="cvt_method")
    growth_conditions = relationship("CVTGrowthCondition", back_populates="cvt_method", uselist=False)
    crystal_processing = relationship("CVTCrystalProcessing", back_populates="cvt_method", uselist=False)
    crystal_morphology = relationship("CVTCrystalMorphology", back_populates="cvt_method", uselist=False)


class CVTRawMaterial(BaseModel):
    """
    化学气相输运方法原料表
    """
    __tablename__ = "cvt_raw_materials"
    
    cvt_method_id = Column(Integer, ForeignKey("cvt_method_details.id"), nullable=False, comment="CVT方法ID")
    material_type = Column(Enum(CVTMaterialType), nullable=False, comment="原料类型")
    material_name = Column(String(255), nullable=False, comment="原料名称")
    chemical_formula = Column(String(255), comment="化学式")
    amount = Column(String(100), comment="用量")
    unit = Column(String(50), comment="单位")
    
    # 关系定义
    cvt_method = relationship("CVTMethodDetail", back_populates="raw_materials")


class CVTGrowthCondition(BaseModel):
    """
    化学气相输运方法生长条件表
    """
    __tablename__ = "cvt_growth_conditions"
    
    cvt_method_id = Column(Integer, ForeignKey("cvt_method_details.id"), nullable=False, comment="CVT方法ID")
    source_temperature = Column(Float, comment="原料温度")
    growth_temperature = Column(Float, comment="生长温度")
    temperature_unit = Column(String(20), comment="温度单位")
    atmosphere_type = Column(Enum(CVTAtmosphereType), comment="气氛类型")
    pressure_value = Column(Float, comment="压力数值")
    pressure_unit = Column(String(20), comment="压力单位")
    
    # 关系定义
    cvt_method = relationship("CVTMethodDetail", back_populates="growth_conditions")


class CVTCrystalProcessing(BaseModel):
    """
    化学气相输运方法晶体处理表
    """
    __tablename__ = "cvt_crystal_processing"
    
    cvt_method_id = Column(Integer, ForeignKey("cvt_method_details.id"), nullable=False, comment="CVT方法ID")
    post_processing = Column(Text, comment="后处理方法")
    storage_method = Column(Enum(CVTStorageMethod), comment="存储方式")
    storage_details = Column(Text, comment="存储详情")
    
    # 关系定义
    cvt_method = relationship("CVTMethodDetail", back_populates="crystal_processing")


class CVTCrystalMorphology(BaseModel):
    """
    化学气相输运方法单晶形态表
    """
    __tablename__ = "cvt_crystal_morphology"
    
    cvt_method_id = Column(Integer, ForeignKey("cvt_method_details.id"), nullable=False, comment="CVT方法ID")
    color = Column(String(100), comment="颜色")
    shape = Column(String(100), comment="形状")
    typical_size = Column(String(100), comment="典型尺寸")
    size_unit = Column(String(20), comment="尺寸单位")
    
    # 关系定义
    cvt_method = relationship("CVTMethodDetail", back_populates="crystal_morphology")
