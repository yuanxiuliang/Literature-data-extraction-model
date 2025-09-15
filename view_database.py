#!/usr/bin/env python3
"""
查看数据库内容的脚本
"""

import sqlite3
import json
from tabulate import tabulate

def view_database():
    """查看数据库内容"""
    print("文献数据库查看器")
    print("=" * 60)
    
    # 连接数据库
    conn = sqlite3.connect('literature_database.db')
    cursor = conn.cursor()
    
    # 1. 数据库概览
    print("\n📊 数据库概览:")
    cursor.execute("SELECT COUNT(*) FROM papers")
    total_papers = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM papers WHERE score >= 70")
    high_score = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM papers WHERE score >= 50 AND score < 70")
    medium_score = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM papers WHERE score < 50")
    low_score = cursor.fetchone()[0]
    
    print(f"  总论文数: {total_papers}")
    print(f"  高分论文 (≥70分): {high_score}")
    print(f"  中等论文 (50-69分): {medium_score}")
    print(f"  低分论文 (<50分): {low_score}")
    
    # 2. 按评分排序的论文列表
    print(f"\n🏆 高分论文 (评分≥70分):")
    cursor.execute("""
        SELECT id, title, score, venue, year, doi
        FROM papers 
        WHERE score >= 70 
        ORDER BY score DESC 
        LIMIT 15
    """)
    
    high_score_papers = cursor.fetchall()
    
    if high_score_papers:
        headers = ["ID", "标题", "评分", "期刊", "年份", "DOI"]
        table_data = []
        for paper in high_score_papers:
            title_short = paper[1][:50] + "..." if len(paper[1]) > 50 else paper[1]
            table_data.append([
                paper[0],
                title_short,
                paper[2],
                paper[3][:30] + "..." if len(paper[3]) > 30 else paper[3],
                paper[4],
                paper[5][:20] + "..." if paper[5] and len(paper[5]) > 20 else paper[5] or "N/A"
            ])
        
        print(tabulate(table_data, headers=headers, tablefmt="grid"))
    else:
        print("  暂无高分论文")
    
    # 3. 期刊分布
    print(f"\n📚 期刊分布:")
    cursor.execute("""
        SELECT venue, COUNT(*) as count 
        FROM papers 
        WHERE venue != 'Unknown' 
        GROUP BY venue 
        ORDER BY count DESC 
        LIMIT 10
    """)
    
    venue_stats = cursor.fetchall()
    if venue_stats:
        headers = ["期刊", "论文数量"]
        print(tabulate(venue_stats, headers=headers, tablefmt="grid"))
    else:
        print("  暂无期刊信息")
    
    # 4. 年份分布
    print(f"\n📅 年份分布:")
    cursor.execute("""
        SELECT year, COUNT(*) as count 
        FROM papers 
        WHERE year IS NOT NULL 
        GROUP BY year 
        ORDER BY year DESC 
        LIMIT 10
    """)
    
    year_stats = cursor.fetchall()
    if year_stats:
        headers = ["年份", "论文数量"]
        print(tabulate(year_stats, headers=headers, tablefmt="grid"))
    else:
        print("  暂无年份信息")
    
    # 5. 搜索查询统计
    print(f"\n🔍 搜索查询统计:")
    cursor.execute("""
        SELECT search_query, COUNT(*) as count 
        FROM papers 
        WHERE search_query IS NOT NULL 
        GROUP BY search_query 
        ORDER BY count DESC
    """)
    
    query_stats = cursor.fetchall()
    if query_stats:
        headers = ["搜索查询", "找到论文数"]
        print(tabulate(query_stats, headers=headers, tablefmt="grid"))
    else:
        print("  暂无搜索查询信息")
    
    # 6. 详细论文信息（可选）
    print(f"\n📄 查看详细论文信息:")
    print("输入论文ID查看详细信息，或按Enter跳过")
    
    try:
        paper_id = input("论文ID: ").strip()
        if paper_id:
            cursor.execute("""
                SELECT title, authors, abstract, score, matched_keywords, recommendation, doi
                FROM papers 
                WHERE id = ?
            """, (paper_id,))
            
            paper = cursor.fetchone()
            if paper:
                print(f"\n📖 论文详情 (ID: {paper_id}):")
                print(f"标题: {paper[0]}")
                print(f"作者: {json.loads(paper[1]) if paper[1] else 'N/A'}")
                print(f"摘要: {paper[2][:200]}..." if paper[2] and len(paper[2]) > 200 else f"摘要: {paper[2] or 'N/A'}")
                print(f"评分: {paper[3]}")
                print(f"匹配关键词: {json.loads(paper[4]) if paper[4] else 'N/A'}")
                print(f"建议: {paper[5]}")
                print(f"DOI: {paper[6]}")
            else:
                print("未找到该论文")
    except KeyboardInterrupt:
        print("\n跳过详细查看")
    
    conn.close()
    print(f"\n✅ 数据库查看完成！")

if __name__ == "__main__":
    view_database()
