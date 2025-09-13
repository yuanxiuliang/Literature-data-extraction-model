# Phase 3.1 使用说明

## 概述

Phase 3.1 实现了从Google Scholar搜索到APS期刊PDF下载的完整工作流程，作为试点验证阶段。

## 功能特点

### 核心功能
- **Google Scholar搜索**: 自动搜索2024年APS期刊的单晶生长相关论文
- **APS PDF提取**: 从Physical Review B、Applied Physics Letters等期刊提取PDF下载链接
- **PDF批量下载**: 支持批量下载、断点续传、失败重试
- **人工干预支持**: 保留人工干预能力，处理需要认证的文献

### 技术特点
- **双模式支持**: 支持requests和Selenium两种模式
- **反爬虫处理**: 请求头伪装、频率控制、代理支持
- **完整日志**: 详细的执行日志和统计信息
- **错误处理**: 完善的错误处理和重试机制

## 安装依赖

```bash
# 安装Python依赖
pip install -r requirements.txt

# 如果使用Selenium模式，需要安装Chrome浏览器
# macOS: brew install --cask google-chrome
# Ubuntu: sudo apt-get install google-chrome-stable
```

## 使用方法

### 1. 基本使用

```bash
# 运行完整工作流程（搜索20篇论文）
python app/main_workflow.py --max-results 20

# 指定下载目录
python app/main_workflow.py --download-dir my_downloads --max-results 10

# 使用Selenium模式（更稳定但需要Chrome）
python app/main_workflow.py --use-selenium --max-results 20
```

### 2. 高级功能

```bash
# 重试失败的下载
python app/main_workflow.py --retry-failed

# 查看需要人工干预的下载列表
python app/main_workflow.py --show-manual

# 查看工作流程统计信息
python app/main_workflow.py --stats
```

### 3. 测试功能

```bash
# 运行完整测试
python test_workflow.py

# 测试各个组件
python -c "from app.services.google_scholar_service import test_google_scholar_service; test_google_scholar_service()"
python -c "from app.services.aps_pdf_extractor import test_aps_pdf_extractor; test_aps_pdf_extractor()"
python -c "from app.services.pdf_downloader import test_pdf_downloader; test_pdf_downloader()"
```

## 参数说明

### 命令行参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `--max-results` | int | 20 | 最大搜索结果数量 |
| `--download-dir` | str | downloads | PDF下载目录 |
| `--use-selenium` | flag | False | 使用Selenium模式 |
| `--retry-failed` | flag | False | 重试失败的下载 |
| `--show-manual` | flag | False | 显示需要人工干预的列表 |
| `--stats` | flag | False | 显示统计信息 |

### 配置选项

可以通过修改代码中的配置来调整行为：

```python
# Google Scholar搜索配置
crystal_growth_keywords = [
    "single crystal growth",
    "crystal growth method", 
    "flux method",
    "chemical vapor transport",
    "CVT",
    "solution growth",
    "crystal synthesis"
]

# APS期刊配置
aps_journals = [
    "Physical Review B",
    "Physical Review Materials",
    "Applied Physics Letters", 
    "Journal of Applied Physics"
]
```

## 输出结果

### 1. 控制台输出

```
开始APS PDF下载工作流程...
最大搜索结果: 20
下载目录: downloads
使用Selenium: False
--------------------------------------------------
进度: 25% - 正在搜索2024年APS期刊论文...
进度: 50% - 正在提取PDF下载链接...
进度: 75% - 正在下载PDF文件...
进度: 100% - 工作流程完成

============================================================
工作流程执行结果
============================================================
总处理论文数: 15
成功下载PDF: 12
失败下载: 3
需要人工干预: 2
执行时间: 45.32秒
成功率: 80.0%
```

### 2. 文件输出

#### 下载的PDF文件
```
downloads/
├── PRB_10_1103_PhysRevB_123_456789.pdf
├── APL_10_1063_5_0123456.pdf
└── ...
```

