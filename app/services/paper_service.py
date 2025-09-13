"""
文献服务

处理文献相关的业务逻辑
"""

from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.papers import Paper
from .base_service import BaseService


class PaperService(BaseService[Paper]):
    """文献服务类"""
    
    def __init__(self):
        super().__init__(Paper)
    
    def get_by_doi(self, db: Session, doi: str) -> Optional[Paper]:
        """根据DOI获取文献"""
        return self.get_by_field(db, "doi", doi)
    
    def create_or_get_by_doi(self, db: Session, doi: str) -> Paper:
        """根据DOI创建或获取文献"""
        paper = self.get_by_doi(db, doi)
        if not paper:
            paper = self.create(db, doi=doi)
        return paper
    
    def search_by_doi(self, db: Session, doi_pattern: str) -> List[Paper]:
        """根据DOI模式搜索文献"""
        return db.query(Paper).filter(Paper.doi.like(f"%{doi_pattern}%")).all()
