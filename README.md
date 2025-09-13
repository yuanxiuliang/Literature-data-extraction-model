# 单晶生长方法文献数据提取模型

## 项目概述

### 项目背景

单晶生长是材料科学、晶体学和固态物理研究中的重要技术。随着科学文献的快速增长，研究人员需要从大量文献中提取和整理单晶生长的实验方法信息，这是一个耗时且容易出错的过程。传统的文献阅读和手工记录方式已经无法满足现代科研的需求。

### 项目目标

本项目旨在开发一个智能化的文献数据提取系统，能够：

- **自动化文献处理**：从科学文献中自动提取单晶生长相关的实验方法信息
- **结构化数据存储**：将提取的信息以结构化的方式存储到本地数据库
- **支持主要生长方法**：重点支持两种主要的单晶生长方法
  - **Flux Method / Solution Growth（助熔剂法/溶液生长法）**
  - **Chemical Vapor Transport（化学气相输运法）**
- **本地化处理**：所有数据处理在本地进行，保护数据隐私
- **用户友好界面**：提供直观的桌面应用界面

### 核心功能

1. **文献获取**
   - 支持通过DOI自动获取文献信息
   - 本地PDF文件上传和处理
   - 批量文献处理能力

2. **智能信息提取**
   - 使用AI模型自动识别和提取关键信息
   - 支持中英文文献处理
   - 高精度的信息提取算法

3. **数据管理**
   - 结构化的数据库存储
   - 支持复杂查询和筛选
   - 数据导出和备份功能

4. **质量控制**
   - 提取结果的可视化展示
   - 人工验证和修正功能
   - 置信度评分系统

### 应用场景

- **科研人员**：快速整理和查询单晶生长方法文献
- **材料研究**：建立单晶生长方法数据库
- **教学辅助**：为晶体生长课程提供案例库
- **工业应用**：为单晶材料制备提供参考

### 技术优势

- **本地化部署**：数据不离开本地，保护隐私
- **离线工作**：无需网络连接即可使用
- **可扩展性**：易于添加新的生长方法类型
- **开源友好**：基于开源技术栈，便于定制和扩展

## 数据库结构设计

### 核心表结构

#### 1. papers（文献表）
```sql
- id (主键)
- doi (DOI，唯一标识)
- created_at (创建时间)
```

#### 2. crystal_materials（晶体材料表）
```sql
- id (主键)
- chemical_formula (化学式)
- crystal_system (晶系)
- space_group (空间群)
- lattice_parameters (晶格参数，JSON格式)
- created_at (创建时间)
```

#### 3. growth_methods（生长方法表）
```sql
- id (主键)
- method_type (方法类型：Flux Method/Solution Growth, Chemical Vapor Transport, other)
- paper_id (外键，关联papers表)
- material_id (外键，关联crystal_materials表)
- created_at (创建时间)
```

### Flux Method / Solution Growth 专用表

#### 4. flux_method_details（助熔剂方法详情表）
```sql
- id (主键)
- method_id (外键，关联growth_methods表)
- created_at (创建时间)
```

#### 5. flux_raw_materials（助熔剂方法原料表）
```sql
- id (主键)
- flux_method_id (外键，关联flux_method_details表)
- material_type (原料类型：助熔剂/其他原料)
- material_name (原料名称)
- chemical_formula (化学式)
- amount (用量)
- unit (单位)
- created_at (创建时间)
```

#### 6. flux_growth_conditions（助熔剂方法生长条件表）
```sql
- id (主键)
- flux_method_id (外键，关联flux_method_details表)
- temperature_start (起始温度)
- temperature_end (终点温度)
- temperature_unit (温度单位)
- heating_rate (变温速度)
- heating_rate_unit (变温速度单位)
- atmosphere_type (气氛类型：真空/惰性气体/大气/其他)
- pressure_value (压力数值)
- pressure_unit (压力单位)
- created_at (创建时间)
```

