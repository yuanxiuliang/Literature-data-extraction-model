# 数据库设计文档

## 概述

本文档详细描述了单晶生长方法文献数据提取模型的数据库设计，包括表结构、关系设计、索引策略等。

## 技术栈

- **数据库**: MySQL 8.0
- **ORM**: SQLAlchemy 2.0
- **迁移工具**: Alembic
- **驱动**: PyMySQL

## 数据库连接

```python
# 连接字符串
DATABASE_URL = "mysql+pymysql://app_user:app_password@localhost:3306/crystal_growth"

# 连接配置
engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    connect_args={
        "charset": "utf8mb4",
        "use_unicode": True
    }
)
```

## 表结构设计

### 核心表（3个）

#### 1. papers（文献表）
```sql
CREATE TABLE papers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    doi VARCHAR(255) UNIQUE NOT NULL COMMENT 'DOI唯一标识',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_doi (doi)
);
```

#### 2. crystal_materials（晶体材料表）
```sql
CREATE TABLE crystal_materials (
    id INT AUTO_INCREMENT PRIMARY KEY,
    chemical_formula VARCHAR(255) NOT NULL COMMENT '化学式',
    crystal_system VARCHAR(100) COMMENT '晶系',
    space_group VARCHAR(50) COMMENT '空间群',
    lattice_parameters JSON COMMENT '晶格参数，JSON格式',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_formula (chemical_formula),
    INDEX idx_crystal_system (crystal_system)
);
```

#### 3. growth_methods（生长方法表）
```sql
CREATE TABLE growth_methods (
    id INT AUTO_INCREMENT PRIMARY KEY,
    method_type ENUM('Flux Method/Solution Growth', 'Chemical Vapor Transport', 'other') NOT NULL COMMENT '方法类型',
    paper_id INT NOT NULL COMMENT '文献ID',
    material_id INT NOT NULL COMMENT '材料ID',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (paper_id) REFERENCES papers(id),
    FOREIGN KEY (material_id) REFERENCES crystal_materials(id),
    INDEX idx_method_type (method_type),
    INDEX idx_paper_material (paper_id, material_id)
);
```

### Flux Method 相关表（5个）

#### 4. flux_method_details（助熔剂方法详情表）
```sql
CREATE TABLE flux_method_details (
    id INT AUTO_INCREMENT PRIMARY KEY,
    method_id INT NOT NULL COMMENT '生长方法ID',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (method_id) REFERENCES growth_methods(id)
);
```

#### 5. flux_raw_materials（助熔剂方法原料表）
```sql
CREATE TABLE flux_raw_materials (
    id INT AUTO_INCREMENT PRIMARY KEY,
    flux_method_id INT NOT NULL COMMENT '助熔剂方法ID',
    material_type ENUM('助熔剂', '其他原料') NOT NULL COMMENT '原料类型',
    material_name VARCHAR(255) NOT NULL COMMENT '原料名称',
    chemical_formula VARCHAR(255) COMMENT '化学式',
    amount VARCHAR(100) COMMENT '用量',
    unit VARCHAR(50) COMMENT '单位',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (flux_method_id) REFERENCES flux_method_details(id)
);
```

#### 6. flux_growth_conditions（助熔剂方法生长条件表）
```sql
CREATE TABLE flux_growth_conditions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    flux_method_id INT NOT NULL COMMENT '助熔剂方法ID',
    temperature_start FLOAT COMMENT '起始温度',
    temperature_end FLOAT COMMENT '终点温度',
    temperature_unit VARCHAR(20) COMMENT '温度单位',
    heating_rate FLOAT COMMENT '变温速度',
    heating_rate_unit VARCHAR(20) COMMENT '变温速度单位',
    atmosphere_type ENUM('真空', '惰性气体', '大气', '其他') COMMENT '气氛类型',
    pressure_value FLOAT COMMENT '压力数值',
    pressure_unit VARCHAR(20) COMMENT '压力单位',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (flux_method_id) REFERENCES flux_method_details(id)
);
```

#### 7. flux_crystal_processing（助熔剂方法晶体处理表）
```sql
CREATE TABLE flux_crystal_processing (
    id INT AUTO_INCREMENT PRIMARY KEY,
    flux_method_id INT NOT NULL COMMENT '助熔剂方法ID',
    flux_removal_method ENUM('离心去除', '反应去除', '无需处理') COMMENT '助熔剂去除方法',
    flux_removal_details TEXT COMMENT '助熔剂去除详情',
    storage_method ENUM('隔绝空气', '其他') COMMENT '存储方式',
    storage_details TEXT COMMENT '存储详情',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (flux_method_id) REFERENCES flux_method_details(id)
);
```

#### 8. flux_crystal_morphology（助熔剂方法单晶形态表）
```sql
CREATE TABLE flux_crystal_morphology (
    id INT AUTO_INCREMENT PRIMARY KEY,
    flux_method_id INT NOT NULL COMMENT '助熔剂方法ID',
    color VARCHAR(100) COMMENT '颜色',
    shape VARCHAR(100) COMMENT '形状',
    typical_size VARCHAR(100) COMMENT '典型尺寸',
    size_unit VARCHAR(20) COMMENT '尺寸单位',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (flux_method_id) REFERENCES flux_method_details(id)
);
```

