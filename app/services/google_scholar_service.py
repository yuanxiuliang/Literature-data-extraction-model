"""
Google Scholar搜索服务
用于搜索2024年APS期刊的学术论文
"""

import requests
from bs4 import BeautifulSoup
import time
import random
import logging
from typing import List, Dict, Optional
from urllib.parse import urljoin, urlparse
import re
from dataclasses import dataclass
from datetime import datetime

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class SearchResult:
    """搜索结果数据类"""
    title: str
    authors: str
    journal: str
    year: int
    doi: Optional[str]
    url: str
    abstract: Optional[str]
    pdf_url: Optional[str]
    is_aps: bool = False

class GoogleScholarService:
    """Google Scholar搜索服务"""
    
    def __init__(self):
        self.base_url = "https://scholar.google.com"
        self.session = requests.Session()
        self._setup_session()
        
        # APS期刊关键词
        self.aps_journals = [
            "Physical Review B",
            "Physical Review Materials", 
            "Applied Physics Letters",
            "Journal of Applied Physics",
            "PRB",
            "PRMaterials",
            "APL",
            "JAP"
        ]
        
        # 单晶生长相关关键词
        self.crystal_growth_keywords = [
            "single crystal growth",
            "crystal growth method",
            "flux method",
            "chemical vapor transport",
            "CVT",
            "solution growth",
            "crystal synthesis"
        ]
    
    def _setup_session(self):
        """设置会话"""
        self.session.headers.update({
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
    
    def _rate_limit(self):
        """请求频率控制"""
        time.sleep(random.uniform(2, 4))  # 2-4秒随机延迟
    
    def search_aps_papers_2024(self, max_results: int = 50) -> List[SearchResult]:
        """
        搜索2024年APS期刊的单晶生长相关论文
        
        Args:
            max_results: 最大搜索结果数量
            
        Returns:
            List[SearchResult]: 搜索结果列表
        """
        all_results = []
        
        for keyword in self.crystal_growth_keywords:
            logger.info(f"搜索关键词: {keyword}")
            
            # 构建搜索查询
            query = f"{keyword} site:journals.aps.org OR site:aip.scitation.org 2024"
            
            try:
                results = self._search_google_scholar(query, max_results // len(self.crystal_growth_keywords))
                all_results.extend(results)
                
                # 频率控制
                self._rate_limit()
                
            except Exception as e:
                logger.error(f"搜索关键词 '{keyword}' 失败: {e}")
                continue
        
        # 去重和排序
        unique_results = self._deduplicate_results(all_results)
        sorted_results = sorted(unique_results, key=lambda x: x.year, reverse=True)
        
        logger.info(f"总共找到 {len(sorted_results)} 篇APS论文")
        return sorted_results[:max_results]
    
    def _search_google_scholar(self, query: str, max_results: int) -> List[SearchResult]:
        """执行Google Scholar搜索"""
        results = []
        start = 0
        
        while len(results) < max_results:
            # 构建搜索URL
            search_url = f"{self.base_url}/scholar"
            params = {
                'q': query,
                'start': start,
                'num': 10,  # 每页10个结果
                'as_sdt': '0,5',  # 包含PDF链接
                'as_ylo': '2024',  # 2024年
                'as_yhi': '2024'
            }
            
            try:
                response = self.session.get(search_url, params=params, timeout=30)
                response.raise_for_status()
                
                # 解析搜索结果
                page_results = self._parse_search_results(response.text)
                results.extend(page_results)
                
                # 如果没有更多结果，退出
                if len(page_results) < 10:
                    break
                
                start += 10
                
            except Exception as e:
                logger.error(f"搜索请求失败: {e}")
                break
        
        return results[:max_results]
    
    def _parse_search_results(self, html_content: str) -> List[SearchResult]:
        """解析搜索结果页面"""
        soup = BeautifulSoup(html_content, 'html.parser')
        results = []
        
        # 查找搜索结果条目
        search_items = soup.find_all('div', class_='gs_ri')
        
        for item in search_items:
            try:
                result = self._parse_search_item(item)
                if result and self._is_aps_journal(result):
                    result.is_aps = True
                    results.append(result)
            except Exception as e:
                logger.warning(f"解析搜索结果项失败: {e}")
                continue
        
        return results
    
    def _parse_search_item(self, item) -> Optional[SearchResult]:
        """解析单个搜索结果项"""
        try:
            # 标题和链接
            title_elem = item.find('h3', class_='gs_rt')
            if not title_elem:
                return None
            
            title_link = title_elem.find('a')
            if not title_link:
                return None
            
            title = title_link.get_text().strip()
            url = title_link.get('href', '')
            
            # 作者和期刊信息
            authors_elem = item.find('div', class_='gs_a')
            if not authors_elem:
                return None
            
            authors_text = authors_elem.get_text().strip()
            
            # 提取期刊和年份
            journal, year = self._extract_journal_and_year(authors_text)
            
            # 摘要
            abstract_elem = item.find('div', class_='gs_rs')
            abstract = abstract_elem.get_text().strip() if abstract_elem else None
            
            # DOI
            doi = self._extract_doi(authors_text)
            
            # PDF链接
            pdf_url = self._extract_pdf_link(item)
            
            return SearchResult(
                title=title,
                authors=authors_text,
                journal=journal,
                year=year,
                doi=doi,
                url=url,
                abstract=abstract,
                pdf_url=pdf_url
            )
            
        except Exception as e:
            logger.warning(f"解析搜索结果项失败: {e}")
            return None
    
    def _extract_journal_and_year(self, authors_text: str) -> tuple:
        """从作者文本中提取期刊和年份"""
        # 匹配期刊和年份模式
        # 例如: "Author Name - Journal Name, 2024"
        pattern = r'(.+?)\s*-\s*(.+?),\s*(\d{4})'
        match = re.search(pattern, authors_text)
        
        if match:
            journal = match.group(2).strip()
            year = int(match.group(3))
            return journal, year
        
        # 如果没有匹配到，尝试其他模式
        year_match = re.search(r'(\d{4})', authors_text)
        year = int(year_match.group(1)) if year_match else 2024
        
        return "Unknown Journal", year
    
    def _extract_doi(self, text: str) -> Optional[str]:
        """提取DOI"""
        doi_pattern = r'10\.\d+/[^\s]+'
        match = re.search(doi_pattern, text)
        return match.group(0) if match else None
    
    def _extract_pdf_link(self, item) -> Optional[str]:
        """提取PDF链接"""
        # 查找PDF链接
        pdf_links = item.find_all('a', href=True)
        for link in pdf_links:
            href = link.get('href', '')
            if 'pdf' in href.lower() or href.endswith('.pdf'):
                return href
        return None
    
    def _is_aps_journal(self, result: SearchResult) -> bool:
        """判断是否为APS期刊"""
        journal_lower = result.journal.lower()
        url_lower = result.url.lower()
        
        # 检查期刊名称
        for aps_journal in self.aps_journals:
            if aps_journal.lower() in journal_lower:
                return True
        
        # 检查URL
        if 'journals.aps.org' in url_lower or 'aip.scitation.org' in url_lower:
            return True
        
        return False
    
    def _deduplicate_results(self, results: List[SearchResult]) -> List[SearchResult]:
        """去重搜索结果"""
        seen_urls = set()
        unique_results = []
        
        for result in results:
            if result.url not in seen_urls:
                seen_urls.add(result.url)
                unique_results.append(result)
        
        return unique_results
    
    def get_paper_details(self, url: str) -> Optional[SearchResult]:
        """获取论文详细信息"""
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 提取标题
            title_elem = soup.find('h1', class_='article-title') or soup.find('h1')
            title = title_elem.get_text().strip() if title_elem else "Unknown Title"
            
            # 提取作者
            authors_elem = soup.find('div', class_='authors') or soup.find('div', class_='author')
            authors = authors_elem.get_text().strip() if authors_elem else "Unknown Authors"
            
            # 提取期刊
            journal_elem = soup.find('div', class_='journal') or soup.find('div', class_='publication')
            journal = journal_elem.get_text().strip() if journal_elem else "Unknown Journal"
            
            # 提取年份
            year_elem = soup.find('div', class_='year') or soup.find('span', class_='year')
            year = int(year_elem.get_text().strip()) if year_elem else 2024
            
            # 提取DOI
            doi_elem = soup.find('meta', {'name': 'citation_doi'})
            doi = doi_elem.get('content') if doi_elem else None
            
            # 提取摘要
            abstract_elem = soup.find('div', class_='abstract') or soup.find('div', class_='summary')
            abstract = abstract_elem.get_text().strip() if abstract_elem else None
            
            return SearchResult(
                title=title,
                authors=authors,
                journal=journal,
                year=year,
                doi=doi,
                url=url,
                abstract=abstract,
                pdf_url=None,
                is_aps=True
            )
            
        except Exception as e:
            logger.error(f"获取论文详情失败: {e}")
            return None

# 测试函数
def test_google_scholar_service():
    """测试Google Scholar服务"""
    service = GoogleScholarService()
    
    print("开始搜索2024年APS期刊论文...")
    results = service.search_aps_papers_2024(max_results=10)
    
    print(f"\n找到 {len(results)} 篇论文:")
    for i, result in enumerate(results, 1):
        print(f"\n{i}. {result.title}")
        print(f"   作者: {result.authors}")
        print(f"   期刊: {result.journal}")
        print(f"   年份: {result.year}")
        print(f"   URL: {result.url}")
        print(f"   DOI: {result.doi}")
        print(f"   PDF: {result.pdf_url}")

if __name__ == "__main__":
    test_google_scholar_service()