#### 7. flux_crystal_processing（助熔剂方法晶体处理表）
```sql
- id (主键)
- flux_method_id (外键，关联flux_method_details表)
- flux_removal_method (助熔剂去除方法：离心去除/反应去除/无需处理)
- flux_removal_details (助熔剂去除详情)
- storage_method (存储方式：隔绝空气/其他)
- storage_details (存储详情)
- created_at (创建时间)
```

#### 8. flux_crystal_morphology（助熔剂方法单晶形态表）
```sql
- id (主键)
- flux_method_id (外键，关联flux_method_details表)
- color (颜色)
- shape (形状)
- typical_size (典型尺寸)
- size_unit (尺寸单位)
- created_at (创建时间)
```

### Chemical Vapor Transport 专用表

#### 9. cvt_method_details（化学气相输运方法详情表）
```sql
- id (主键)
- method_id (外键，关联growth_methods表)
- created_at (创建时间)
```

#### 10. cvt_raw_materials（化学气相输运方法原料表）
```sql
- id (主键)
- cvt_method_id (外键，关联cvt_method_details表)
- material_type (原料类型：输运剂/其他原料)
- material_name (原料名称)
- chemical_formula (化学式)
- amount (用量)
- unit (单位)
- created_at (创建时间)
```

#### 11. cvt_growth_conditions（化学气相输运方法生长条件表）
```sql
- id (主键)
- cvt_method_id (外键，关联cvt_method_details表)
- source_temperature (原料温度)
- growth_temperature (生长温度)
- temperature_unit (温度单位)
- atmosphere_type (气氛类型：真空/惰性气体/大气/其他)
- pressure_value (压力数值)
- pressure_unit (压力单位)
- created_at (创建时间)
```

#### 12. cvt_crystal_processing（化学气相输运方法晶体处理表）
```sql
- id (主键)
- cvt_method_id (外键，关联cvt_method_details表)
- post_processing (后处理方法)
- storage_method (存储方式)
- storage_details (存储详情)
- created_at (创建时间)
```

#### 13. cvt_crystal_morphology（化学气相输运方法单晶形态表）
```sql
- id (主键)
- cvt_method_id (外键，关联cvt_method_details表)
- color (颜色)
- shape (形状)
- typical_size (典型尺寸)
- size_unit (尺寸单位)
- created_at (创建时间)
```

## 数据库关系图

```
papers (1) ←→ (N) growth_methods
crystal_materials (1) ←→ (N) growth_methods
growth_methods (1) ←→ (1) flux_method_details (Flux Method)
growth_methods (1) ←→ (1) cvt_method_details (Chemical Vapor Transport)
flux_method_details (1) ←→ (N) flux_raw_materials
flux_method_details (1) ←→ (1) flux_growth_conditions
flux_method_details (1) ←→ (1) flux_crystal_processing
flux_method_details (1) ←→ (1) flux_crystal_morphology
cvt_method_details (1) ←→ (N) cvt_raw_materials
cvt_method_details (1) ←→ (1) cvt_growth_conditions
cvt_method_details (1) ←→ (1) cvt_crystal_processing
cvt_method_details (1) ←→ (1) cvt_crystal_morphology
```

## JSON字段示例

### lattice_parameters字段示例
```json
{
  "a": 5.43,
  "b": 5.43,
  "c": 5.43,
  "alpha": 90,
  "beta": 90,
  "gamma": 90
}
```

## 项目特点

- **专注两种主要方法**：Flux Method/Solution Growth 和 Chemical Vapor Transport
- **结构简洁**：去除冗余字段，提高查询效率
- **本地化处理**：支持本地数据库存储和处理
- **易于扩展**：可根据需要添加新的生长方法类型

## 技术栈

### 后端技术
- **Python 3.9+**：主要开发语言
- **FastAPI**：Web框架
- **SQLAlchemy**：ORM框架
- **Alembic**：数据库迁移工具
- **MySQL 8.0**：关系型数据库

### 前端技术
- **React**：用户界面框架
- **Ant Design**：UI组件库
- **Electron**：桌面应用框架
- **D3.js/Chart.js**：数据可视化

