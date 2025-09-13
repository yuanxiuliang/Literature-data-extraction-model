# 出版社网站PDF获取分析

## 概述

本文档详细分析了主流学术出版社网站的PDF获取方式，为Phase 3的PDF下载功能提供技术实现指导。

## 核心策略

### 技术路线重新设计

```
1. 搜索引擎 → 获取文献基本信息
2. 识别出版社 → 确定PDF获取策略
3. 访问出版社网站 → 获取PDF下载链接
4. 下载PDF文件 → 本地存储
```

**关键点**: 搜索引擎只是入口，真正的PDF获取需要针对不同出版社网站实现专门的链接提取规则。

## 主流出版社分析

### 1. Elsevier (ScienceDirect)

#### 网站特点
- **URL模式**: `https://www.sciencedirect.com/science/article/pii/`
- **PDF链接**: 通常在页面右侧或顶部
- **访问控制**: 需要机构订阅或开放获取

#### PDF获取策略
```python
# Elsevier PDF获取规则
def get_elsevier_pdf_url(article_url):
    """
    获取Elsevier文章的PDF下载链接
    """
    # 1. 访问文章页面
    # 2. 查找PDF下载按钮/链接
    # 3. 处理可能的认证要求
    # 4. 返回PDF直接下载链接
    pass
```

#### 技术实现要点
- 使用Selenium处理JavaScript渲染
- 处理登录认证（机构访问）
- 识别开放获取标识
- 处理下载限制和验证码

### 2. Wiley Online Library

#### 网站特点
- **URL模式**: `https://onlinelibrary.wiley.com/doi/`
- **PDF链接**: 通常在文章标题下方
- **访问控制**: 需要订阅或开放获取

#### PDF获取策略
```python
# Wiley PDF获取规则
def get_wiley_pdf_url(article_url):
    """
    获取Wiley文章的PDF下载链接
    """
    # 1. 访问文章页面
    # 2. 查找"Download PDF"按钮
    # 3. 处理订阅检查
    # 4. 获取PDF下载链接
    pass
```

#### 技术实现要点
- 处理动态加载的PDF链接
- 识别订阅状态
- 处理下载权限检查

### 3. SpringerLink

#### 网站特点
- **URL模式**: `https://link.springer.com/article/`
- **PDF链接**: 通常在页面右侧
- **访问控制**: 混合模式（部分开放获取）

#### PDF获取策略
```python
# Springer PDF获取规则
def get_springer_pdf_url(article_url):
    """
    获取Springer文章的PDF下载链接
    """
    # 1. 访问文章页面
    # 2. 查找PDF下载区域
    # 3. 处理开放获取检查
    # 4. 获取PDF链接
    pass
```

### 4. ACS Publications

#### 网站特点
- **URL模式**: `https://pubs.acs.org/doi/`
- **PDF链接**: 通常在文章标题附近
- **访问控制**: 需要订阅

#### PDF获取策略
```python
# ACS PDF获取规则
def get_acs_pdf_url(article_url):
    """
    获取ACS文章的PDF下载链接
    """
    # 1. 访问文章页面
    # 2. 查找"PDF"下载链接
    # 3. 处理订阅验证
    # 4. 获取PDF下载URL
    pass
```

### 5. Nature Publishing Group

#### 网站特点
- **URL模式**: `https://www.nature.com/articles/`
- **PDF链接**: 通常在文章标题下方
- **访问控制**: 需要订阅

#### PDF获取策略
```python
# Nature PDF获取规则
def get_nature_pdf_url(article_url):
    """
    获取Nature文章的PDF下载链接
    """
    # 1. 访问文章页面
    # 2. 查找"Download PDF"按钮
    # 3. 处理订阅检查
    # 4. 获取PDF链接
    pass
```

## 开放获取文献处理

### 1. PubMed Central (PMC)

#### 特点
- 完全开放获取
- 直接PDF下载链接
- 无需认证

#### 获取策略
```python
def get_pmc_pdf_url(pmid):
    """
    从PMC获取PDF下载链接
    """
    # 1. 根据PMID构建PMC URL
    # 2. 直接获取PDF下载链接
    # 3. 无需认证处理
    pass
```

### 2. arXiv

#### 特点
- 预印本服务器
- 直接PDF下载
- 无需认证

#### 获取策略
```python
def get_arxiv_pdf_url(arxiv_id):
    """
    从arXiv获取PDF下载链接
    """
    # 1. 根据arXiv ID构建URL
    # 2. 直接获取PDF链接
    # 3. 无需认证
    pass
```

### 3. PLOS ONE

#### 特点
- 开放获取期刊
- 直接PDF下载
- 无需认证

## 技术实现架构

### 1. 出版社识别器

```python
class PublisherIdentifier:
    """出版社识别器"""
    
    def identify_publisher(self, url: str) -> str:
        """
        根据URL识别出版社
        """
        if "sciencedirect.com" in url:
            return "elsevier"
        elif "onlinelibrary.wiley.com" in url:
            return "wiley"
        elif "link.springer.com" in url:
            return "springer"
        elif "pubs.acs.org" in url:
            return "acs"
        elif "nature.com" in url:
            return "nature"
        # ... 更多出版社
        else:
            return "unknown"
```

