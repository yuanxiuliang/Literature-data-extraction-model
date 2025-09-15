# 文献检索数据库系统

## 系统概述

我们建立了一个完整的文献检索和数据库管理系统，用于存储和管理检索到的文献信息及评分。

## 系统组件

### 1. 论文评分系统 (`paper_scoring_system.py`)

**功能**：
- 使用Semantic Scholar API搜索论文
- 基于摘要内容计算PDF下载必要性评分
- 识别实验论文和单晶生长相关论文

**评分规则**：
- **核心实验关键词** (0-80分)：
  - "single crystal" → 80分
  - "crystal growth" → 75分
  - "flux method" → 80分
  - "chemical vapor transport" → 80分
  - "Czochralski method" → 75分

- **实验过程描述** (0-80分)：
  - "crystals were grown" → 80分
  - "samples were prepared" → 80分
  - "using flux" → 75分
  - "by chemical vapor transport" → 80分

**评分标准**：
- 70-100分：必须下载PDF
- 50-69分：强烈建议下载PDF
- 30-49分：建议下载PDF
- 0-29分：不建议下载PDF

### 2. 文献数据库系统 (`literature_database.py`)

**功能**：
- 存储论文信息和评分
- 管理搜索会话记录
- 提供查询和统计功能

**数据库表结构**：
- `papers`：论文信息表
- `search_sessions`：搜索会话表
- `download_records`：下载记录表

**主要功能**：
- 保存论文信息
- 按评分筛选论文
- 搜索论文
- 导出数据
- 统计信息

### 3. 集成系统 (`integrated_literature_system.py`)

**功能**：
- 整合评分系统和数据库
- 批量搜索和存储
- 获取下载候选论文
- 数据库管理

## 使用流程

### 1. 搜索论文
```python
from integrated_literature_system import IntegratedLiteratureSystem

system = IntegratedLiteratureSystem()
result = system.search_and_store_papers("single crystal growth", limit=20)
```

### 2. 批量搜索
```python
queries = [
    "single crystal growth",
    "flux method crystal", 
    "chemical vapor transport"
]
result = system.batch_search_and_store(queries, limit_per_query=20)
```

### 3. 获取下载候选
```python
candidates = system.get_download_candidates(min_score=70, limit=100)
```

### 4. 搜索数据库
```python
results = system.search_database("crystal growth", min_score=70)
```

### 5. 导出数据
```python
system.export_database("literature_export.csv")
```

## 数据库字段说明

### papers表字段
- `id`：主键
- `paper_id`：论文唯一标识
- `title`：论文标题
- `authors`：作者列表（JSON格式）
- `year`：发表年份
- `venue`：期刊名称
- `abstract`：摘要
- `doi`：DOI
- `citation_count`：引用数
- `is_open_access`：是否开放获取
- `score`：评分
- `matched_keywords`：匹配的关键词（JSON格式）
- `recommendation`：下载建议
- `description`：描述
- `search_query`：搜索查询
- `created_at`：创建时间
- `updated_at`：更新时间

## 系统优势

1. **智能筛选**：基于摘要内容自动识别实验论文
2. **评分系统**：量化PDF下载必要性
3. **数据持久化**：本地数据库存储所有信息
4. **批量处理**：支持大规模文献检索
5. **灵活查询**：多种查询和筛选方式
6. **数据导出**：支持CSV格式导出

## 技术特点

- **API集成**：使用Semantic Scholar API
- **数据库**：SQLite本地数据库
- **评分算法**：基于关键词匹配的评分系统
- **错误处理**：完善的异常处理机制
- **日志记录**：详细的操作日志

## 扩展功能

1. **PDF下载管理**：记录下载状态和错误信息
2. **数据可视化**：生成统计图表
3. **定期更新**：定时搜索新论文
4. **多数据源**：支持其他学术数据库
5. **机器学习**：改进评分算法

## 使用建议

1. **定期搜索**：建议每周运行一次批量搜索
2. **评分筛选**：优先下载70分以上的论文
3. **数据备份**：定期备份数据库文件
4. **监控日志**：关注API限制和错误信息
5. **优化查询**：根据实际需求调整搜索关键词

这个系统为单晶生长方法数据库的建立提供了完整的数据收集和管理解决方案。
