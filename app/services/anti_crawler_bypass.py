"""
反爬虫绕过模块
提供多种策略绕过学术网站的反爬虫机制
"""

import requests
import time
import random
import logging
from typing import List, Dict, Optional
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

logger = logging.getLogger(__name__)

class AntiCrawlerBypass:
    """反爬虫绕过类"""
    
    def __init__(self):
        self.session = requests.Session()
        self.driver = None
        self._setup_session()
    
    def _setup_session(self):
        """设置会话"""
        self.session.headers.update(self._get_realistic_headers())
    
    def _get_realistic_headers(self) -> Dict[str, str]:
        """获取真实的浏览器请求头"""
        user_agents = [
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15'
        ]
        
        return {
            'User-Agent': random.choice(user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0',
            'Referer': 'https://www.google.com/'
        }
    
    def _smart_delay(self, min_delay: float = 2.0, max_delay: float = 5.0):
        """智能延迟"""
        delay = random.uniform(min_delay, max_delay)
        time.sleep(delay)
    
    def _exponential_backoff(self, attempt: int, base_delay: float = 1.0):
        """指数退避"""
        delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
        time.sleep(delay)
    
    def bypass_with_requests(self, url: str, max_retries: int = 3) -> Optional[requests.Response]:
        """使用requests绕过反爬虫"""
        for attempt in range(max_retries):
            try:
                # 更新请求头
                self.session.headers.update(self._get_realistic_headers())
                
                # 添加随机延迟
                self._smart_delay()
                
                # 发送请求
                response = self.session.get(url, timeout=30)
                
                if response.status_code == 200:
                    logger.info(f"成功访问: {url}")
                    return response
                elif response.status_code == 403:
                    logger.warning(f"403错误，尝试 {attempt + 1}/{max_retries}")
                    if attempt < max_retries - 1:
                        self._exponential_backoff(attempt)
                        continue
                elif response.status_code == 429:
                    logger.warning(f"429错误，请求过于频繁，等待更长时间")
                    self._smart_delay(5, 10)
                    continue
                else:
                    logger.warning(f"HTTP {response.status_code}错误")
                    
            except requests.exceptions.RequestException as e:
                logger.error(f"请求失败: {e}")
                if attempt < max_retries - 1:
                    self._exponential_backoff(attempt)
                    continue
        
        return None
    
    def bypass_with_selenium(self, url: str) -> Optional[str]:
        """使用Selenium绕过反爬虫"""
        try:
            if not self.driver:
                self._setup_selenium()
            
            # 访问页面
            self.driver.get(url)
            
            # 等待页面加载
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # 随机延迟
            self._smart_delay()
            
            # 获取页面内容
            page_source = self.driver.page_source
            
            logger.info(f"Selenium成功访问: {url}")
            return page_source
            
        except TimeoutException:
            logger.error(f"Selenium访问超时: {url}")
            return None
        except WebDriverException as e:
            logger.error(f"Selenium访问失败: {e}")
            return None
    
    def _setup_selenium(self):
        """设置Selenium"""
        try:
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            chrome_options.add_argument('--user-agent=' + self._get_realistic_headers()['User-Agent'])
            
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
        except Exception as e:
            logger.error(f"Selenium设置失败: {e}")
            self.driver = None
    
    def search_alternative_sources(self, query: str) -> List[Dict]:
        """搜索替代学术源"""
        results = []
        
        # 1. Semantic Scholar API
        try:
            semantic_results = self._search_semantic_scholar(query)
            results.extend(semantic_results)
            logger.info(f"Semantic Scholar找到 {len(semantic_results)} 篇论文")
        except Exception as e:
            logger.error(f"Semantic Scholar搜索失败: {e}")
        
        # 2. arXiv API
        try:
            arxiv_results = self._search_arxiv(query)
            results.extend(arxiv_results)
            logger.info(f"arXiv找到 {len(arxiv_results)} 篇论文")
        except Exception as e:
            logger.error(f"arXiv搜索失败: {e}")
        
        # 3. PubMed API
        try:
            pubmed_results = self._search_pubmed(query)
            results.extend(pubmed_results)
            logger.info(f"PubMed找到 {len(pubmed_results)} 篇论文")
        except Exception as e:
            logger.error(f"PubMed搜索失败: {e}")
        
        return results
    
    def _search_semantic_scholar(self, query: str) -> List[Dict]:
        """搜索Semantic Scholar"""
        url = "https://api.semanticscholar.org/graph/v1/paper/search"
        params = {
            'query': query,
            'limit': 10,
            'fields': 'title,authors,year,abstract,openAccessPdf,externalIds'
        }
        
        response = self.session.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        results = []
        
        for paper in data.get('data', []):
            results.append({
                'title': paper.get('title', ''),
                'authors': ', '.join([author['name'] for author in paper.get('authors', [])]),
                'year': paper.get('year', 0),
                'abstract': paper.get('abstract', ''),
                'pdf_url': paper.get('openAccessPdf', {}).get('url'),
                'doi': paper.get('externalIds', {}).get('DOI'),
                'source': 'Semantic Scholar'
            })
        
        return results
    
    def _search_arxiv(self, query: str) -> List[Dict]:
        """搜索arXiv"""
        url = "http://export.arxiv.org/api/query"
        params = {
            'search_query': query,
            'max_results': 10,
            'sortBy': 'relevance',
            'sortOrder': 'descending'
        }
        
        response = self.session.get(url, params=params)
        response.raise_for_status()
        
        # 解析XML响应
        import xml.etree.ElementTree as ET
        root = ET.fromstring(response.text)
        
        results = []
        for entry in root.findall('{http://www.w3.org/2005/Atom}entry'):
            title = entry.find('{http://www.w3.org/2005/Atom}title').text
            authors = [author.find('{http://www.w3.org/2005/Atom}name').text 
                      for author in entry.findall('{http://www.w3.org/2005/Atom}author')]
            published = entry.find('{http://www.w3.org/2005/Atom}published').text
            year = int(published[:4]) if published else 0
            
            # arXiv PDF链接
            pdf_url = None
            for link in entry.findall('{http://www.w3.org/2005/Atom}link'):
                if link.get('type') == 'application/pdf':
                    pdf_url = link.get('href')
                    break
            
            results.append({
                'title': title,
                'authors': ', '.join(authors),
                'year': year,
                'abstract': entry.find('{http://www.w3.org/2005/Atom}summary').text,
                'pdf_url': pdf_url,
                'doi': None,
                'source': 'arXiv'
            })
        
        return results
    
    def _search_pubmed(self, query: str) -> List[Dict]:
        """搜索PubMed"""
        # 搜索PMID
        search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
        search_params = {
            'db': 'pubmed',
            'term': query,
            'retmax': 10,
            'retmode': 'json'
        }
        
        search_response = self.session.get(search_url, params=search_params)
        search_response.raise_for_status()
        
        search_data = search_response.json()
        pmids = search_data.get('esearchresult', {}).get('idlist', [])
        
        if not pmids:
            return []
        
        # 获取详细信息
        fetch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
        fetch_params = {
            'db': 'pubmed',
            'id': ','.join(pmids),
            'retmode': 'xml'
        }
        
        fetch_response = self.session.get(fetch_url, params=fetch_params)
        fetch_response.raise_for_status()
        
        # 解析XML响应
        import xml.etree.ElementTree as ET
        root = ET.fromstring(fetch_response.text)
        
        results = []
        for article in root.findall('.//PubmedArticle'):
            title_elem = article.find('.//ArticleTitle')
            title = title_elem.text if title_elem is not None else ''
            
            authors = []
            for author in article.findall('.//Author'):
                last_name = author.find('LastName')
                first_name = author.find('ForeName')
                if last_name is not None and first_name is not None:
                    authors.append(f"{first_name.text} {last_name.text}")
            
            year_elem = article.find('.//PubDate/Year')
            year = int(year_elem.text) if year_elem is not None else 0
            
            abstract_elem = article.find('.//AbstractText')
            abstract = abstract_elem.text if abstract_elem is not None else ''
            
            results.append({
                'title': title,
                'authors': ', '.join(authors),
                'year': year,
                'abstract': abstract,
                'pdf_url': None,  # PubMed通常不直接提供PDF
                'doi': None,
                'source': 'PubMed'
            })
        
        return results
    
    def close(self):
        """关闭资源"""
        if self.driver:
            self.driver.quit()
        self.session.close()

# 测试函数
def test_anti_crawler_bypass():
    """测试反爬虫绕过功能"""
    bypass = AntiCrawlerBypass()
    
    # 测试requests绕过
    print("测试requests绕过...")
    response = bypass.bypass_with_requests("https://journals.aps.org")
    if response:
        print(f"✅ requests成功访问，状态码: {response.status_code}")
    else:
        print("❌ requests访问失败")
    
    # 测试替代搜索源
    print("\n测试替代搜索源...")
    results = bypass.search_alternative_sources("single crystal growth")
    print(f"找到 {len(results)} 篇论文")
    
    for i, result in enumerate(results[:3], 1):
        print(f"{i}. {result['title'][:60]}...")
        print(f"   来源: {result['source']}")
        print(f"   年份: {result['year']}")
        print(f"   PDF: {'有' if result['pdf_url'] else '无'}")
    
    bypass.close()

if __name__ == "__main__":
    test_anti_crawler_bypass()