#### 日志文件
```
workflow.log                    # 详细执行日志
downloads/download_log.json     # 下载记录
downloads/workflow_log.json     # 工作流程记录
```

### 3. 统计信息

```bash
python app/main_workflow.py --stats
```

输出示例：
```
工作流程统计信息:
------------------------------
总运行次数: 3
总处理论文数: 45
总成功下载数: 36
平均成功率: 80.0%

最近运行记录:
  2024-09-15T10:30:00: 处理20篇, 成功16篇
  2024-09-15T11:15:00: 处理15篇, 成功12篇
  2024-09-15T12:00:00: 处理10篇, 成功8篇
```

## 故障排除

### 1. 常见问题

#### Google Scholar搜索失败
```
问题: 搜索不到结果或搜索结果为空
解决: 
1. 检查网络连接
2. 调整搜索关键词
3. 检查反爬虫限制
```

#### PDF提取失败
```
问题: 无法提取PDF下载链接
解决:
1. 使用Selenium模式: --use-selenium
2. 检查目标网站结构变化
3. 更新选择器规则
```

#### 下载失败
```
问题: PDF文件下载失败
解决:
1. 检查网络连接
2. 检查文件权限
3. 检查磁盘空间
4. 使用重试功能: --retry-failed
```

### 2. 调试模式

```bash
# 启用详细日志
export PYTHONPATH=.
python -c "
import logging
logging.basicConfig(level=logging.DEBUG)
from app.main_workflow import main
main()
"
```

### 3. 手动干预

对于需要认证的文献，系统会标记为需要人工干预：

```bash
# 查看需要人工干预的列表
python app/main_workflow.py --show-manual
```

输出示例：
```
需要人工干预的下载 (2 个):
--------------------------------------------------

1. PRB_10_1103_PhysRevB_123_456789.pdf
   URL: https://journals.aps.org/prb/pdf/10.1103/PhysRevB.123.456789
   访问类型: subscription
   时间: 2024-09-15T10:30:00

2. APL_10_1063_5_0123456.pdf
   URL: https://aip.scitation.org/doi/pdf/10.1063/5.0123456
   访问类型: subscription
   时间: 2024-09-15T10:31:00
```

## 性能优化

### 1. 并发下载

```python
# 在workflow_integrator.py中调整并发数
def _download_pdfs(self, pdf_infos, progress_callback=None):
    # 可以添加并发下载逻辑
    pass
```

### 2. 缓存机制

```python
# 添加搜索结果缓存
def search_aps_papers_2024(self, max_results=50, use_cache=True):
    if use_cache and self.cache_exists():
        return self.load_from_cache()
    # ... 搜索逻辑
```

### 3. 代理支持

```python
# 在PDFDownloader中添加代理支持
def __init__(self, download_dir="downloads", proxies=None):
    self.proxies = proxies
    # ...
```

## 扩展功能

### 1. 添加新的出版社

```python
# 在aps_pdf_extractor.py中添加新的出版社支持
def _identify_publisher(self, url):
    if "newpublisher.com" in url:
        return "new_publisher"
    # ... 现有逻辑
```

### 2. 自定义搜索策略

```python
# 在google_scholar_service.py中添加新的搜索策略
def search_with_custom_strategy(self, strategy):
    if strategy == "advanced":
        # 高级搜索逻辑
        pass
```

### 3. 集成数据库

```python
# 将搜索结果保存到数据库
def save_to_database(self, search_results):
    for result in search_results:
        # 保存到MySQL数据库
        pass
```

## 注意事项

1. **法律合规**: 确保遵守相关网站的使用条款和版权法律
2. **频率限制**: 避免过于频繁的请求，以免被网站封禁
3. **数据质量**: 定期验证下载的PDF文件完整性
4. **隐私保护**: 不要泄露下载的学术文献内容
5. **资源管理**: 定期清理临时文件和日志

---

*最后更新：2024年9月*
