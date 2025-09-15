#!/usr/bin/env python3
"""
测试开放获取论文的数量和质量
"""

import requests
import time
import logging
from datetime import datetime

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OpenAccessTester:
    """开放获取论文测试器"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        })
    
    def test_arxiv_api(self):
        """测试arXiv API"""
        print("测试arXiv API - 单晶生长相关论文")
        print("=" * 50)
        
        # 测试不同的搜索词
        search_queries = [
            "single crystal growth",
            "crystal growth method",
            "flux method",
            "chemical vapor transport",
            "Czochralski method",
            "Bridgman method"
        ]
        
        total_papers = 0
        
        for query in search_queries:
            try:
                # arXiv API搜索
                url = "http://export.arxiv.org/api/query"
                params = {
                    'search_query': f'all:{query}',
                    'start': 0,
                    'max_results': 100,
                    'sortBy': 'submittedDate',
                    'sortOrder': 'descending'
                }
                
                response = self.session.get(url, params=params, timeout=30)
                
                if response.status_code == 200:
                    # 解析XML响应
                    import xml.etree.ElementTree as ET
                    root = ET.fromstring(response.content)
                    
                    # 计算论文数量
                    entries = root.findall('{http://www.w3.org/2005/Atom}entry')
                    paper_count = len(entries)
                    total_papers += paper_count
                    
                    print(f"查询: {query}")
                    print(f"找到论文: {paper_count} 篇")
                    
                    # 显示前3篇论文信息
                    for i, entry in enumerate(entries[:3]):
                        title = entry.find('{http://www.w3.org/2005/Atom}title').text
                        authors = entry.findall('{http://www.w3.org/2005/Atom}author')
                        author_names = [author.find('{http://www.w3.org/2005/Atom}name').text for author in authors[:2]]
                        published = entry.find('{http://www.w3.org/2005/Atom}published').text
                        
                        print(f"  {i+1}. {title[:60]}...")
                        print(f"     作者: {', '.join(author_names)}")
                        print(f"     日期: {published[:10]}")
                    
                    print()
                    
                else:
                    print(f"查询失败: {query} (状态码: {response.status_code})")
                
                time.sleep(1)  # 避免请求过快
                
            except Exception as e:
                print(f"查询失败: {query} - {e}")
        
        print(f"arXiv总计找到: {total_papers} 篇相关论文")
        return total_papers
    
    def test_semantic_scholar_open_access(self):
        """测试Semantic Scholar开放获取论文"""
        print("\n测试Semantic Scholar - 开放获取论文")
        print("=" * 50)
        
        try:
            url = "https://api.semanticscholar.org/graph/v1/paper/search"
            params = {
                'query': 'single crystal growth',
                'limit': 50,
                'year': '2020-2024',
                'fields': 'title,authors,year,openAccessPdf,venue'
            }
            
            response = self.session.get(url, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                papers = data.get('data', [])
                
                open_access_papers = []
                for paper in papers:
                    if paper.get('openAccessPdf'):
                        open_access_papers.append(paper)
                
                print(f"总论文数: {len(papers)}")
                print(f"开放获取论文数: {len(open_access_papers)}")
                print(f"开放获取比例: {len(open_access_papers)/len(papers)*100:.1f}%")
                
                # 显示开放获取论文信息
                print("\n开放获取论文示例:")
                for i, paper in enumerate(open_access_papers[:5], 1):
                    title = paper.get('title', 'Unknown')
                    authors = paper.get('authors', [])
                    year = paper.get('year', 'Unknown')
                    venue = paper.get('venue', 'Unknown')
                    pdf_url = paper.get('openAccessPdf', {}).get('url', 'Unknown')
                    
                    print(f"\n{i}. {title[:60]}...")
                    print(f"   作者: {', '.join([author.get('name', '') for author in authors[:3]])}")
                    print(f"   年份: {year} | 期刊: {venue}")
                    print(f"   PDF: {pdf_url}")
                
                return len(open_access_papers)
            else:
                print(f"API请求失败: {response.status_code}")
                return 0
                
        except Exception as e:
            print(f"测试失败: {e}")
            return 0
    
    def estimate_database_size(self, arxiv_count, semantic_count):
        """估算数据库规模"""
        print("\n数据库规模估算")
        print("=" * 50)
        
        # 保守估算
        total_estimated = arxiv_count + semantic_count * 2  # 考虑其他来源
        
        print(f"arXiv论文: {arxiv_count} 篇")
        print(f"Semantic Scholar开放获取: {semantic_count} 篇")
        print(f"估算总论文数: {total_estimated} 篇")
        
        # 估算提取成功率
        extraction_rate = 0.3  # 假设30%的论文包含单晶生长方法
        useful_papers = int(total_estimated * extraction_rate)
        
        print(f"预计有用论文: {useful_papers} 篇")
        print(f"预计提取成功率: {extraction_rate*100:.1f}%")
        
        if useful_papers >= 1000:
            print("✅ 数据库规模充足，可以建立有意义的单晶生长方法数据库")
        elif useful_papers >= 100:
            print("⚠️ 数据库规模中等，可以建立基础的单晶生长方法数据库")
        else:
            print("❌ 数据库规模不足，需要寻找更多数据源")

def main():
    """主函数"""
    print("开放获取论文数量和质量测试")
    print("=" * 60)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    tester = OpenAccessTester()
    
    # 测试arXiv
    arxiv_count = tester.test_arxiv_api()
    
    # 测试Semantic Scholar
    semantic_count = tester.test_semantic_scholar_open_access()
    
    # 估算数据库规模
    tester.estimate_database_size(arxiv_count, semantic_count)

if __name__ == "__main__":
    main()
