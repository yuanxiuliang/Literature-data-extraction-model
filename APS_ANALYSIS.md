# APS (American Physical Society) PDF获取分析

## 概述

本文档详细分析APS期刊的PDF获取方式，作为Phase 3.1的试点验证目标。

## APS期刊信息

### 目标期刊列表

#### 1. Physical Review B (PRB)
- **URL模式**: `https://journals.aps.org/prb/abstract/`
- **PDF链接**: 通常在文章标题下方
- **访问控制**: 需要订阅或开放获取
- **单晶生长相关**: 凝聚态物理，包含大量单晶生长研究

#### 2. Physical Review Materials (PRMaterials)
- **URL模式**: `https://journals.aps.org/prmaterials/abstract/`
- **PDF链接**: 通常在文章标题下方
- **访问控制**: 需要订阅或开放获取
- **单晶生长相关**: 材料科学专业期刊

#### 3. Applied Physics Letters (APL)
- **URL模式**: `https://aip.scitation.org/doi/`
- **PDF链接**: 通常在文章标题附近
- **访问控制**: 需要订阅或开放获取
- **单晶生长相关**: 应用物理，包含晶体生长方法

#### 4. Journal of Applied Physics (JAP)
- **URL模式**: `https://aip.scitation.org/doi/`
- **PDF链接**: 通常在文章标题附近
- **访问控制**: 需要订阅或开放获取
- **单晶生长相关**: 应用物理期刊

## 网站结构分析

### 1. APS Journals (journals.aps.org)

#### 页面结构
```html
<!-- 文章页面典型结构 -->
<div class="article-header">
    <h1 class="article-title">文章标题</h1>
    <div class="article-actions">
        <a href="/prb/pdf/10.1103/PhysRevB.xxx" class="pdf-link">
            Download PDF
        </a>
    </div>
</div>
```

#### PDF链接特征
- **链接模式**: `/prb/pdf/10.1103/PhysRevB.xxx`
- **完整URL**: `https://journals.aps.org/prb/pdf/10.1103/PhysRevB.xxx`
- **访问权限**: 需要订阅或开放获取

### 2. AIP Scitation (aip.scitation.org)

#### 页面结构
```html
<!-- AIP文章页面典型结构 -->
<div class="article-header">
    <h1 class="article-title">文章标题</h1>
    <div class="article-tools">
        <a href="/doi/pdf/10.1063/xxx" class="pdf-download">
            Download PDF
        </a>
    </div>
</div>
```

#### PDF链接特征
- **链接模式**: `/doi/pdf/10.1063/xxx`
- **完整URL**: `https://aip.scitation.org/doi/pdf/10.1063/xxx`
- **访问权限**: 需要订阅或开放获取

## 技术实现策略

### 1. 出版社识别

```python
def identify_aps_publisher(url: str) -> str:
    """识别APS相关出版社"""
    if "journals.aps.org" in url:
        return "aps_journals"
    elif "aip.scitation.org" in url:
        return "aip_scitation"
    else:
        return "unknown"
```

### 2. PDF链接提取器

#### APS Journals提取器

```python
class APSJournalsExtractor:
    """APS Journals PDF链接提取器"""
    
    def __init__(self):
        self.base_url = "https://journals.aps.org"
        self.selectors = {
            "pdf_link": "a[href*='/pdf/']",
            "article_title": "h1.article-title",
            "doi": "meta[name='citation_doi']"
        }
    
    def extract_pdf_url(self, article_url: str) -> Optional[str]:
        """提取PDF下载链接"""
        try:
            # 1. 访问文章页面
            response = self.session.get(article_url, timeout=30)
            response.raise_for_status()
            
            # 2. 解析HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 3. 查找PDF链接
            pdf_link = soup.select_one(self.selectors["pdf_link"])
            if pdf_link:
                pdf_url = pdf_link.get('href')
                if pdf_url.startswith('/'):
                    pdf_url = self.base_url + pdf_url
                return pdf_url
            
            return None
            
        except Exception as e:
            logging.error(f"APS Journals PDF提取失败: {e}")
            return None
```

#### AIP Scitation提取器

```python
class AIPScitationExtractor:
    """AIP Scitation PDF链接提取器"""
    
    def __init__(self):
        self.base_url = "https://aip.scitation.org"
        self.selectors = {
            "pdf_link": "a[href*='/doi/pdf/']",
            "article_title": "h1.article-title",
            "doi": "meta[name='citation_doi']"
        }
    
    def extract_pdf_url(self, article_url: str) -> Optional[str]:
        """提取PDF下载链接"""
        try:
            # 1. 访问文章页面
            response = self.session.get(article_url, timeout=30)
            response.raise_for_status()
            
            # 2. 解析HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 3. 查找PDF链接
            pdf_link = soup.select_one(self.selectors["pdf_link"])
            if pdf_link:
                pdf_url = pdf_link.get('href')
                if pdf_url.startswith('/'):
                    pdf_url = self.base_url + pdf_url
                return pdf_url
            
            return None
            
        except Exception as e:
            logging.error(f"AIP Scitation PDF提取失败: {e}")
            return None
```

