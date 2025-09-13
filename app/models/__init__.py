"""
数据模型模块

包含所有数据库表的模型定义
"""

from .papers import Paper
from .crystal_materials import CrystalMaterial
from .growth_methods import GrowthMethod
from .flux_methods import (
    FluxMethodDetail,
    FluxRawMaterial,
    FluxGrowthCondition,
    FluxCrystalProcessing,
    FluxCrystalMorphology
)
from .cvt_methods import (
    CVTMethodDetail,
    CVTRawMaterial,
    CVTGrowthCondition,
    CVTCrystalProcessing,
    CVTCrystalMorphology
)

__all__ = [
    # 核心表
    "Paper",
    "CrystalMaterial", 
    "GrowthMethod",
    
    # Flux Method表
    "FluxMethodDetail",
    "FluxRawMaterial",
    "FluxGrowthCondition", 
    "FluxCrystalProcessing",
    "FluxCrystalMorphology",
    
    # CVT Method表
    "CVTMethodDetail",
    "CVTRawMaterial",
    "CVTGrowthCondition",
    "CVTCrystalProcessing", 
    "CVTCrystalMorphology"
]
