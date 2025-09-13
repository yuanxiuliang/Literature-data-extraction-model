"""
数据库初始化脚本

创建所有数据库表
"""

from sqlalchemy import create_engine
from app.database.connection import DATABASE_URL
from app.database.base import Base
from app.models import *  # 导入所有模型


def create_tables():
    """创建所有数据库表"""
    engine = create_engine(DATABASE_URL)
    
    # 创建所有表
    Base.metadata.create_all(bind=engine)
    print("✅ 数据库表创建成功！")


def drop_tables():
    """删除所有数据库表"""
    engine = create_engine(DATABASE_URL)
    
    # 删除所有表
    Base.metadata.drop_all(bind=engine)
    print("✅ 数据库表删除成功！")


if __name__ == "__main__":
    create_tables()