### 3. 统一PDF获取器

```python
class APSPDFExtractor:
    """APS统一PDF获取器"""
    
    def __init__(self):
        self.extractors = {
            "aps_journals": APSJournalsExtractor(),
            "aip_scitation": AIPScitationExtractor()
        }
        self.session = requests.Session()
        self._setup_session()
    
    def _setup_session(self):
        """设置会话"""
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
    
    def extract_pdf_url(self, article_url: str) -> Optional[str]:
        """提取PDF下载链接"""
        publisher = self.identify_aps_publisher(article_url)
        extractor = self.extractors.get(publisher)
        
        if extractor:
            return extractor.extract_pdf_url(article_url)
        else:
            logging.warning(f"未知的APS出版社: {publisher}")
            return None
```

## 反爬虫处理

### 1. 请求头伪装

```python
def setup_aps_session():
    """设置APS专用会话"""
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Cache-Control': 'max-age=0'
    })
    return session
```

### 2. 频率控制

```python
import time
import random

def rate_limit_aps():
    """APS请求频率控制"""
    # APS相对宽松，1-2秒延迟即可
    time.sleep(random.uniform(1, 2))
```

### 3. 错误处理和重试

```python
def extract_with_retry(self, article_url: str, max_retries: int = 3) -> Optional[str]:
    """带重试的PDF链接提取"""
    for attempt in range(max_retries):
        try:
            pdf_url = self.extract_pdf_url(article_url)
            if pdf_url:
                return pdf_url
        except Exception as e:
            logging.warning(f"APS PDF提取失败 (尝试 {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # 指数退避
            else:
                logging.error(f"APS PDF提取最终失败: {e}")
    
    return None
```

## 质量保证

### 1. PDF文件验证

```python
def validate_aps_pdf(file_path: str) -> bool:
    """验证APS PDF文件"""
    try:
        import PyPDF2
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            # 检查页数
            if len(reader.pages) < 1:
                return False
            # 检查是否包含APS标识
            first_page = reader.pages[0]
            text = first_page.extract_text()
            if "Physical Review" in text or "Applied Physics" in text:
                return True
            return False
    except Exception as e:
        logging.error(f"PDF验证失败: {e}")
        return False
```

### 2. 下载成功率监控

```python
class APSDownloadMonitor:
    """APS下载监控器"""
    
    def __init__(self):
        self.stats = {
            "total_attempts": 0,
            "successful_downloads": 0,
            "failed_downloads": 0,
            "success_rate": 0.0
        }
    
    def record_attempt(self, success: bool):
        """记录下载尝试"""
        self.stats["total_attempts"] += 1
        if success:
            self.stats["successful_downloads"] += 1
        else:
            self.stats["failed_downloads"] += 1
        
        self.stats["success_rate"] = (
            self.stats["successful_downloads"] / self.stats["total_attempts"]
        )
    
    def get_stats(self) -> dict:
        """获取统计信息"""
        return self.stats.copy()
```

## 测试用例

### 1. 测试文章URL

```python
test_articles = [
    {
        "url": "https://journals.aps.org/prb/abstract/10.1103/PhysRevB.123.456789",
        "expected_publisher": "aps_journals",
        "expected_pdf_pattern": "/prb/pdf/10.1103/PhysRevB.123.456789"
    },
    {
        "url": "https://aip.scitation.org/doi/10.1063/5.0123456",
        "expected_publisher": "aip_scitation",
        "expected_pdf_pattern": "/doi/pdf/10.1063/5.0123456"
    }
]
```

### 2. 测试流程

```python
def test_aps_pdf_extraction():
    """测试APS PDF提取"""
    extractor = APSPDFExtractor()
    
    for article in test_articles:
        print(f"测试文章: {article['url']}")
        
        # 测试出版社识别
        publisher = identify_aps_publisher(article['url'])
        assert publisher == article['expected_publisher']
        print(f"✓ 出版社识别正确: {publisher}")
        
        # 测试PDF链接提取
        pdf_url = extractor.extract_pdf_url(article['url'])
        if pdf_url:
            assert article['expected_pdf_pattern'] in pdf_url
            print(f"✓ PDF链接提取成功: {pdf_url}")
        else:
            print(f"✗ PDF链接提取失败")
        
        print("-" * 50)
```

## 预期结果

### 1. 技术指标
- **PDF获取成功率**: > 80%
- **平均响应时间**: < 3秒
- **错误率**: < 5%

### 2. 质量指标
- **PDF文件完整性**: 100%
- **文本提取成功率**: > 95%
- **元数据提取准确性**: > 90%

### 3. 稳定性指标
- **连续运行时间**: > 24小时
- **内存使用**: < 500MB
- **CPU使用率**: < 50%

---

*最后更新：2024年9月*
