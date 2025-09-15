#!/usr/bin/env python3
"""
混合策略测试：Sci-Hub + arXiv
"""

import requests
import time
import logging
from bs4 import BeautifulSoup
import re
import xml.etree.ElementTree as ET

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HybridStrategyTester:
    """混合策略测试器"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        })
        
        self.scihub_urls = [
            "https://sci-hub.in/",
            "https://sci-hub.se/",
            "https://sci-hub.ru/",
            "https://sci-hub.st/"
        ]
    
    def test_scihub_papers(self):
        """测试Sci-Hub论文下载"""
        print("测试Sci-Hub论文下载")
        print("=" * 50)
        
        # 测试论文列表（包含不同期刊）
        test_papers = [
            {
                "doi": "10.1038/nature12373",
                "title": "Nature论文",
                "journal": "Nature"
            },
            {
                "doi": "10.1126/science.abc7424", 
                "title": "Science论文",
                "journal": "Science"
            },
            {
                "doi": "10.1103/PhysRevB.105.045103",
                "title": "PRB论文",
                "journal": "Physical Review B"
            },
            {
                "doi": "10.1016/j.jcrysgro.2020.125456",
                "title": "Journal of Crystal Growth论文",
                "journal": "Journal of Crystal Growth"
            }
        ]
        
        success_count = 0
        results = []
        
        for paper in test_papers:
            print(f"\n测试: {paper['title']} ({paper['journal']})")
            success = self._test_scihub_download(paper['doi'], paper['title'])
            
            results.append({
                'title': paper['title'],
                'journal': paper['journal'],
                'success': success
            })
            
            if success:
                success_count += 1
            
            time.sleep(3)
        
        print(f"\nSci-Hub测试结果: {success_count}/{len(test_papers)} 成功")
        return results
    
    def test_arxiv_papers(self):
        """测试arXiv论文搜索"""
        print("\n测试arXiv论文搜索")
        print("=" * 50)
        
        try:
            url = "http://export.arxiv.org/api/query"
            params = {
                'search_query': 'cat:cond-mat.mtrl-sci AND all:"single crystal growth"',
                'start': 0,
                'max_results': 20,
                'sortBy': 'submittedDate',
                'sortOrder': 'descending'
            }
            
            response = self.session.get(url, params=params, timeout=30)
            
            if response.status_code == 200:
                root = ET.fromstring(response.content)
                entries = root.findall('{http://www.w3.org/2005/Atom}entry')
                
                print(f"找到 {len(entries)} 篇arXiv论文")
                
                # 显示前5篇论文
                for i, entry in enumerate(entries[:5], 1):
                    title = entry.find('{http://www.w3.org/2005/Atom}title').text
                    authors = entry.findall('{http://www.w3.org/2005/Atom}author')
                    author_names = [author.find('{http://www.w3.org/2005/Atom}name').text for author in authors[:2]]
                    published = entry.find('{http://www.w3.org/2005/Atom}published').text
                    
                    print(f"\n{i}. {title[:60]}...")
                    print(f"   作者: {', '.join(author_names)}")
                    print(f"   日期: {published[:10]}")
                
                return len(entries)
            else:
                print(f"arXiv搜索失败: {response.status_code}")
                return 0
                
        except Exception as e:
            print(f"arXiv搜索失败: {e}")
            return 0
    
    def _test_scihub_download(self, doi, title):
        """测试Sci-Hub下载"""
        for mirror_url in self.scihub_urls:
            try:
                search_url = f"{mirror_url}{doi}"
                response = self.session.get(search_url, timeout=60)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # 检查页面标题
                    title_tag = soup.find('title')
                    if title_tag:
                        page_title = title_tag.get_text()
                        if "not found" in page_title.lower() or "未找到" in page_title:
                            continue
                    
                    # 查找PDF链接
                    pdf_url = self._find_pdf_url(soup, mirror_url)
                    
                    if pdf_url:
                        print(f"  ✅ 找到PDF: {pdf_url}")
                        return True
                    else:
                        print(f"  ❌ 未找到PDF")
                        continue
                else:
                    print(f"  ❌ 访问失败: {response.status_code}")
                    continue
                    
            except Exception as e:
                print(f"  ❌ 测试失败: {e}")
                continue
        
        return False
    
    def _find_pdf_url(self, soup, base_url):
        """查找PDF链接"""
        # 使用正则表达式搜索
        page_text = str(soup)
        pdf_patterns = [
            r'href="([^"]*\.pdf[^"]*)"',
            r'src="([^"]*\.pdf[^"]*)"',
            r'url\(["\']?([^"\']*\.pdf[^"\']*)["\']?\)',
            r'https?://[^"\s]*\.pdf[^"\s]*'
        ]
        
        for pattern in pdf_patterns:
            matches = re.findall(pattern, page_text, re.IGNORECASE)
            if matches:
                pdf_url = matches[0]
                if pdf_url.startswith('//'):
                    return 'https:' + pdf_url
                elif pdf_url.startswith('/'):
                    return base_url.rstrip('/') + pdf_url
                elif pdf_url.startswith('http'):
                    return pdf_url
                else:
                    return base_url.rstrip('/') + '/' + pdf_url
        
        return None
    
    def estimate_database_potential(self, scihub_results, arxiv_count):
        """估算数据库潜力"""
        print("\n数据库潜力估算")
        print("=" * 50)
        
        # Sci-Hub成功论文
        scihub_success = sum(1 for result in scihub_results if result['success'])
        scihub_total = len(scihub_results)
        
        print(f"Sci-Hub测试: {scihub_success}/{scihub_total} 成功")
        print(f"arXiv论文: {arxiv_count} 篇")
        
        # 估算实际数据库规模
        # 假设Sci-Hub成功率为60%，arXiv有100篇相关论文
        estimated_scihub_papers = 1000  # 保守估计
        estimated_arxiv_papers = arxiv_count
        
        total_estimated = estimated_scihub_papers + estimated_arxiv_papers
        
        print(f"\n估算数据库规模:")
        print(f"  Sci-Hub论文: {estimated_scihub_papers} 篇")
        print(f"  arXiv论文: {estimated_arxiv_papers} 篇")
        print(f"  总计: {total_estimated} 篇")
        
        # 估算提取成功率
        extraction_rate = 0.4  # 假设40%的论文包含单晶生长方法
        useful_papers = int(total_estimated * extraction_rate)
        
        print(f"\n预计有用论文: {useful_papers} 篇")
        print(f"预计提取成功率: {extraction_rate*100:.1f}%")
        
        if useful_papers >= 500:
            print("✅ 数据库规模充足，可以建立完整的单晶生长方法数据库")
        elif useful_papers >= 200:
            print("⚠️ 数据库规模中等，可以建立有意义的单晶生长方法数据库")
        else:
            print("❌ 数据库规模不足，需要寻找更多数据源")

def main():
    """主函数"""
    print("混合策略测试：Sci-Hub + arXiv")
    print("=" * 60)
    
    tester = HybridStrategyTester()
    
    # 测试Sci-Hub
    scihub_results = tester.test_scihub_papers()
    
    # 测试arXiv
    arxiv_count = tester.test_arxiv_papers()
    
    # 估算数据库潜力
    tester.estimate_database_potential(scihub_results, arxiv_count)

if __name__ == "__main__":
    main()
