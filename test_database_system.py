#!/usr/bin/env python3
"""
测试数据库系统
"""

from literature_database import LiteratureDatabase
from paper_scoring_system import PaperScoringSystem

def test_database_system():
    """测试数据库系统"""
    print("测试数据库系统")
    print("=" * 60)
    
    # 初始化数据库
    db = LiteratureDatabase("test_literature.db")
    
    # 初始化评分系统
    scorer = PaperScoringSystem()
    
    # 搜索论文
    print("搜索论文...")
    papers = scorer.search_papers("single crystal growth", limit=3)
    
    if papers:
        print(f"找到 {len(papers)} 篇论文")
        
        # 分析论文
        results = scorer.batch_analyze_papers(papers)
        
        # 保存到数据库
        print("保存到数据库...")
        for paper in results:
            paper['search_query'] = "single crystal growth"
            success = db.save_paper(paper)
            if success:
                print(f"✅ 保存成功: {paper['title'][:50]}... (评分: {paper['score']}分)")
            else:
                print(f"❌ 保存失败: {paper['title'][:50]}...")
        
        # 获取统计信息
        print("\n数据库统计:")
        stats = db.get_database_stats()
        print(f"  总论文数: {stats.get('total_papers', 0)}")
        print(f"  高分论文: {stats.get('high_score_papers', 0)}")
        
        # 获取高分论文
        print("\n高分论文:")
        high_score_papers = db.get_papers_by_score(min_score=70)
        for paper in high_score_papers:
            print(f"  - {paper['title'][:50]}... (评分: {paper['score']}分)")
        
        # 搜索数据库
        print("\n搜索数据库:")
        search_results = db.search_papers("crystal", min_score=70)
        for paper in search_results:
            print(f"  - {paper['title'][:50]}... (评分: {paper['score']}分)")
        
        print("\n✅ 数据库系统测试完成")
    else:
        print("❌ 未找到论文")

if __name__ == "__main__":
    test_database_system()
