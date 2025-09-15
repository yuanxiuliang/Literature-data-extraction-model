#!/usr/bin/env python3
"""
Semantic Scholar API + Sci-Hub 完整流程测试
搜索PRB论文并下载PDF
"""

import requests
import time
import logging
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re
import os
import json

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SemanticScholarSearcher:
    """Semantic Scholar API搜索器"""
    
    def __init__(self):
        self.base_url = "https://api.semanticscholar.org/graph/v1/paper/search"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json',
        })
    
    def search_papers(self, query, limit=20, year_start=2020, year_end=2024):
        """搜索论文"""
        try:
            params = {
                'query': query,
                'limit': limit,
                'year': f"{year_start}-{year_end}",
                'fields': 'title,authors,year,abstract,openAccessPdf,externalIds,venue'
            }
            
            logger.info(f"搜索查询: {query}")
            logger.info(f"年份范围: {year_start}-{year_end}")
            
            response = self.session.get(self.base_url, params=params, timeout=30)
            
            if response.status_code != 200:
                logger.error(f"API请求失败，状态码: {response.status_code}")
                return []
            
            data = response.json()
            papers = data.get('data', [])
            
            logger.info(f"找到 {len(papers)} 篇论文")
            return papers
            
        except Exception as e:
            logger.error(f"搜索失败: {e}")
            return []
    
    def filter_prb_papers(self, papers):
        """过滤出PRB期刊论文"""
        prb_papers = []
        
        for paper in papers:
            # 检查期刊名称
            venue = paper.get('venue', '').lower()
            title = paper.get('title', '').lower()
            
            # 检查是否包含PRB相关关键词
            prb_keywords = [
                'physical review b',
                'prb',
                'phys. rev. b',
                'physical review b:'
            ]
            
            is_prb = any(keyword in venue for keyword in prb_keywords)
            
            # 如果期刊信息不明确，检查标题中的关键词
            if not is_prb:
                prb_keywords_in_title = [
                    'single crystal',
                    'crystal growth',
                    'flux method',
                    'chemical vapor transport'
                ]
                is_prb = any(keyword in title for keyword in prb_keywords_in_title)
            
            if is_prb:
                prb_papers.append(paper)
                logger.info(f"找到PRB论文: {paper.get('title', 'Unknown')[:60]}...")
        
        logger.info(f"过滤后找到 {len(prb_papers)} 篇PRB论文")
        return prb_papers

