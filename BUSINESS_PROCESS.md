# 业务流程文档

## 概述

本文档详细描述了单晶生长方法文献数据提取模型的完整业务流程，从文献搜索到数据存储的每个环节。

## 完整业务流程

### 1. 文献搜索阶段 🔍

#### 1.1 搜索策略
- **关键词搜索**: 使用相关关键词搜索学术文献
- **多语言支持**: 支持中英文关键词搜索
- **多数据库搜索**: 集成多个学术搜索引擎

#### 1.2 搜索关键词
```python
# 英文关键词
english_keywords = [
    "single crystal growth",
    "crystal growth method",
    "flux method crystal",
    "chemical vapor transport",
    "crystal growth technique",
    "crystal synthesis",
    "crystal preparation"
]

# 中文关键词
chinese_keywords = [
    "单晶生长",
    "晶体生长方法",
    "助熔剂法",
    "化学气相输运",
    "晶体合成",
    "晶体制备"
]
```

#### 1.3 支持的搜索引擎
- **Google Scholar**: 学术搜索
- **Semantic Scholar**: AI驱动的学术搜索
- **PubMed**: 生物医学文献
- **arXiv**: 预印本服务器
- **Crossref**: 学术文献元数据

#### 1.4 搜索结果处理
- 获取文献基本信息（标题、作者、摘要、DOI、期刊、年份）
- 搜索结果去重和排序
- 相关性评分和筛选

### 2. PDF获取阶段 📥

#### 2.1 下载策略
- **开放获取优先**: 优先下载开放获取的文献
- **批量下载**: 支持批量下载多个PDF
- **断点续传**: 支持下载中断后继续
- **失败重试**: 自动重试失败的下载

#### 2.2 下载源识别
```python
# 开放获取源
open_access_sources = [
    "PubMed Central (PMC)",
    "arXiv",
    "DOAJ",
    "Hindawi",
    "PLOS ONE"
]

# 付费文献处理
paid_sources = [
    "ScienceDirect",
    "Wiley Online Library", 
    "SpringerLink",
    "ACS Publications"
]
```

#### 2.3 文件管理
- PDF文件本地存储
- 文件命名规范（DOI_标题.pdf）
- 文件完整性验证
- 重复文件检测

### 3. PDF解析阶段 📄

#### 3.1 文本提取
- 使用PyMuPDF提取完整文本
- 保持文本格式和结构
- 处理多栏布局
- 提取图片和表格信息

#### 3.2 章节识别
```python
# 常见章节标题
section_keywords = [
    "Abstract", "Introduction", "Experimental", "Methods",
    "Results", "Discussion", "Conclusion", "References",
    "摘要", "引言", "实验", "方法", "结果", "讨论", "结论", "参考文献"
]
```

#### 3.3 文本预处理
- 文本清洗和格式化
- 特殊字符处理
- 中英文混合处理
- 文本分块和分段

### 4. 文献筛选阶段 🎯

#### 4.1 AI模型筛选
- **文献分类模型**: 判断是否包含单晶生长方法
- **方法识别模型**: 识别具体的生长方法类型
- **相关度评分**: 计算文献与单晶生长的相关度

#### 4.2 筛选标准
```python
# 筛选条件
filter_criteria = {
    "contains_crystal_growth": True,  # 包含单晶生长相关内容
    "has_experimental_methods": True,  # 有实验方法描述
    "has_material_info": True,  # 有材料信息
    "has_parameters": True,  # 有实验参数
    "quality_score": 0.7  # 质量评分阈值
}
```

#### 4.3 方法类型识别
- **Flux Method/Solution Growth**: 助熔剂法/溶液生长法
- **Chemical Vapor Transport**: 化学气相输运法
- **Other Methods**: 其他单晶生长方法

### 5. 信息提取阶段 🔬

#### 5.1 晶体材料信息提取
- 化学式识别和验证
- 晶系和空间群提取
- 晶格参数提取
- 材料性质描述

#### 5.2 实验参数提取
- 温度条件（起始温度、终点温度、变温速度）
- 气氛条件（真空、惰性气体、大气等）
- 压力条件（常压、加压数值）
- 时间参数（生长时间、退火时间等）

#### 5.3 生长条件提取
- 助熔剂信息（Flux Method）
- 输运剂信息（CVT Method）
- 设备信息
- 工艺条件

#### 5.4 结果数据提取
- 晶体形态（颜色、形状、尺寸）
- 晶体质量评估
- 产率数据
- 性能参数

### 6. 数据存储阶段 💾

#### 6.1 数据验证
- 数据格式验证
- 数据完整性检查
- 数据一致性验证
- 异常数据标记

#### 6.2 数据库存储
- 存储到MySQL数据库
- 建立表间关联
- 创建索引优化查询
- 数据备份和恢复

#### 6.3 质量控制
- 数据质量评分
- 重复数据检测
- 数据更新和修正
- 质量报告生成

## 技术实现细节

### 1. 搜索模块
```python
class LiteratureSearchService:
    def search_by_keywords(self, keywords: List[str]) -> List[PaperInfo]
    def search_by_doi(self, doi: str) -> PaperInfo
    def filter_results(self, results: List[PaperInfo]) -> List[PaperInfo]
```

### 2. 下载模块
```python
class PDFDownloadService:
    def download_by_doi(self, doi: str) -> str
    def batch_download(self, doi_list: List[str]) -> List[str]
    def verify_pdf(self, file_path: str) -> bool
```

### 3. 解析模块
```python
class PDFParserService:
    def extract_text(self, pdf_path: str) -> str
    def extract_metadata(self, pdf_path: str) -> Dict
    def identify_sections(self, text: str) -> Dict[str, str]
```

### 4. 筛选模块
```python
class LiteratureFilterService:
    def classify_paper(self, text: str) -> bool
    def identify_method_type(self, text: str) -> str
    def calculate_relevance_score(self, text: str) -> float
```

### 5. 提取模块
```python
class InformationExtractionService:
    def extract_material_info(self, text: str) -> MaterialInfo
    def extract_experimental_params(self, text: str) -> Dict
    def extract_growth_conditions(self, text: str) -> Dict
```

## 数据质量控制

### 1. 文献质量评估
- 期刊影响因子
- 引用次数
- 作者权威性
- 实验完整性

### 2. 数据质量检查
- 必填字段完整性
- 数据格式正确性
- 数值范围合理性
- 逻辑一致性

### 3. 质量改进
- 人工审核标记
- 错误数据修正
- 缺失数据补充
- 质量报告生成

## 性能优化

### 1. 并发处理
- 多线程文献搜索
- 并行PDF下载
- 批量文本处理
- 异步数据库操作

### 2. 缓存策略
- 搜索结果缓存
- PDF文件缓存
- 解析结果缓存
- 数据库查询缓存

### 3. 资源管理
- 内存使用优化
- 磁盘空间管理
- 网络带宽控制
- CPU使用平衡

## 错误处理

### 1. 搜索错误
- API限制处理
- 网络超时重试
- 搜索结果为空处理
- 格式错误处理

### 2. 下载错误
- 文件不存在处理
- 下载失败重试
- 文件损坏处理
- 权限错误处理

### 3. 解析错误
- PDF格式不支持
- 文本提取失败
- 编码错误处理
- 内存不足处理

---

*最后更新：2024年9月*
