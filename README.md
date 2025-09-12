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

- **数据库**：SQLite（本地数据库）
- **后端**：Python + FastAPI
- **前端**：React + Electron（桌面应用）
- **AI模型**：Hugging Face Transformers（本地推理）
- **爬虫**：Selenium + BeautifulSoup（本地爬取）

## 使用说明

1. 通过DOI标识文献
2. 自动提取晶体材料信息（化学式、晶系、空间群、晶格参数）
3. 识别生长方法类型并提取相应参数
4. 存储到本地SQLite数据库
5. 支持数据查询和导出

---

*最后更新：2024年*
