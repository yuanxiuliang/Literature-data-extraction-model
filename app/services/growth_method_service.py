"""
生长方法服务

处理生长方法相关的业务逻辑
"""

from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.growth_methods import GrowthMethod, MethodType
from .base_service import BaseService


class GrowthMethodService(BaseService[GrowthMethod]):
    """生长方法服务类"""
    
    def __init__(self):
        super().__init__(GrowthMethod)
    
    def get_by_paper_and_material(self, db: Session, paper_id: int, material_id: int) -> Optional[GrowthMethod]:
        """根据文献和材料获取生长方法"""
        return db.query(GrowthMethod).filter(
            GrowthMethod.paper_id == paper_id,
            GrowthMethod.material_id == material_id
        ).first()
    
    def get_by_method_type(self, db: Session, method_type: MethodType) -> List[GrowthMethod]:
        """根据方法类型获取生长方法列表"""
        return db.query(GrowthMethod).filter(GrowthMethod.method_type == method_type).all()
    
    def create_growth_method(self, db: Session, paper_id: int, material_id: int, method_type: MethodType) -> GrowthMethod:
        """创建生长方法"""
        return self.create(
            db,
            paper_id=paper_id,
            material_id=material_id,
            method_type=method_type
        )
    
    def get_flux_methods(self, db: Session) -> List[GrowthMethod]:
        """获取所有助熔剂方法"""
        return self.get_by_method_type(db, MethodType.FLUX_METHOD)
    
    def get_cvt_methods(self, db: Session) -> List[GrowthMethod]:
        """获取所有化学气相输运方法"""
        return self.get_by_method_type(db, MethodType.CHEMICAL_VAPOR_TRANSPORT)
