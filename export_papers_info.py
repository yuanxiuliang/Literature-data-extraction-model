#!/usr/bin/env python3
"""
导出搜索到的论文信息
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

class PaperInfoExporter:
    """论文信息导出器"""
    
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
            
            response = self.session.get(self.base_url, params=params, timeout=30)
            
            if response.status_code == 429:
                logger.warning("API速率限制，等待60秒...")
                time.sleep(60)
                response = self.session.get(self.base_url, params=params, timeout=30)
            
            if response.status_code != 200:
                logger.error(f"API请求失败，状态码: {response.status_code}")
                return []
            
            data = response.json()
            papers = data.get('data', [])
            
            return papers
            
        except Exception as e:
            logger.error(f"搜索失败: {e}")
            return []
    
    def export_papers_info(self):
        """导出论文信息"""
        print("导出搜索到的论文信息")
        print("=" * 60)
        
        # 搜索查询
        search_queries = [
            "site:journals.aps.org/prb single crystal growth",
            "physical review b single crystal",
            "PRB crystal growth flux method"
        ]
        
        all_papers = []
        
        # 搜索论文
        for i, query in enumerate(search_queries):
            print(f"搜索查询 {i+1}/{len(search_queries)}: {query}")
            papers = self.search_papers(query, limit=5, year_start=2020, year_end=2024)
            all_papers.extend(papers)
            
            if i < len(search_queries) - 1:
                print("等待30秒避免速率限制...")
                time.sleep(30)
        
        # 去重
        unique_papers = []
        seen_titles = set()
        for paper in all_papers:
            title = paper.get('title', '')
            if title not in seen_titles:
                unique_papers.append(paper)
                seen_titles.add(title)
        
        print(f"\n总共找到 {len(unique_papers)} 篇唯一论文")
        
        # 导出论文信息
        with open('papers_info.txt', 'w', encoding='utf-8') as f:
            f.write("Semantic Scholar API 搜索到的论文信息\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"搜索时间: 2024年\n")
            f.write(f"搜索查询: {', '.join(search_queries)}\n")
            f.write(f"总论文数: {len(unique_papers)}\n\n")
            
            for i, paper in enumerate(unique_papers, 1):
                title = paper.get('title', 'Unknown')
                authors = paper.get('authors', [])
                year = paper.get('year', 'Unknown')
                venue = paper.get('venue', 'Unknown')
                doi = paper.get('externalIds', {}).get('DOI', 'Unknown')
                abstract = paper.get('abstract', '')
                
                f.write(f"{i}. {title}\n")
                f.write(f"   作者: {', '.join([author.get('name', '') for author in authors[:5]])}\n")
                f.write(f"   年份: {year}\n")
                f.write(f"   期刊: {venue}\n")
                f.write(f"   DOI: {doi}\n")
                
                # 生成各种链接
                if doi != 'Unknown':
                    f.write(f"   APS链接: https://journals.aps.org/prb/abstract/{doi}\n")
                    f.write(f"   Sci-Hub链接: https://sci-hub.in/{doi}\n")
                    f.write(f"   Google Scholar: https://scholar.google.com/scholar?q={doi}\n")
                
                if abstract:
                    f.write(f"   摘要: {abstract[:200]}...\n")
                
                f.write("\n" + "-" * 60 + "\n\n")
        
        print(f"论文信息已导出到 papers_info.txt")
        
        # 显示前5篇论文的简要信息
        print("\n前5篇论文简要信息:")
        print("-" * 40)
        for i, paper in enumerate(unique_papers[:5], 1):
            title = paper.get('title', 'Unknown')
            authors = paper.get('authors', [])
            year = paper.get('year', 'Unknown')
            venue = paper.get('venue', 'Unknown')
            doi = paper.get('externalIds', {}).get('DOI', 'Unknown')
            
            print(f"\n{i}. {title[:60]}...")
            print(f"   作者: {', '.join([author.get('name', '') for author in authors[:3]])}")
            print(f"   年份: {year} | 期刊: {venue}")
            print(f"   DOI: {doi}")
            if doi != 'Unknown':
                print(f"   APS: https://journals.aps.org/prb/abstract/{doi}")
                print(f"   Sci-Hub: https://sci-hub.in/{doi}")

if __name__ == "__main__":
    exporter = PaperInfoExporter()
    exporter.export_papers_info()
