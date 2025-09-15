#!/usr/bin/env python3
"""
简单去重测试
"""

from enhanced_literature_system import EnhancedLiteratureSystem

def test_simple_deduplication():
    """简单去重测试"""
    print("简单去重测试")
    print("=" * 60)
    
    # 初始化系统
    system = EnhancedLiteratureSystem()
    
    # 获取初始状态
    print("初始数据库状态:")
    system.get_database_summary()
    
    # 第一次搜索
    print("\n第一次搜索...")
    result1 = system.search_and_store_papers("single crystal growth", limit=2)
    
    # 获取第一次搜索后的状态
    print("\n第一次搜索后数据库状态:")
    system.get_database_summary()
    
    # 等待一下
    print("\n等待5秒...")
    import time
    time.sleep(5)
    
    # 第二次搜索（相同查询，应该去重）
    print("\n第二次搜索（相同查询，应该去重）...")
    result2 = system.search_and_store_papers("single crystal growth", limit=2)
    
    # 获取最终状态
    print("\n最终数据库状态:")
    system.get_database_summary()
    
    print(f"\n去重测试结果:")
    print(f"  第一次搜索: 新存储 {result1['processed']} 篇")
    print(f"  第二次搜索: 新存储 {result2['processed']} 篇，重复跳过 {result2['duplicates']} 篇")
    
    # 显示所有论文
    print("\n数据库中的所有论文:")
    all_papers = system.database.get_papers_by_score(min_score=0, limit=100)
    for i, paper in enumerate(all_papers, 1):
        print(f"{i}. {paper['title'][:60]}... (评分: {paper['score']}分)")

if __name__ == "__main__":
    test_simple_deduplication()