### Chemical Vapor Transport 相关表（5个）

#### 9. cvt_method_details（化学气相输运方法详情表）
```sql
CREATE TABLE cvt_method_details (
    id INT AUTO_INCREMENT PRIMARY KEY,
    method_id INT NOT NULL COMMENT '生长方法ID',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (method_id) REFERENCES growth_methods(id)
);
```

#### 10. cvt_raw_materials（化学气相输运方法原料表）
```sql
CREATE TABLE cvt_raw_materials (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cvt_method_id INT NOT NULL COMMENT 'CVT方法ID',
    material_type ENUM('输运剂', '其他原料') NOT NULL COMMENT '原料类型',
    material_name VARCHAR(255) NOT NULL COMMENT '原料名称',
    chemical_formula VARCHAR(255) COMMENT '化学式',
    amount VARCHAR(100) COMMENT '用量',
    unit VARCHAR(50) COMMENT '单位',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (cvt_method_id) REFERENCES cvt_method_details(id)
);
```

#### 11. cvt_growth_conditions（化学气相输运方法生长条件表）
```sql
CREATE TABLE cvt_growth_conditions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cvt_method_id INT NOT NULL COMMENT 'CVT方法ID',
    source_temperature FLOAT COMMENT '原料温度',
    growth_temperature FLOAT COMMENT '生长温度',
    temperature_unit VARCHAR(20) COMMENT '温度单位',
    atmosphere_type ENUM('真空', '惰性气体', '大气', '其他') COMMENT '气氛类型',
    pressure_value FLOAT COMMENT '压力数值',
    pressure_unit VARCHAR(20) COMMENT '压力单位',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (cvt_method_id) REFERENCES cvt_method_details(id)
);
```

#### 12. cvt_crystal_processing（化学气相输运方法晶体处理表）
```sql
CREATE TABLE cvt_crystal_processing (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cvt_method_id INT NOT NULL COMMENT 'CVT方法ID',
    post_processing TEXT COMMENT '后处理方法',
    storage_method ENUM('隔绝空气', '其他') COMMENT '存储方式',
    storage_details TEXT COMMENT '存储详情',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (cvt_method_id) REFERENCES cvt_method_details(id)
);
```

#### 13. cvt_crystal_morphology（化学气相输运方法单晶形态表）
```sql
CREATE TABLE cvt_crystal_morphology (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cvt_method_id INT NOT NULL COMMENT 'CVT方法ID',
    color VARCHAR(100) COMMENT '颜色',
    shape VARCHAR(100) COMMENT '形状',
    typical_size VARCHAR(100) COMMENT '典型尺寸',
    size_unit VARCHAR(20) COMMENT '尺寸单位',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (cvt_method_id) REFERENCES cvt_method_details(id)
);
```

## 关系图

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

## 索引策略

### 主要索引
- `papers.doi`: 唯一索引，用于快速查找文献
- `crystal_materials.chemical_formula`: 普通索引，用于材料搜索
- `crystal_materials.crystal_system`: 普通索引，用于晶系筛选
- `growth_methods.method_type`: 普通索引，用于方法类型筛选
- `growth_methods.paper_id, material_id`: 复合索引，用于关联查询

### 外键约束
- 所有外键都设置了适当的约束
- 支持级联删除和更新
- 确保数据完整性

## 数据示例

### 晶格参数JSON格式
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

### 枚举值说明

#### 方法类型 (method_type)
- `Flux Method/Solution Growth`: 助熔剂法/溶液生长法
- `Chemical Vapor Transport`: 化学气相输运法
- `other`: 其他方法

#### 原料类型 (material_type)
- `助熔剂`: 助熔剂材料
- `其他原料`: 其他原料
- `输运剂`: 输运剂材料

#### 气氛类型 (atmosphere_type)
- `真空`: 真空环境
- `惰性气体`: 惰性气体环境
- `大气`: 大气环境
- `其他`: 其他气氛

## 数据库操作

### 创建表
```bash
# 使用初始化脚本
PYTHONPATH=. python app/database/init_db.py

# 使用Alembic迁移
PYTHONPATH=. alembic upgrade head
```

### 测试数据库
```bash
# 运行测试脚本
python test_db.py
```

### 备份和恢复
```bash
# 备份数据库
mysqldump -u app_user -p crystal_growth > backup.sql

# 恢复数据库
mysql -u app_user -p crystal_growth < backup.sql
```

## 性能优化

### 连接池配置
- 最大连接数: 10
- 最大溢出连接: 20
- 连接预检查: 启用

### 查询优化
- 使用适当的索引
- 避免全表扫描
- 优化JOIN查询
- 使用EXPLAIN分析查询计划

---

*最后更新：2024年9月*
