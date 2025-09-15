#!/usr/bin/env python3
"""
精确搜索单晶生长相关论文
"""

import requests
import time
import logging
from datetime import datetime
import xml.etree.ElementTree as ET

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PreciseCrystalGrowthSearcher:
    """精确单晶生长论文搜索器"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        })
    
    def search_arxiv_precise(self):
        """精确搜索arXiv单晶生长论文"""
        print("精确搜索arXiv单晶生长论文")
        print("=" * 50)
        
        # 更精确的搜索查询
        precise_queries = [
            "cat:cond-mat.mtrl-sci AND all:\"single crystal growth\"",
            "cat:cond-mat.mtrl-sci AND all:\"flux method\"",
            "cat:cond-mat.mtrl-sci AND all:\"chemical vapor transport\"",
            "cat:cond-mat.mtrl-sci AND all:\"Czochralski\"",
            "cat:cond-mat.mtrl-sci AND all:\"Bridgman method\"",
            "cat:cond-mat.mtrl-sci AND all:\"crystal growth method\""
        ]
        
        all_papers = []
        
        for query in precise_queries:
            try:
                print(f"\n搜索: {query}")
                
                url = "http://export.arxiv.org/api/query"
                params = {
                    'search_query': query,
                    'start': 0,
                    'max_results': 50,  # 减少每页数量，提高精确度
                    'sortBy': 'submittedDate',
                    'sortOrder': 'descending'
                }
                
                response = self.session.get(url, params=params, timeout=30)
                
                if response.status_code == 200:
                    root = ET.fromstring(response.content)
                    entries = root.findall('{http://www.w3.org/2005/Atom}entry')
                    
                    print(f"找到: {len(entries)} 篇论文")
                    
                    # 过滤和显示论文
                    for i, entry in enumerate(entries[:3]):  # 只显示前3篇
                        title = entry.find('{http://www.w3.org/2005/Atom}title').text
                        authors = entry.findall('{http://www.w3.org/2005/Atom}author')
                        author_names = [author.find('{http://www.w3.org/2005/Atom}name').text for author in authors[:2]]
                        published = entry.find('{http://www.w3.org/2005/Atom}published').text
                        summary = entry.find('{http://www.w3.org/2005/Atom}summary').text
                        
                        print(f"  {i+1}. {title[:60]}...")
                        print(f"     作者: {', '.join(author_names)}")
                        print(f"     日期: {published[:10]}")
                        print(f"     摘要: {summary[:100]}...")
                        print()
                    
                    all_papers.extend(entries)
                    
                else:
                    print(f"搜索失败: {response.status_code}")
                
                time.sleep(2)  # 避免请求过快
                
            except Exception as e:
                print(f"搜索失败: {e}")
        
        # 去重
        unique_papers = []
        seen_titles = set()
        for entry in all_papers:
            title = entry.find('{http://www.w3.org/2005/Atom}title').text
            if title not in seen_titles:
                unique_papers.append(entry)
                seen_titles.add(title)
        
        print(f"\n去重后总计: {len(unique_papers)} 篇唯一论文")
        return unique_papers
    
    def analyze_paper_content(self, papers):
        """分析论文内容相关性"""
        print("\n分析论文内容相关性")
        print("=" * 50)
        
        relevant_papers = []
        crystal_keywords = [
            'single crystal', 'crystal growth', 'flux method', 
            'chemical vapor transport', 'Czochralski', 'Bridgman',
            'crystal structure', 'crystal synthesis', 'crystal preparation'
        ]
        
        for entry in papers:
            title = entry.find('{http://www.w3.org/2005/Atom}title').text.lower()
            summary = entry.find('{http://www.w3.org/2005/Atom}summary').text.lower()
            
            # 计算关键词匹配度
            keyword_count = sum(1 for keyword in crystal_keywords if keyword in title or keyword in summary)
            
            if keyword_count >= 2:  # 至少包含2个关键词
                relevant_papers.append((entry, keyword_count))
        
        # 按相关性排序
        relevant_papers.sort(key=lambda x: x[1], reverse=True)
        
        print(f"高度相关论文: {len(relevant_papers)} 篇")
        
        # 显示最相关的论文
        print("\n最相关的论文:")
        for i, (entry, score) in enumerate(relevant_papers[:10], 1):
            title = entry.find('{http://www.w3.org/2005/Atom}title').text
            authors = entry.findall('{http://www.w3.org/2005/Atom}author')
            author_names = [author.find('{http://www.w3.org/2005/Atom}name').text for author in authors[:2]]
            published = entry.find('{http://www.w3.org/2005/Atom}published').text
            
            print(f"\n{i}. {title[:70]}...")
            print(f"   作者: {', '.join(author_names)}")
            print(f"   日期: {published[:10]}")
            print(f"   相关性得分: {score}")
        
        return relevant_papers
    
    def estimate_database_potential(self, relevant_papers):
        """估算数据库潜力"""
        print("\n数据库潜力估算")
        print("=" * 50)
        
        total_papers = len(relevant_papers)
        
        # 估算不同质量等级的论文数量
        high_quality = sum(1 for _, score in relevant_papers if score >= 4)
        medium_quality = sum(1 for _, score in relevant_papers if 2 <= score < 4)
        
        print(f"总相关论文: {total_papers} 篇")
        print(f"高质量论文 (得分≥4): {high_quality} 篇")
        print(f"中等质量论文 (得分2-3): {medium_quality} 篇")
        
        # 估算提取成功率
        high_success_rate = 0.8  # 高质量论文80%成功率
        medium_success_rate = 0.5  # 中等质量论文50%成功率
        
        estimated_extractions = high_quality * high_success_rate + medium_quality * medium_success_rate
        
        print(f"预计成功提取: {estimated_extractions:.0f} 篇")
        
        if estimated_extractions >= 100:
            print("✅ 数据库潜力充足，可以建立有意义的单晶生长方法数据库")
        elif estimated_extractions >= 50:
            print("⚠️ 数据库潜力中等，可以建立基础的单晶生长方法数据库")
        else:
            print("❌ 数据库潜力不足，需要寻找更多数据源")
        
        return estimated_extractions

def main():
    """主函数"""
    print("精确单晶生长论文搜索和分析")
    print("=" * 60)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    searcher = PreciseCrystalGrowthSearcher()
    
    # 精确搜索
    papers = searcher.search_arxiv_precise()
    
    if papers:
        # 分析内容相关性
        relevant_papers = searcher.analyze_paper_content(papers)
        
        # 估算数据库潜力
        searcher.estimate_database_potential(relevant_papers)
    else:
        print("❌ 未找到相关论文")

if __name__ == "__main__":
    main()
