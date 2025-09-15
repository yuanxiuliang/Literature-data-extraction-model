#!/usr/bin/env python3
"""
文献检索数据库系统
用于存储和管理检索到的文献信息及评分
"""

import sqlite3
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import os

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LiteratureDatabase:
    """文献检索数据库"""
    
    def __init__(self, db_path: str = "literature_database.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """初始化数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建文献表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS papers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                paper_id TEXT UNIQUE,
                title TEXT NOT NULL,
                authors TEXT,
                year INTEGER,
                venue TEXT,
                abstract TEXT,
                doi TEXT,
                citation_count INTEGER,
                is_open_access BOOLEAN,
                score INTEGER,
                matched_keywords TEXT,
                recommendation TEXT,
                description TEXT,
                search_query TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 创建搜索记录表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS search_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query TEXT NOT NULL,
                total_found INTEGER,
                high_score_count INTEGER,
                medium_score_count INTEGER,
                low_score_count INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 创建下载记录表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS download_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                paper_id TEXT,
                download_status TEXT,
                download_url TEXT,
                file_path TEXT,
                download_time TIMESTAMP,
                error_message TEXT,
                FOREIGN KEY (paper_id) REFERENCES papers (paper_id)
            )
        ''')
        
        # 创建索引
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_papers_score ON papers (score)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_papers_query ON papers (search_query)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_papers_created ON papers (created_at)')
        
        conn.commit()
        conn.close()
        
        logger.info("数据库初始化完成")
    
    def save_paper(self, paper_data: Dict) -> bool:
        """保存论文信息"""
        try:
            conn = sqlite3.connect(self.db_path, timeout=30)
            cursor = conn.cursor()
            
            # 准备数据
            paper_id = paper_data.get('paper_id', '')
            title = paper_data.get('title', '')
            authors = json.dumps(paper_data.get('authors', []))
            year = paper_data.get('year')
            venue = paper_data.get('venue', '')
            abstract = paper_data.get('abstract', '')
            doi = paper_data.get('doi', '')
            citation_count = paper_data.get('citation_count', 0)
            is_open_access = paper_data.get('is_open_access', False)
            score = paper_data.get('score', 0)
            matched_keywords = json.dumps(paper_data.get('matched_keywords', {}))
            recommendation = paper_data.get('recommendation', '')
            description = paper_data.get('description', '')
            search_query = paper_data.get('search_query', '')
            
            # 插入或更新数据
            cursor.execute('''
                INSERT OR REPLACE INTO papers (
                    paper_id, title, authors, year, venue, abstract, doi,
                    citation_count, is_open_access, score, matched_keywords,
                    recommendation, description, search_query, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                paper_id, title, authors, year, venue, abstract, doi,
                citation_count, is_open_access, score, matched_keywords,
                recommendation, description, search_query, datetime.now()
            ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"论文已保存: {title[:50]}...")
            return True
            
        except Exception as e:
            logger.error(f"保存论文失败: {e}")
            return False
    
    def save_search_session(self, query: str, results: List[Dict]) -> int:
        """保存搜索会话"""
        try:
            conn = sqlite3.connect(self.db_path, timeout=30)
            cursor = conn.cursor()
            
            # 统计结果
            total_found = len(results)
            high_score_count = sum(1 for r in results if r.get('score', 0) >= 70)
            medium_score_count = sum(1 for r in results if 50 <= r.get('score', 0) < 70)
            low_score_count = sum(1 for r in results if r.get('score', 0) < 50)
            
            # 插入搜索会话
            cursor.execute('''
                INSERT INTO search_sessions (
                    query, total_found, high_score_count, medium_score_count, low_score_count
                ) VALUES (?, ?, ?, ?, ?)
            ''', (query, total_found, high_score_count, medium_score_count, low_score_count))
            
            session_id = cursor.lastrowid
            
            # 保存论文数据
            for paper in results:
                paper['search_query'] = query
                self.save_paper(paper)
            
            conn.commit()
            conn.close()
            
            logger.info(f"搜索会话已保存: {query} (找到{total_found}篇论文)")
            return session_id
            
        except Exception as e:
            logger.error(f"保存搜索会话失败: {e}")
            return -1
    
    def get_papers_by_score(self, min_score: int = 70, limit: int = 100) -> List[Dict]:
        """根据评分获取论文"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM papers 
                WHERE score >= ? 
                ORDER BY score DESC 
                LIMIT ?
            ''', (min_score, limit))
            
            rows = cursor.fetchall()
            conn.close()
            
            # 转换为字典格式
            papers = []
            for row in rows:
                paper = {
                    'id': row[0],
                    'paper_id': row[1],
                    'title': row[2],
                    'authors': json.loads(row[3]) if row[3] else [],
                    'year': row[4],
                    'venue': row[5],
                    'abstract': row[6],
                    'doi': row[7],
                    'citation_count': row[8],
                    'is_open_access': bool(row[9]),
                    'score': row[10],
                    'matched_keywords': json.loads(row[11]) if row[11] else {},
                    'recommendation': row[12],
                    'description': row[13],
                    'search_query': row[14],
                    'created_at': row[15],
                    'updated_at': row[16]
                }
                papers.append(paper)
            
            return papers
            
        except Exception as e:
            logger.error(f"获取论文失败: {e}")
            return []
    
    def get_all_papers(self) -> List[Dict]:
        """获取所有论文"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM papers 
                ORDER BY created_at DESC
            ''')
            
            rows = cursor.fetchall()
            conn.close()
            
            # 转换为字典格式
            papers = []
            for row in rows:
                paper = {
                    'id': row[0],
                    'paper_id': row[1],
                    'title': row[2],
                    'authors': json.loads(row[3]) if row[3] else [],
                    'year': row[4],
                    'venue': row[5],
                    'abstract': row[6],
                    'doi': row[7],
                    'citation_count': row[8],
                    'is_open_access': bool(row[9]),
                    'score': row[10],
                    'matched_keywords': json.loads(row[11]) if row[11] else {},
                    'recommendation': row[12],
                    'description': row[13],
                    'search_query': row[14],
                    'created_at': row[15],
                    'updated_at': row[16]
                }
                papers.append(paper)
            
            return papers
            
        except Exception as e:
            logger.error(f"获取所有论文失败: {e}")
            return []
    
    def get_papers_by_query(self, query: str) -> List[Dict]:
        """根据搜索查询获取论文"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM papers 
                WHERE search_query = ? 
                ORDER BY score DESC
            ''', (query,))
            
            rows = cursor.fetchall()
            conn.close()
            
            # 转换为字典格式
            papers = []
            for row in rows:
                paper = {
                    'id': row[0],
                    'paper_id': row[1],
                    'title': row[2],
                    'authors': json.loads(row[3]) if row[3] else [],
                    'year': row[4],
                    'venue': row[5],
                    'abstract': row[6],
                    'doi': row[7],
                    'citation_count': row[8],
                    'is_open_access': bool(row[9]),
                    'score': row[10],
                    'matched_keywords': json.loads(row[11]) if row[11] else {},
                    'recommendation': row[12],
                    'description': row[13],
                    'search_query': row[14],
                    'created_at': row[15],
                    'updated_at': row[16]
                }
                papers.append(paper)
            
            return papers
            
        except Exception as e:
            logger.error(f"获取论文失败: {e}")
            return []
    
    def get_database_stats(self) -> Dict:
        """获取数据库统计信息"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 总论文数
            cursor.execute('SELECT COUNT(*) FROM papers')
            total_papers = cursor.fetchone()[0]
            
            # 按评分统计
            cursor.execute('SELECT COUNT(*) FROM papers WHERE score >= 70')
            high_score_papers = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM papers WHERE score >= 50 AND score < 70')
            medium_score_papers = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM papers WHERE score < 50')
            low_score_papers = cursor.fetchone()[0]
            
            # 按年份统计
            cursor.execute('SELECT year, COUNT(*) FROM papers GROUP BY year ORDER BY year DESC')
            year_stats = cursor.fetchall()
            
            # 按期刊统计
            cursor.execute('SELECT venue, COUNT(*) FROM papers GROUP BY venue ORDER BY COUNT(*) DESC LIMIT 10')
            venue_stats = cursor.fetchall()
            
            # 搜索会话统计
            cursor.execute('SELECT COUNT(*) FROM search_sessions')
            total_searches = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                'total_papers': total_papers,
                'high_score_papers': high_score_papers,
                'medium_score_papers': medium_score_papers,
                'low_score_papers': low_score_papers,
                'year_stats': year_stats,
                'venue_stats': venue_stats,
                'total_searches': total_searches
            }
            
        except Exception as e:
            logger.error(f"获取统计信息失败: {e}")
            return {}
    
    def search_papers(self, keyword: str, min_score: int = 0) -> List[Dict]:
        """搜索论文"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM papers 
                WHERE (title LIKE ? OR abstract LIKE ? OR venue LIKE ?) 
                AND score >= ?
                ORDER BY score DESC
            ''', (f'%{keyword}%', f'%{keyword}%', f'%{keyword}%', min_score))
            
            rows = cursor.fetchall()
            conn.close()
            
            # 转换为字典格式
            papers = []
            for row in rows:
                paper = {
                    'id': row[0],
                    'paper_id': row[1],
                    'title': row[2],
                    'authors': json.loads(row[3]) if row[3] else [],
                    'year': row[4],
                    'venue': row[5],
                    'abstract': row[6],
                    'doi': row[7],
                    'citation_count': row[8],
                    'is_open_access': bool(row[9]),
                    'score': row[10],
                    'matched_keywords': json.loads(row[11]) if row[11] else {},
                    'recommendation': row[12],
                    'description': row[13],
                    'search_query': row[14],
                    'created_at': row[15],
                    'updated_at': row[16]
                }
                papers.append(paper)
            
            return papers
            
        except Exception as e:
            logger.error(f"搜索论文失败: {e}")
            return []
    
    def export_to_csv(self, filename: str = "literature_database.csv"):
        """导出到CSV文件"""
        try:
            import csv
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM papers ORDER BY score DESC')
            rows = cursor.fetchall()
            
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                # 写入标题行
                writer.writerow([
                    'ID', 'Paper ID', 'Title', 'Authors', 'Year', 'Venue', 'Abstract',
                    'DOI', 'Citation Count', 'Is Open Access', 'Score', 'Matched Keywords',
                    'Recommendation', 'Description', 'Search Query', 'Created At', 'Updated At'
                ])
                
                # 写入数据行
                for row in rows:
                    writer.writerow(row)
            
            conn.close()
            logger.info(f"数据已导出到: {filename}")
            return True
            
        except Exception as e:
            logger.error(f"导出CSV失败: {e}")
            return False

def main():
    """主函数 - 测试数据库功能"""
    print("文献检索数据库系统测试")
    print("=" * 60)
    
    # 初始化数据库
    db = LiteratureDatabase()
    
    # 获取统计信息
    stats = db.get_database_stats()
    
    print(f"数据库统计信息:")
    print(f"  总论文数: {stats.get('total_papers', 0)}")
    print(f"  高分论文 (≥70分): {stats.get('high_score_papers', 0)}")
    print(f"  中等论文 (50-69分): {stats.get('medium_score_papers', 0)}")
    print(f"  低分论文 (<50分): {stats.get('low_score_papers', 0)}")
    print(f"  总搜索次数: {stats.get('total_searches', 0)}")
    
    # 获取高分论文
    high_score_papers = db.get_papers_by_score(min_score=70, limit=10)
    
    if high_score_papers:
        print(f"\n高分论文 (前10篇):")
        print("-" * 60)
        for i, paper in enumerate(high_score_papers, 1):
            print(f"{i}. {paper['title'][:60]}... (评分: {paper['score']}分)")
    else:
        print("\n暂无高分论文")

if __name__ == "__main__":
    main()
