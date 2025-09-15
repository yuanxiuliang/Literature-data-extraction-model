#!/usr/bin/env python3
"""
集成文献检索和数据库管理系统
结合Semantic Scholar API、评分系统和数据库存储
"""

import requests
import time
import logging
import json
from typing import Dict, List, Tuple
from literature_database import LiteratureDatabase
from paper_scoring_system import PaperScoringSystem

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IntegratedLiteratureSystem:
    """集成文献检索和数据库管理系统"""
    
    def __init__(self, db_path: str = "literature_database.db"):
        self.database = LiteratureDatabase(db_path)
        self.scorer = PaperScoringSystem()
        
    def search_and_store_papers(self, query: str, limit: int = 20) -> Dict:
        """搜索论文并存储到数据库"""
        print(f"搜索查询: {query}")
        print("=" * 60)
        
        # 搜索论文
        papers = self.scorer.search_papers(query, limit)
        
        if not papers:
            print("未找到相关论文")
            return {'success': False, 'message': '未找到相关论文'}
        
        # 分析论文
        results = self.scorer.batch_analyze_papers(papers)
        
        # 存储到数据库
        session_id = self.database.save_search_session(query, results)
        
        if session_id > 0:
            print(f"✅ 成功存储 {len(results)} 篇论文到数据库")
            
            # 显示统计信息
            high_score = sum(1 for r in results if r['score'] >= 70)
            medium_score = sum(1 for r in results if 50 <= r['score'] < 70)
            low_score = sum(1 for r in results if r['score'] < 50)
            
            print(f"  高分论文 (≥70分): {high_score} 篇")
            print(f"  中等论文 (50-69分): {medium_score} 篇")
            print(f"  低分论文 (<50分): {low_score} 篇")
            
            return {
                'success': True,
                'session_id': session_id,
                'total_papers': len(results),
                'high_score_papers': high_score,
                'medium_score_papers': medium_score,
                'low_score_papers': low_score
            }
        else:
            print("❌ 存储失败")
            return {'success': False, 'message': '存储失败'}
    
    def batch_search_and_store(self, queries: List[str], limit_per_query: int = 20) -> Dict:
        """批量搜索并存储论文"""
        print("批量搜索和存储论文")
        print("=" * 60)
        
        total_papers = 0
        total_high_score = 0
        total_medium_score = 0
        total_low_score = 0
        
        for i, query in enumerate(queries, 1):
            print(f"\n搜索 {i}/{len(queries)}: {query}")
            
            result = self.search_and_store_papers(query, limit_per_query)
            
            if result['success']:
                total_papers += result['total_papers']
                total_high_score += result['high_score_papers']
                total_medium_score += result['medium_score_papers']
                total_low_score += result['low_score_papers']
            
            # 避免API速率限制
            if i < len(queries):
                print("等待2秒避免速率限制...")
                time.sleep(2)
        
        print(f"\n批量搜索完成:")
        print(f"  总论文数: {total_papers}")
        print(f"  高分论文: {total_high_score}")
        print(f"  中等论文: {total_medium_score}")
        print(f"  低分论文: {total_low_score}")
        
        return {
            'success': True,
            'total_papers': total_papers,
            'high_score_papers': total_high_score,
            'medium_score_papers': total_medium_score,
            'low_score_papers': total_low_score
        }
    
    def get_download_candidates(self, min_score: int = 70, limit: int = 100) -> List[Dict]:
        """获取下载候选论文"""
        papers = self.database.get_papers_by_score(min_score, limit)
        
        print(f"下载候选论文 (评分≥{min_score}分):")
        print("=" * 60)
        
        if not papers:
            print("暂无候选论文")
            return []
        
        # 按评分排序
        papers.sort(key=lambda x: x['score'], reverse=True)
        
        for i, paper in enumerate(papers, 1):
            print(f"{i}. {paper['title'][:60]}...")
            print(f"   评分: {paper['score']}分 | 期刊: {paper['venue']}")
            print(f"   建议: {paper['recommendation']}")
            print(f"   DOI: {paper['doi']}")
            print("-" * 60)
        
        return papers
    
    def search_database(self, keyword: str, min_score: int = 0) -> List[Dict]:
        """在数据库中搜索论文"""
        papers = self.database.search_papers(keyword, min_score)
        
        print(f"数据库搜索结果: '{keyword}' (评分≥{min_score}分)")
        print("=" * 60)
        
        if not papers:
            print("未找到相关论文")
            return []
        
        for i, paper in enumerate(papers, 1):
            print(f"{i}. {paper['title'][:60]}...")
            print(f"   评分: {paper['score']}分 | 期刊: {paper['venue']}")
            print(f"   搜索查询: {paper['search_query']}")
            print("-" * 60)
        
        return papers
    
    def get_database_summary(self) -> Dict:
        """获取数据库摘要"""
        stats = self.database.get_database_stats()
        
        print("数据库摘要")
        print("=" * 60)
        print(f"总论文数: {stats.get('total_papers', 0)}")
        print(f"高分论文 (≥70分): {stats.get('high_score_papers', 0)}")
        print(f"中等论文 (50-69分): {stats.get('medium_score_papers', 0)}")
        print(f"低分论文 (<50分): {stats.get('low_score_papers', 0)}")
        print(f"总搜索次数: {stats.get('total_searches', 0)}")
        
        # 年份统计
        year_stats = stats.get('year_stats', [])
        if year_stats:
            print(f"\n年份分布:")
            for year, count in year_stats[:5]:  # 显示前5年
                print(f"  {year}: {count} 篇")
        
        # 期刊统计
        venue_stats = stats.get('venue_stats', [])
        if venue_stats:
            print(f"\n期刊分布 (前10名):")
            for venue, count in venue_stats:
                print(f"  {venue}: {count} 篇")
        
        return stats
    
    def export_database(self, filename: str = "literature_database.csv"):
        """导出数据库"""
        success = self.database.export_to_csv(filename)
        
        if success:
            print(f"✅ 数据库已导出到: {filename}")
        else:
            print("❌ 导出失败")
        
        return success

def main():
    """主函数 - 演示集成系统"""
    print("集成文献检索和数据库管理系统")
    print("=" * 60)
    
    # 初始化系统
    system = IntegratedLiteratureSystem()
    
    # 获取数据库摘要
    system.get_database_summary()
    
    # 示例：搜索并存储论文
    test_queries = [
        "single crystal growth",
        "flux method crystal",
        "chemical vapor transport"
    ]
    
    print(f"\n开始批量搜索...")
    result = system.batch_search_and_store(test_queries, limit_per_query=5)
    
    if result['success']:
        print(f"\n批量搜索完成!")
        
        # 获取下载候选论文
        candidates = system.get_download_candidates(min_score=70, limit=10)
        
        # 搜索数据库
        search_results = system.search_database("crystal growth", min_score=70)
        
        # 导出数据库
        system.export_database("literature_export.csv")

if __name__ == "__main__":
    main()