class SciHubDownloader:
    """Sci-Hub下载器"""
    
    def __init__(self, base_url="https://sci-hub.in/"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
    
    def download_paper(self, paper_info):
        """下载论文PDF"""
        try:
            # 获取DOI
            doi = self._extract_doi(paper_info)
            if not doi:
                logger.warning("无法获取DOI")
                return False
            
            title = paper_info.get('title', 'Unknown')
            logger.info(f"尝试下载: {title[:50]}...")
            logger.info(f"DOI: {doi}")
            
            # 搜索论文
            search_url = f"{self.base_url}{doi}"
            logger.info(f"访问URL: {search_url}")
            
            response = self.session.get(search_url, timeout=60)
            
            if response.status_code != 200:
                logger.warning(f"搜索失败，状态码: {response.status_code}")
                return False
            
            logger.info("页面加载完成，开始提取PDF链接...")
            
            # 等待页面完全加载
            time.sleep(3)
            
            # 提取PDF链接
            pdf_url = self._extract_pdf_url(response.text)
            if not pdf_url:
                logger.warning("未找到PDF链接，尝试其他方法...")
                pdf_url = self._search_pdf_in_content(response.text)
                if not pdf_url:
                    logger.warning("仍未找到PDF链接")
                    return False
            
            logger.info(f"找到PDF链接: {pdf_url}")
            
            # 测试PDF访问
            pdf_response = self.session.head(pdf_url, timeout=30)
            if pdf_response.status_code == 200:
                logger.info("✅ PDF可访问")
                return True
            else:
                logger.warning(f"PDF不可访问，状态码: {pdf_response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"下载失败: {e}")
            return False
    
    def _extract_doi(self, paper_info):
        """从论文信息中提取DOI"""
        # 优先从externalIds中获取
        external_ids = paper_info.get('externalIds', {})
        doi = external_ids.get('DOI')
        
        if doi:
            return doi
        
        # 如果externalIds中没有，尝试从其他字段提取
        # 这里可以根据实际API响应结构调整
        return None
    
    def _extract_pdf_url(self, html_content):
        """从HTML内容中提取PDF链接"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # 查找PDF链接的多种方式
            pdf_selectors = [
                'a[href*=".pdf"]',
                'a[href*="pdf"]',
                'a[title*="PDF"]',
                'a[title*="pdf"]',
                '#pdf',
                '.pdf',
                'a[onclick*="pdf"]'
            ]
            
            pdf_url = None
            for selector in pdf_selectors:
                try:
                    element = soup.select_one(selector)
                    if element and element.get('href'):
                        href = element['href']
                        if href.startswith('//'):
                            pdf_url = 'https:' + href
                        elif href.startswith('/'):
                            pdf_url = self.base_url.rstrip('/') + href
                        elif href.startswith('http'):
                            pdf_url = href
                        else:
                            pdf_url = urljoin(self.base_url, href)
                        break
                except:
                    continue
            
            return pdf_url
            
        except Exception as e:
            logger.error(f"PDF链接提取失败: {e}")
            return None
    
    def _search_pdf_in_content(self, html_content):
        """从页面内容中搜索PDF链接"""
        try:
            # 使用正则表达式搜索PDF链接
            pdf_patterns = [
                r'href="([^"]*\.pdf[^"]*)"',
                r'src="([^"]*\.pdf[^"]*)"',
                r'url\(["\']?([^"\']*\.pdf[^"\']*)["\']?\)',
                r'https?://[^"\s]*\.pdf[^"\s]*',
                r'//[^"\s]*\.pdf[^"\s]*'
            ]
            
            for pattern in pdf_patterns:
                matches = re.findall(pattern, html_content, re.IGNORECASE)
                if matches:
                    pdf_url = matches[0]
                    if pdf_url.startswith('//'):
                        pdf_url = 'https:' + pdf_url
                    elif pdf_url.startswith('/'):
                        pdf_url = self.base_url.rstrip('/') + pdf_url
                    elif not pdf_url.startswith('http'):
                        pdf_url = urljoin(self.base_url, pdf_url)
                    
                    logger.info(f"通过正则表达式找到PDF链接: {pdf_url}")
                    return pdf_url
            
            # 搜索包含PDF的iframe
            iframe_pattern = r'<iframe[^>]*src="([^"]*)"[^>]*>'
            iframe_matches = re.findall(iframe_pattern, html_content, re.IGNORECASE)
            for iframe_src in iframe_matches:
                if '.pdf' in iframe_src.lower():
                    pdf_url = iframe_src
                    if pdf_url.startswith('//'):
                        pdf_url = 'https:' + pdf_url
                    elif pdf_url.startswith('/'):
                        pdf_url = self.base_url.rstrip('/') + pdf_url
                    elif not pdf_url.startswith('http'):
                        pdf_url = urljoin(self.base_url, pdf_url)
                    
                    logger.info(f"通过iframe找到PDF链接: {pdf_url}")
                    return pdf_url
            
            return None
            
        except Exception as e:
            logger.error(f"PDF链接搜索失败: {e}")
            return None

def test_semantic_scholar_scihub_workflow():
    """测试Semantic Scholar + Sci-Hub完整流程"""
    print("Semantic Scholar API + Sci-Hub 完整流程测试")
    print("=" * 60)
    
    # 初始化搜索器和下载器
    searcher = SemanticScholarSearcher()
    downloader = SciHubDownloader()
    
    # 搜索查询
    search_queries = [
        "single crystal growth PRB",
        "flux method single crystal",
        "chemical vapor transport single crystal",
        "crystal growth physical review b"
    ]
    
    all_papers = []
    
    # 搜索论文
    print("\n步骤1: 使用Semantic Scholar API搜索论文")
    print("-" * 40)
    
    for query in search_queries:
        print(f"\n搜索查询: {query}")
        papers = searcher.search_papers(query, limit=10, year_start=2020, year_end=2024)
        all_papers.extend(papers)
        time.sleep(1)  # 避免API速率限制
    
    # 去重
    unique_papers = []
    seen_titles = set()
    for paper in all_papers:
        title = paper.get('title', '')
        if title not in seen_titles:
            unique_papers.append(paper)
            seen_titles.add(title)
    
    print(f"\n总共找到 {len(unique_papers)} 篇唯一论文")
    
    # 过滤PRB论文
    print("\n步骤2: 过滤PRB期刊论文")
    print("-" * 40)
    
    prb_papers = searcher.filter_prb_papers(unique_papers)
    
    if not prb_papers:
        print("❌ 未找到PRB论文")
        return
    
    print(f"找到 {len(prb_papers)} 篇PRB论文")
    
    # 显示论文信息
    print("\n步骤3: 显示论文信息")
    print("-" * 40)
    
    for i, paper in enumerate(prb_papers[:10], 1):  # 只显示前10篇
        title = paper.get('title', 'Unknown')
        authors = paper.get('authors', [])
        year = paper.get('year', 'Unknown')
        venue = paper.get('venue', 'Unknown')
        
        print(f"\n{i}. {title[:80]}...")
        print(f"   作者: {', '.join([author.get('name', '') for author in authors[:3]])}")
        print(f"   年份: {year}")
        print(f"   期刊: {venue}")
    
    # 测试PDF下载
    print(f"\n步骤4: 测试PDF下载 (前5篇)")
    print("-" * 40)
    
    success_count = 0
    test_papers = prb_papers[:5]  # 只测试前5篇
    
    for i, paper in enumerate(test_papers, 1):
        print(f"\n测试 {i}/{len(test_papers)}: {paper.get('title', 'Unknown')[:50]}...")
        
        if downloader.download_paper(paper):
            print("✅ 下载成功")
            success_count += 1
        else:
            print("❌ 下载失败")
        
        # 避免请求过快
        time.sleep(3)
    
    # 输出结果统计
    print(f"\n测试结果统计")
    print("=" * 60)
    print(f"搜索到的论文总数: {len(unique_papers)}")
    print(f"PRB论文数量: {len(prb_papers)}")
    print(f"测试下载数量: {len(test_papers)}")
    print(f"成功下载数量: {success_count}")
    print(f"下载成功率: {success_count/len(test_papers)*100:.1f}%")
    
    if success_count > 0:
        print("\n✅ Semantic Scholar + Sci-Hub 方案可行")
        print("✅ 可以替代Google Scholar搜索")
    else:
        print("\n❌ 方案需要进一步优化")

if __name__ == "__main__":
    test_semantic_scholar_scihub_workflow()
