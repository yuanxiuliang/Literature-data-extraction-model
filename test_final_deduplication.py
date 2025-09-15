#!/usr/bin/env python3
"""
测试最终修复的去重功能
"""

from enhanced_literature_system import EnhancedLiteratureSystem
import time

def test_final_deduplication():
    """测试最终修复的去重功能"""
    print("测试最终修复的去重功能")
    print("=" * 60)
    
    # 初始化系统
    system = EnhancedLiteratureSystem()
    
    # 获取初始数据库状态
    print("初始数据库状态:")
    system.get_database_summary()
    
    # 第一轮搜索
    print(f"\n第一轮搜索...")
    first_queries = ["single crystal growth"]
    
    print(f"搜索查询: {first_queries}")
    result1 = system.batch_search_and_store(first_queries, limit_per_query=2)
    
    if result1['success']:
        print(f"第一轮结果:")
        print(f"  新存储: {result1['total_processed']} 篇")
        print(f"  重复跳过: {result1['total_duplicates']} 篇")
    
    # 等待一下
    print(f"\n等待3秒...")
    time.sleep(3)
    
    # 第二轮搜索 - 完全相同的查询（应该触发去重）
    print(f"\n第二轮搜索（完全重复查询）...")
    second_queries = ["single crystal growth"]  # 完全相同的查询
    
    print(f"搜索查询: {second_queries}")
    result2 = system.batch_search_and_store(second_queries, limit_per_query=2)
    
    if result2['success']:
        print(f"第二轮结果:")
        print(f"  新存储: {result2['total_processed']} 篇")
        print(f"  重复跳过: {result2['total_duplicates']} 篇")
    
    # 获取最终数据库状态
    print(f"\n最终数据库状态:")
    system.get_database_summary()
    
    # 分析去重效果
    print(f"\n去重功能分析:")
    print(f"  第一轮新存储: {result1['total_processed'] if result1 else 0} 篇")
    print(f"  第二轮新存储: {result2['total_processed'] if result2 else 0} 篇")
    print(f"  第二轮重复跳过: {result2['total_duplicates'] if result2 else 0} 篇")
    
    if result2 and result2['total_duplicates'] > 0:
        print(f"  ✅ 去重功能正常工作！")
        return True
    else:
        print(f"  ❌ 去重功能仍有问题")
        return False

if __name__ == "__main__":
    success = test_final_deduplication()
    
    if success:
        print(f"\n🎉 去重功能测试通过！")
    else:
        print(f"\n❌ 去重功能测试失败！")
