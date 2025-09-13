# 项目结构说明

## 目录结构

```
project/
├── app/                           # 应用核心代码
│   ├── __init__.py               # 应用包初始化
│   ├── main.py                   # FastAPI应用入口
│   ├── database/                 # 数据库相关
│   │   ├── __init__.py
│   │   ├── base.py              # 基础模型类
│   │   ├── connection.py        # 数据库连接配置
│   │   └── init_db.py           # 数据库初始化脚本
│   ├── models/                   # 数据模型
│   │   ├── __init__.py
│   │   ├── papers.py            # 文献表模型
│   │   ├── crystal_materials.py # 晶体材料表模型
│   │   ├── growth_methods.py    # 生长方法表模型
│   │   ├── flux_methods.py      # 助熔剂方法相关模型
│   │   └── cvt_methods.py       # 化学气相输运方法相关模型
│   ├── services/                 # 业务逻辑服务层
│   │   ├── __init__.py
│   │   ├── base_service.py      # 基础服务类
│   │   ├── paper_service.py     # 文献服务
│   │   ├── crystal_material_service.py # 晶体材料服务
│   │   └── growth_method_service.py    # 生长方法服务
│   ├── api/                      # API接口层 (待开发)
│   └── utils/                    # 工具函数 (待开发)
├── data/                         # 数据存储目录
│   ├── raw_pdfs/                 # 原始PDF文件
│   ├── processed_texts/          # 处理后的文本文件
│   └── models/                   # AI模型文件
├── tests/                        # 测试代码
├── docs/                         # 文档目录
├── alembic/                      # 数据库迁移
│   ├── versions/                 # 迁移版本文件
│   ├── env.py                    # Alembic环境配置
│   └── script.py.mako           # 迁移脚本模板
├── venv/                         # Python虚拟环境
├── requirements.txt              # Python依赖包
├── alembic.ini                   # Alembic配置文件
├── docker-compose.yml            # Docker Compose配置
├── Dockerfile                    # Docker镜像配置
├── init.sql                      # 数据库初始化SQL
├── test_db.py                    # 数据库测试脚本
├── README.md                     # 项目说明文档
├── TECHNICAL_ROADMAP.md          # 技术路线图
├── DATABASE.md                   # 数据库设计文档
├── DEPLOYMENT.md                 # 部署指南
└── PROJECT_STRUCTURE.md          # 项目结构说明
```

## 核心模块说明

### 1. 数据库层 (app/database/)

#### base.py
- 定义所有数据库模型的基类 `BaseModel`
- 包含通用字段：id、created_at、updated_at
- 提供通用的 `__repr__` 方法

#### connection.py
- 数据库连接配置和引擎创建
- 会话工厂和依赖注入
- 连接池配置和错误处理

#### init_db.py
- 数据库表创建脚本
- 支持一键创建所有表
- 用于开发和测试环境

### 2. 数据模型层 (app/models/)

#### 核心模型
- **papers.py**: 文献表模型，使用DOI作为唯一标识
- **crystal_materials.py**: 晶体材料表模型，包含化学式、晶系等信息
- **growth_methods.py**: 生长方法表模型，关联文献和材料

#### 方法专用模型
- **flux_methods.py**: 助熔剂方法相关的5个表模型
- **cvt_methods.py**: 化学气相输运方法相关的5个表模型

### 3. 服务层 (app/services/)

#### base_service.py
- 通用CRUD操作基类
- 支持泛型，适用于所有模型
- 包含创建、查询、更新、删除等操作

#### 专门服务类
- **paper_service.py**: 文献相关业务逻辑
- **crystal_material_service.py**: 晶体材料相关业务逻辑
- **growth_method_service.py**: 生长方法相关业务逻辑

### 4. 配置和工具

#### 数据库迁移 (alembic/)
- 使用Alembic管理数据库版本
- 支持自动生成迁移脚本
- 支持数据库升级和回滚

#### 测试 (test_db.py)
- 数据库功能测试脚本
- 验证所有CRUD操作
- 测试数据关系完整性

## 开发规范

### 代码组织
- 按功能模块组织代码
- 每个模块都有独立的 `__init__.py`
- 使用类型提示和文档字符串

### 数据库设计
- 所有表都继承自 `BaseModel`
- 使用外键约束保证数据完整性
- 合理使用索引提高查询性能

### 服务层设计
- 每个模型都有对应的服务类
- 服务类继承自 `BaseService`
- 提供高级业务逻辑方法

## 扩展指南

### 添加新表
1. 在 `app/models/` 中创建新的模型文件
2. 在 `app/models/__init__.py` 中导入新模型
3. 在 `app/services/` 中创建对应的服务类
4. 运行 `alembic revision --autogenerate` 生成迁移

### 添加新功能
1. 在 `app/services/` 中添加业务逻辑
2. 在 `app/api/` 中添加API接口
3. 在 `tests/` 中添加测试用例

### 数据库升级
1. 修改模型文件
2. 运行 `alembic revision --autogenerate -m "描述"`
3. 检查生成的迁移文件
4. 运行 `alembic upgrade head` 应用迁移

## 环境配置

### 开发环境
- Python 3.9+
- MySQL 8.0
- 虚拟环境隔离

### 生产环境
- Docker容器化部署
- 云数据库服务
- 环境变量配置

---

*最后更新：2024年9月*