### 2. PDF链接提取器

```python
class PDFLinkExtractor:
    """PDF链接提取器"""
    
    def __init__(self):
        self.extractors = {
            "elsevier": ElsevierPDFExtractor(),
            "wiley": WileyPDFExtractor(),
            "springer": SpringerPDFExtractor(),
            "acs": ACSPDFExtractor(),
            "nature": NaturePDFExtractor(),
            "pmc": PMCPDFExtractor(),
            "arxiv": ArxivPDFExtractor(),
        }
    
    def extract_pdf_url(self, article_url: str) -> Optional[str]:
        """
        提取PDF下载链接
        """
        publisher = self.identify_publisher(article_url)
        extractor = self.extractors.get(publisher)
        
        if extractor:
            return extractor.extract(article_url)
        else:
            return None
```

### 3. 各出版社专用提取器

```python
class BasePDFExtractor:
    """PDF链接提取器基类"""
    
    def extract(self, article_url: str) -> Optional[str]:
        """提取PDF链接"""
        raise NotImplementedError

class ElsevierPDFExtractor(BasePDFExtractor):
    """Elsevier PDF链接提取器"""
    
    def extract(self, article_url: str) -> Optional[str]:
        # 1. 使用Selenium访问页面
        # 2. 查找PDF下载按钮
        # 3. 处理认证和权限
        # 4. 返回PDF链接
        pass

class WileyPDFExtractor(BasePDFExtractor):
    """Wiley PDF链接提取器"""
    
    def extract(self, article_url: str) -> Optional[str]:
        # Wiley特定的PDF链接提取逻辑
        pass
```

## 反爬虫处理策略

### 1. 请求头伪装

```python
# 模拟真实浏览器请求
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'keep-alive',
}
```

### 2. 请求频率控制

```python
import time
import random

def rate_limit():
    """请求频率限制"""
    time.sleep(random.uniform(1, 3))  # 随机延迟1-3秒
```

### 3. 代理轮换

```python
class ProxyManager:
    """代理管理器"""
    
    def __init__(self):
        self.proxies = [
            "http://proxy1:port",
            "http://proxy2:port",
            # ... 更多代理
        ]
        self.current_proxy = 0
    
    def get_proxy(self):
        """获取下一个代理"""
        proxy = self.proxies[self.current_proxy]
        self.current_proxy = (self.current_proxy + 1) % len(self.proxies)
        return proxy
```

### 4. 会话管理

```python
import requests

class SessionManager:
    """会话管理器"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(headers)
    
    def get_with_retry(self, url, max_retries=3):
        """带重试的请求"""
        for attempt in range(max_retries):
            try:
                response = self.session.get(url, timeout=30)
                if response.status_code == 200:
                    return response
            except Exception as e:
                if attempt == max_retries - 1:
                    raise e
                time.sleep(2 ** attempt)  # 指数退避
```

## 数据库设计扩展

### 出版社信息表

```sql
CREATE TABLE publishers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    domain VARCHAR(100) NOT NULL,
    pdf_extraction_rule JSON,
    access_type ENUM('open', 'subscription', 'mixed'),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 插入主要出版社信息
INSERT INTO publishers (name, domain, access_type) VALUES
('Elsevier', 'sciencedirect.com', 'subscription'),
('Wiley', 'onlinelibrary.wiley.com', 'subscription'),
('Springer', 'link.springer.com', 'mixed'),
('ACS', 'pubs.acs.org', 'subscription'),
('Nature', 'nature.com', 'subscription'),
('PMC', 'ncbi.nlm.nih.gov', 'open'),
('arXiv', 'arxiv.org', 'open');
```

### PDF下载记录表

```sql
CREATE TABLE pdf_downloads (
    id INT AUTO_INCREMENT PRIMARY KEY,
    search_result_id INT,
    publisher_id INT,
    article_url VARCHAR(500),
    pdf_url VARCHAR(500),
    download_status ENUM('pending', 'extracting', 'downloading', 'completed', 'failed'),
    file_path VARCHAR(500),
    file_size BIGINT,
    download_time DATETIME,
    error_message TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (search_result_id) REFERENCES search_results(id),
    FOREIGN KEY (publisher_id) REFERENCES publishers(id)
);
```

## 实现优先级

### Phase 3.2 实现顺序

1. **高优先级**: 开放获取文献（PMC、arXiv、PLOS等）
2. **中优先级**: 主流商业出版社（Elsevier、Wiley、Springer）
3. **低优先级**: 其他专业出版社

### 技术难点排序

1. **最难**: 需要认证的付费文献
2. **中等**: 反爬虫机制强的网站
3. **较易**: 开放获取文献

## 质量保证

### 1. PDF文件验证

```python
def validate_pdf(file_path: str) -> bool:
    """验证PDF文件完整性"""
    try:
        import PyPDF2
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            return len(reader.pages) > 0
    except:
        return False
```

### 2. 下载成功率监控

```python
def monitor_download_success():
    """监控下载成功率"""
    # 统计各出版社下载成功率
    # 识别问题出版社
    # 调整下载策略
    pass
```

### 3. 错误处理和日志

```python
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('pdf_download.log'),
        logging.StreamHandler()
    ]
)
```

---

*最后更新：2024年9月*
