"""
基础服务类

提供通用的CRUD操作
"""

from typing import TypeVar, Generic, Type, Optional, List, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.database.base import BaseModel

ModelType = TypeVar("ModelType", bound=BaseModel)


class BaseService(Generic[ModelType]):
    """
    基础服务类
    
    提供通用的CRUD操作
    """
    
    def __init__(self, model: Type[ModelType]):
        self.model = model
    
    def create(self, db: Session, **kwargs) -> ModelType:
        """创建记录"""
        try:
            db_obj = self.model(**kwargs)
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            return db_obj
        except SQLAlchemyError as e:
            db.rollback()
            raise e
    
    def get(self, db: Session, id: int) -> Optional[ModelType]:
        """根据ID获取记录"""
        return db.query(self.model).filter(self.model.id == id).first()
    
    def get_by_field(self, db: Session, field_name: str, field_value: Any) -> Optional[ModelType]:
        """根据字段值获取记录"""
        return db.query(self.model).filter(getattr(self.model, field_name) == field_value).first()
    
    def get_all(self, db: Session, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """获取所有记录"""
        return db.query(self.model).offset(skip).limit(limit).all()
    
    def update(self, db: Session, id: int, **kwargs) -> Optional[ModelType]:
        """更新记录"""
        try:
            db_obj = self.get(db, id)
            if db_obj:
                for key, value in kwargs.items():
                    if hasattr(db_obj, key):
                        setattr(db_obj, key, value)
                db.commit()
                db.refresh(db_obj)
            return db_obj
        except SQLAlchemyError as e:
            db.rollback()
            raise e
    
    def delete(self, db: Session, id: int) -> bool:
        """删除记录"""
        try:
            db_obj = self.get(db, id)
            if db_obj:
                db.delete(db_obj)
                db.commit()
                return True
            return False
        except SQLAlchemyError as e:
            db.rollback()
            raise e
    
    def count(self, db: Session) -> int:
        """获取记录总数"""
        return db.query(self.model).count()
