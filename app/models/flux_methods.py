"""
Flux Method / Solution Growth 相关模型

包含助熔剂方法的所有相关表
"""

from sqlalchemy import Column, String, Integer, ForeignKey, Float, Text, Enum
from sqlalchemy.orm import relationship
from app.database.base import BaseModel
import enum


class MaterialType(str, enum.Enum):
    """原料类型枚举"""
    FLUX = "助熔剂"
    OTHER = "其他原料"


class AtmosphereType(str, enum.Enum):
    """气氛类型枚举"""
    VACUUM = "真空"
    INERT_GAS = "惰性气体"
    ATMOSPHERE = "大气"
    OTHER = "其他"


class FluxRemovalMethod(str, enum.Enum):
    """助熔剂去除方法枚举"""
    CENTRIFUGAL = "离心去除"
    REACTION = "反应去除"
    NO_TREATMENT = "无需处理"


class StorageMethod(str, enum.Enum):
    """存储方式枚举"""
    AIR_ISOLATION = "隔绝空气"
    OTHER = "其他"


class FluxMethodDetail(BaseModel):
    """
    助熔剂方法详情表
    """
    __tablename__ = "flux_method_details"
    
    method_id = Column(Integer, ForeignKey("growth_methods.id"), nullable=False, comment="生长方法ID")
    
    # 关系定义
    method = relationship("GrowthMethod")
    raw_materials = relationship("FluxRawMaterial", back_populates="flux_method")
    growth_conditions = relationship("FluxGrowthCondition", back_populates="flux_method", uselist=False)
    crystal_processing = relationship("FluxCrystalProcessing", back_populates="flux_method", uselist=False)
    crystal_morphology = relationship("FluxCrystalMorphology", back_populates="flux_method", uselist=False)


class FluxRawMaterial(BaseModel):
    """
    助熔剂方法原料表
    """
    __tablename__ = "flux_raw_materials"
    
    flux_method_id = Column(Integer, ForeignKey("flux_method_details.id"), nullable=False, comment="助熔剂方法ID")
    material_type = Column(Enum(MaterialType), nullable=False, comment="原料类型")
    material_name = Column(String(255), nullable=False, comment="原料名称")
    chemical_formula = Column(String(255), comment="化学式")
    amount = Column(String(100), comment="用量")
    unit = Column(String(50), comment="单位")
    
    # 关系定义
    flux_method = relationship("FluxMethodDetail", back_populates="raw_materials")


class FluxGrowthCondition(BaseModel):
    """
    助熔剂方法生长条件表
    """
    __tablename__ = "flux_growth_conditions"
    
    flux_method_id = Column(Integer, ForeignKey("flux_method_details.id"), nullable=False, comment="助熔剂方法ID")
    temperature_start = Column(Float, comment="起始温度")
    temperature_end = Column(Float, comment="终点温度")
    temperature_unit = Column(String(20), comment="温度单位")
    heating_rate = Column(Float, comment="变温速度")
    heating_rate_unit = Column(String(20), comment="变温速度单位")
    atmosphere_type = Column(Enum(AtmosphereType), comment="气氛类型")
    pressure_value = Column(Float, comment="压力数值")
    pressure_unit = Column(String(20), comment="压力单位")
    
    # 关系定义
    flux_method = relationship("FluxMethodDetail", back_populates="growth_conditions")


class FluxCrystalProcessing(BaseModel):
    """
    助熔剂方法晶体处理表
    """
    __tablename__ = "flux_crystal_processing"
    
    flux_method_id = Column(Integer, ForeignKey("flux_method_details.id"), nullable=False, comment="助熔剂方法ID")
    flux_removal_method = Column(Enum(FluxRemovalMethod), comment="助熔剂去除方法")
    flux_removal_details = Column(Text, comment="助熔剂去除详情")
    storage_method = Column(Enum(StorageMethod), comment="存储方式")
    storage_details = Column(Text, comment="存储详情")
    
    # 关系定义
    flux_method = relationship("FluxMethodDetail", back_populates="crystal_processing")


class FluxCrystalMorphology(BaseModel):
    """
    助熔剂方法单晶形态表
    """
    __tablename__ = "flux_crystal_morphology"
    
    flux_method_id = Column(Integer, ForeignKey("flux_method_details.id"), nullable=False, comment="助熔剂方法ID")
    color = Column(String(100), comment="颜色")
    shape = Column(String(100), comment="形状")
    typical_size = Column(String(100), comment="典型尺寸")
    size_unit = Column(String(20), comment="尺寸单位")
    
    # 关系定义
    flux_method = relationship("FluxMethodDetail", back_populates="crystal_morphology")
