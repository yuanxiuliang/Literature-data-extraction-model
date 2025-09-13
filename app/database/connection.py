"""
数据库连接配置

提供数据库连接、会话管理和配置
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
from typing import Generator

# 数据库配置
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "mysql+pymysql://app_user:app_password@localhost:3306/crystal_growth"
)

# 创建数据库引擎
engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    echo=False,  # 设置为True可以看到SQL语句
    connect_args={
        "charset": "utf8mb4",
        "use_unicode": True
    }
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建基础模型类
Base = declarative_base()


def get_database_url() -> str:
    """获取数据库连接URL"""
    return DATABASE_URL


def create_engine():
    """创建数据库引擎"""
    return engine


def get_session() -> Generator:
    """
    获取数据库会话
    
    Yields:
        Session: SQLAlchemy会话对象
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_db():
    """依赖注入用的数据库会话获取函数"""
    return get_session()
