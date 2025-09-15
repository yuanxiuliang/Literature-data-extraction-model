#!/usr/bin/env python3
"""
论文PDF下载必要性评分系统
基于摘要内容判断是否为实验论文，并给出下载评分
"""

import requests
import time
import logging
import re
from typing import Dict, List, Tuple

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PaperScoringSystem:
    """论文评分系统"""
    
    def __init__(self):
        self.base_url = "https://api.semanticscholar.org/graph/v1/paper/search"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json',
        })
        
        # 定义评分关键词和分数
        self.scoring_keywords = {
            # 核心实验关键词 (0-80分)
            'crystal_keywords': {
                'single crystal': 80,
                'crystal growth': 75,
                'crystal synthesis': 75,
                'crystal preparation': 70,
            },
            'synthesis_keywords': {
                'synthesized by': 75,
                'prepared by': 75,
                'grown by': 70,
                'fabricated by': 70,
            },
            'method_keywords': {
                'flux method': 80,
                'chemical vapor transport': 80,
                'Czochralski method': 75,
                'Bridgman method': 75,
            },
            # 实验过程描述 (0-80分)
            'process_keywords': {
                'crystals were grown': 80,
                'samples were prepared': 80,
                'materials were synthesized': 75,
                'crystals were synthesized': 75,
                'single crystals were grown': 80,
                'crystals were prepared': 75,
            },
            'condition_keywords': {
                'using flux': 75,
                'by chemical vapor transport': 80,
                'at temperature': 70,
                'under pressure': 70,
                'for X hours': 65,
                'in vacuum': 65,
                'in atmosphere': 65,
            },
            # 相关性确认 (0-5分)
            'relevance_keywords': {
                'crystal structure': 3,
                'crystal morphology': 3,
                'crystal quality': 3,
                'crystal size': 2,
                'crystal shape': 2,
            }
        }
    
    def search_papers(self, query: str, limit: int = 20) -> List[Dict]:
        """搜索论文"""
        try:
            params = {
                'query': query,
                'limit': limit,
                'year': '2020-2024',
                'fields': 'title,authors,year,abstract,openAccessPdf,externalIds,venue,citationCount,isOpenAccess'
            }
            
            response = self.session.get(self.base_url, params=params, timeout=30)
            
            if response.status_code == 429:
                logger.warning("API速率限制，等待20秒...")
                time.sleep(20)
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
    
    def calculate_score(self, paper: Dict) -> Tuple[int, Dict]:
        """计算论文评分"""
        title = paper.get('title', '') or ''
        abstract = paper.get('abstract', '') or ''
        
        title = title.lower()
        abstract = abstract.lower()
        
        # 合并标题和摘要进行搜索
        text = f"{title} {abstract}"
        
        score = 0
        matched_keywords = {}
        
        # 遍历所有关键词类别
        for category, keywords in self.scoring_keywords.items():
            for keyword, points in keywords.items():
                if keyword.lower() in text:
                    score += points
                    matched_keywords[keyword] = points
                    logger.debug(f"匹配关键词: {keyword} (+{points}分)")
        
        return score, matched_keywords
    
    def get_download_recommendation(self, score: int) -> Tuple[str, str]:
        """获取下载建议"""
        if score >= 70:
            return "必须下载", "强烈实验论文"
        elif score >= 50:
            return "强烈建议下载", "明确实验论文"
        elif score >= 30:
            return "建议下载", "可能实验论文"
        elif score >= 20:
            return "可考虑下载", "相关性一般"
        else:
            return "不建议下载", "相关性低"
    
    def analyze_paper(self, paper: Dict) -> Dict:
        """分析单篇论文"""
        title = paper.get('title', 'Unknown')
        authors = paper.get('authors', [])
        year = paper.get('year', 'Unknown')
        venue = paper.get('venue', 'Unknown')
        abstract = paper.get('abstract', '')
        citation_count = paper.get('citationCount', 0)
        is_open_access = paper.get('isOpenAccess', False)
        external_ids = paper.get('externalIds', {})
        
        # 计算评分
        score, matched_keywords = self.calculate_score(paper)
        
        # 获取下载建议
        recommendation, description = self.get_download_recommendation(score)
        
        return {
            'paper_id': paper.get('paperId', ''),  # 添加paper_id字段
            'title': title,
            'authors': authors,
            'year': year,
            'venue': venue,
            'abstract': abstract,
            'citation_count': citation_count,
            'is_open_access': is_open_access,
            'doi': external_ids.get('DOI', 'Unknown'),
            'score': score,
            'matched_keywords': matched_keywords,
            'recommendation': recommendation,
            'description': description
        }
    
    def batch_analyze_papers(self, papers: List[Dict]) -> List[Dict]:
        """批量分析论文"""
        results = []
        
        for i, paper in enumerate(papers, 1):
            logger.info(f"分析论文 {i}/{len(papers)}: {paper.get('title', 'Unknown')[:50]}...")
            
            analysis = self.analyze_paper(paper)
            results.append(analysis)
            
            # 避免请求过快
            time.sleep(0.7)
        
        return results
    
    def search_and_analyze(self, query: str, limit: int = 20) -> List[Dict]:
        """搜索并分析论文"""
        print(f"搜索查询: {query}")
        print("=" * 60)
        
        # 搜索论文
        papers = self.search_papers(query, limit)
        
        if not papers:
            print("未找到相关论文")
            return []
        
        # 分析论文
        results = self.batch_analyze_papers(papers)
        
        # 按评分排序
        results.sort(key=lambda x: x['score'], reverse=True)
        
        return results
    
    def display_results(self, results: List[Dict], show_details: bool = True):
        """显示分析结果"""
        print(f"\n分析结果 (共{len(results)}篇论文)")
        print("=" * 60)
        
        # 统计信息
        high_score = sum(1 for r in results if r['score'] >= 70)
        medium_score = sum(1 for r in results if 50 <= r['score'] < 70)
        low_score = sum(1 for r in results if r['score'] < 50)
        
        print(f"高分论文 (≥70分): {high_score} 篇")
        print(f"中等论文 (50-69分): {medium_score} 篇")
        print(f"低分论文 (<50分): {low_score} 篇")
        
        if show_details:
            print(f"\n详细结果:")
            print("-" * 60)
            
            for i, result in enumerate(results, 1):
                print(f"\n{i}. {result['title'][:80]}...")
                print(f"   作者: {', '.join([author.get('name', '') for author in result['authors'][:3]])}")
                print(f"   年份: {result['year']} | 期刊: {result['venue']}")
                print(f"   评分: {result['score']}分 | 建议: {result['recommendation']}")
                print(f"   匹配关键词: {', '.join(result['matched_keywords'].keys())}")
                
                if result['doi'] != 'Unknown':
                    print(f"   DOI: {result['doi']}")
                
                if result['abstract']:
                    print(f"   摘要: {result['abstract'][:200]}...")
                
                print("-" * 60)