### AI和NLP
- **Hugging Face Transformers**：预训练模型
- **spaCy**：自然语言处理
- **SciBERT/ChemBERTa**：科学文献专用模型

### 部署和运维
- **Docker**：容器化部署
- **Docker Compose**：本地开发环境
- **云服务**：生产环境部署（阿里云/腾讯云/AWS）
- **MySQL云数据库**：云端数据存储

### 开发工具
- **Selenium**：网页自动化
- **BeautifulSoup4**：HTML解析
- **PyMuPDF**：PDF处理
- **pytest**：单元测试

## 使用说明

### 本地开发环境

1. **环境准备**
   ```bash
   # 克隆项目
   git clone https://github.com/yuanxiuliang/Literature-data-extraction-model.git
   
   # 进入项目目录
   cd Literature-data-extraction-model
   
   # 创建虚拟环境
   python3 -m venv venv
   source venv/bin/activate  # Linux/Mac
   # 或 venv\Scripts\activate  # Windows
   
   # 安装依赖
   pip install -r requirements.txt
   ```

2. **启动数据库**
   ```bash
   # 启动本地MySQL服务 (macOS)
   brew services start mysql
   
   # 创建数据库和用户
   mysql -u root -e "CREATE DATABASE IF NOT EXISTS crystal_growth CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
   mysql -u root -e "CREATE USER IF NOT EXISTS 'app_user'@'localhost' IDENTIFIED BY 'app_password';"
   mysql -u root -e "GRANT ALL PRIVILEGES ON crystal_growth.* TO 'app_user'@'localhost';"
   mysql -u root -e "FLUSH PRIVILEGES;"
   
   # 创建数据库表
   PYTHONPATH=. python app/database/init_db.py
   
   # 运行数据库迁移
   PYTHONPATH=. alembic upgrade head
   ```

3. **测试数据库**
   ```bash
   # 运行数据库测试
   python test_db.py
   ```

4. **启动应用**
   ```bash
   # 启动API服务
   PYTHONPATH=. python app/main.py
   
   # 访问API文档
   # http://localhost:8000/docs
   ```

### 生产环境部署

1. **云端部署**
   - 配置云数据库MySQL
   - 部署应用服务器
   - 配置域名和SSL证书

2. **数据管理**
   - 通过DOI标识文献
   - 自动提取晶体材料信息（化学式、晶系、空间群、晶格参数）
   - 识别生长方法类型并提取相应参数
   - 存储到MySQL数据库
   - 支持数据查询和导出

### 功能特点

- **本地化开发**：使用MySQL本地开发环境
- **云端部署**：支持部署到云服务供他人使用
- **数据一致性**：开发和生产环境使用相同的数据库技术
- **易于扩展**：模块化设计，便于添加新功能

## 项目进度

### ✅ 已完成阶段

#### Phase 1: 项目基础环境搭建 ✅
- Python 3.9+ 虚拟环境配置
- 项目目录结构创建
- Git版本控制和GitHub仓库配置
- 基础依赖包安装

#### Phase 2: 数据库设计与实现 ✅
- MySQL 8.0 本地数据库配置
- 13个核心数据表模型创建
- SQLAlchemy ORM映射实现
- Alembic数据库迁移配置
- 完整服务层和CRUD操作
- 数据库功能测试验证

### 🚧 进行中阶段

#### Phase 3: 文献搜索与PDF获取 (待开始)
- 学术文献搜索引擎集成
- 关键词搜索和结果筛选
- PDF批量下载和预处理

### 📋 待完成阶段

- Phase 4: PDF解析与文本提取
- Phase 5: 文献筛选与分类
- Phase 6: 信息提取与数据存储
- Phase 7: AI模型集成与训练
- Phase 8: Web用户界面开发
- Phase 9: 桌面应用开发
- Phase 10: 测试与优化
- Phase 11: 部署与文档

---

*最后更新：2024年*
