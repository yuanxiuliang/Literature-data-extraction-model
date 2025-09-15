#!/usr/bin/env python3
"""
搜索至少20篇论文并写入数据库
"""

from enhanced_literature_system import EnhancedLiteratureSystem
import time

def search_20_papers():
    """搜索至少20篇论文"""
    print("搜索至少20篇论文并写入数据库")
    print("=" * 60)
    
    # 初始化系统
    system = EnhancedLiteratureSystem()
    
    # 获取初始数据库状态
    print("初始数据库状态:")
    system.get_database_summary()
    
    # 定义搜索查询（确保能获得至少20篇论文）
    search_queries = [
        "single crystal growth",
        "flux method crystal",
        "chemical vapor transport",
        "Czochralski method",
        "Bridgman method",
        "crystal synthesis",
        "crystal preparation",
        "crystal growth method"
    ]
    
    print(f"\n开始批量搜索...")
    print(f"搜索查询: {len(search_queries)} 个")
    print(f"每个查询限制: 5 篇论文")
    print(f"预计总论文数: {len(search_queries) * 5} 篇")
    
    # 批量搜索
    result = system.batch_search_and_store(search_queries, limit_per_query=5)
    
    if result['success']:
        print(f"\n✅ 批量搜索完成!")
        print(f"  总找到: {result['total_found']} 篇")
        print(f"  新存储: {result['total_processed']} 篇")
        print(f"  重复跳过: {result['total_duplicates']} 篇")
        print(f"  处理失败: {result['total_errors']} 篇")
        
        # 获取最终数据库状态
        print(f"\n最终数据库状态:")
        system.get_database_summary()
        
        # 显示高分论文
        print(f"\n高分论文 (≥70分):")
        high_score_papers = system.get_download_candidates(min_score=70, limit=20)
        
        if high_score_papers:
            print(f"找到 {len(high_score_papers)} 篇高分论文")
        else:
            print("暂无高分论文")
        
        # 导出数据库
        print(f"\n导出数据库...")
        success = system.export_database("literature_20_papers.csv")
        
        if success:
            print("✅ 数据库已导出到 literature_20_papers.csv")
        else:
            print("❌ 导出失败")
        
        return result
    else:
        print("❌ 搜索失败")
        return None

if __name__ == "__main__":
    result = search_20_papers()
    
    if result and result['total_processed'] >= 20:
        print(f"\n🎉 成功！已存储 {result['total_processed']} 篇论文到数据库")
    else:
        print(f"\n⚠️ 存储了 {result['total_processed'] if result else 0} 篇论文，未达到20篇目标")