def main():
    """主函数"""
    print("论文PDF下载必要性评分系统")
    print("=" * 60)
    
    scorer = PaperScoringSystem()
    
    # 测试查询
    test_queries = [
        "single crystal growth",
        "flux method crystal",
        "chemical vapor transport",
        "Czochralski method"
    ]
    
    all_results = []
    
    for query in test_queries:
        print(f"\n搜索查询: {query}")
        results = scorer.search_and_analyze(query, limit=5)
        all_results.extend(results)
        
        # 显示结果
        scorer.display_results(results, show_details=True)
        
        time.sleep(2)  # 避免API速率限制
    
    # 显示总体统计
    print(f"\n总体统计")
    print("=" * 60)
    print(f"总论文数: {len(all_results)}")
    
    high_score = sum(1 for r in all_results if r['score'] >= 70)
    medium_score = sum(1 for r in all_results if 50 <= r['score'] < 70)
    low_score = sum(1 for r in all_results if r['score'] < 50)
    
    print(f"高分论文 (≥70分): {high_score} 篇")
    print(f"中等论文 (50-69分): {medium_score} 篇")
    print(f"低分论文 (<50分): {low_score} 篇")
    
    # 显示高分论文
    high_score_papers = [r for r in all_results if r['score'] >= 70]
    if high_score_papers:
        print(f"\n高分论文列表 (≥70分):")
        print("-" * 60)
        for i, paper in enumerate(high_score_papers, 1):
            print(f"{i}. {paper['title'][:60]}... (评分: {paper['score']}分)")

if __name__ == "__main__":
    main()
