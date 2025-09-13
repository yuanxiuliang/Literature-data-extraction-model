"""
晶体材料服务

处理晶体材料相关的业务逻辑
"""

from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.crystal_materials import CrystalMaterial
from .base_service import BaseService


class CrystalMaterialService(BaseService[CrystalMaterial]):
    """晶体材料服务类"""
    
    def __init__(self):
        super().__init__(CrystalMaterial)
    
    def get_by_formula(self, db: Session, chemical_formula: str) -> Optional[CrystalMaterial]:
        """根据化学式获取材料"""
        return self.get_by_field(db, "chemical_formula", chemical_formula)
    
    def create_or_get_by_formula(self, db: Session, chemical_formula: str, **kwargs) -> CrystalMaterial:
        """根据化学式创建或获取材料"""
        material = self.get_by_formula(db, chemical_formula)
        if not material:
            material = self.create(db, chemical_formula=chemical_formula, **kwargs)
        return material
    
    def search_by_formula(self, db: Session, formula_pattern: str) -> List[CrystalMaterial]:
        """根据化学式模式搜索材料"""
        return db.query(CrystalMaterial).filter(
            CrystalMaterial.chemical_formula.like(f"%{formula_pattern}%")
        ).all()
    
    def search_by_crystal_system(self, db: Session, crystal_system: str) -> List[CrystalMaterial]:
        """根据晶系搜索材料"""
        return db.query(CrystalMaterial).filter(
            CrystalMaterial.crystal_system == crystal_system
        ).all()
