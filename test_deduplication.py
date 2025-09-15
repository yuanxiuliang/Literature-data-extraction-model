#!/usr/bin/env python3
"""
测试去重功能
"""

from enhanced_literature_system import EnhancedLiteratureSystem

def test_deduplication():
    """测试去重功能"""
    print("测试去重功能")
    print("=" * 60)
    
    # 初始化系统
    system = EnhancedLiteratureSystem()
    
    # 获取初始数据库状态
    print("初始数据库状态:")
    system.get_database_summary()
    
    # 第一次搜索
    print("\n第一次搜索...")
    result1 = system.search_and_store_papers("single crystal growth", limit=3)
    
    # 获取第一次搜索后的状态
    print("\n第一次搜索后数据库状态:")
    system.get_database_summary()
    
    # 第二次搜索（相同查询，应该去重）
    print("\n第二次搜索（相同查询，应该去重）...")
    result2 = system.search_and_store_papers("single crystal growth", limit=3)
    
    # 获取最终状态
    print("\n最终数据库状态:")
    system.get_database_summary()
    
    # 显示下载候选
    print("\n下载候选论文:")
    candidates = system.get_download_candidates(min_score=70, limit=10)
    
    print(f"\n去重测试结果:")
    print(f"  第一次搜索: 新存储 {result1['processed']} 篇")
    print(f"  第二次搜索: 新存储 {result2['processed']} 篇，重复跳过 {result2['duplicates']} 篇")

if __name__ == "__main__":
    test_deduplication()
