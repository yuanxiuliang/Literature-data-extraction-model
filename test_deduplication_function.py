#!/usr/bin/env python3
"""
测试去重功能 - 故意搜索重复数据
"""

from enhanced_literature_system import EnhancedLiteratureSystem
import time

def test_deduplication():
    """测试去重功能"""
    print("测试去重功能")
    print("=" * 60)
    
    # 初始化系统
    system = EnhancedLiteratureSystem()
    
    # 获取初始数据库状态
    print("初始数据库状态:")
    system.get_database_summary()
    
    # 第一轮搜索 - 搜索一些论文
    print(f"\n第一轮搜索...")
    first_queries = [
        "single crystal growth",
        "flux method crystal"
    ]
    
    print(f"搜索查询: {first_queries}")
    result1 = system.batch_search_and_store(first_queries, limit_per_query=3)
    
    if result1['success']:
        print(f"第一轮结果:")
        print(f"  新存储: {result1['total_processed']} 篇")
        print(f"  重复跳过: {result1['total_duplicates']} 篇")
    
    # 等待一下
    print(f"\n等待5秒...")
    time.sleep(5)
    
    # 第二轮搜索 - 搜索相同的查询（应该触发去重）
    print(f"\n第二轮搜索（相同查询）...")
    second_queries = [
        "single crystal growth",  # 重复查询
        "flux method crystal",    # 重复查询
        "chemical vapor transport"  # 新查询
    ]
    
    print(f"搜索查询: {second_queries}")
    result2 = system.batch_search_and_store(second_queries, limit_per_query=3)
    
    if result2['success']:
        print(f"第二轮结果:")
        print(f"  新存储: {result2['total_processed']} 篇")
        print(f"  重复跳过: {result2['total_duplicates']} 篇")
    
    # 等待一下
    print(f"\n等待5秒...")
    time.sleep(5)
    
    # 第三轮搜索 - 再次搜索相同的查询（应该全部去重）
    print(f"\n第三轮搜索（完全重复查询）...")
    third_queries = [
        "single crystal growth",  # 重复查询
        "flux method crystal",    # 重复查询
        "chemical vapor transport"  # 重复查询
    ]
    
    print(f"搜索查询: {third_queries}")
    result3 = system.batch_search_and_store(third_queries, limit_per_query=3)
    
    if result3['success']:
        print(f"第三轮结果:")
        print(f"  新存储: {result3['total_processed']} 篇")
        print(f"  重复跳过: {result3['total_duplicates']} 篇")
    
    # 获取最终数据库状态
    print(f"\n最终数据库状态:")
    system.get_database_summary()
    
    # 分析去重效果
    print(f"\n去重功能分析:")
    print(f"  第一轮新存储: {result1['total_processed'] if result1 else 0} 篇")
    print(f"  第二轮新存储: {result2['total_processed'] if result2 else 0} 篇")
    print(f"  第三轮新存储: {result3['total_processed'] if result3 else 0} 篇")
    
    total_new = (result1['total_processed'] if result1 else 0) + \
                (result2['total_processed'] if result2 else 0) + \
                (result3['total_processed'] if result3 else 0)
    
    total_duplicates = (result1['total_duplicates'] if result1 else 0) + \
                      (result2['total_duplicates'] if result2 else 0) + \
                      (result3['total_duplicates'] if result3 else 0)
    
    print(f"  总新存储: {total_new} 篇")
    print(f"  总重复跳过: {total_duplicates} 篇")
    
    if total_duplicates > 0:
        print(f"  ✅ 去重功能正常工作！")
    else:
        print(f"  ⚠️ 未检测到去重，可能存在问题")
    
    return {
        'round1': result1,
        'round2': result2,
        'round3': result3,
        'total_new': total_new,
        'total_duplicates': total_duplicates
    }

if __name__ == "__main__":
    result = test_deduplication()
    
    print(f"\n测试完成！")
    print(f"去重功能状态: {'正常' if result['total_duplicates'] > 0 else '异常'}")
