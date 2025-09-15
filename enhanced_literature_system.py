#!/usr/bin/env python3
"""
增强版文献检索和数据库系统
确保每条数据都经过去重处理后写入数据库
"""

import requests
import time
import logging
import json
from typing import Dict, List, Tuple, Set
from literature_database import LiteratureDatabase
from paper_scoring_system import PaperScoringSystem

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedLiteratureSystem:
    """增强版文献检索和数据库系统"""
    
    def __init__(self, db_path: str = "literature_database.db"):
        self.database = LiteratureDatabase(db_path)
        self.scorer = PaperScoringSystem()
        self.processed_papers: Set[str] = set()  # 用于去重的已处理论文集合
        
    def load_processed_papers(self):
        """加载已处理的论文ID集合"""
        try:
            # 从数据库获取所有已处理的论文ID
            all_papers = self.database.get_all_papers()
            self.processed_papers = {paper['paper_id'] for paper in all_papers if paper['paper_id']}
            logger.info(f"已加载 {len(self.processed_papers)} 篇已处理论文")
        except Exception as e:
            logger.error(f"加载已处理论文失败: {e}")
            self.processed_papers = set()
    
    def is_duplicate(self, paper: Dict) -> bool:
        """检查论文是否重复"""
        paper_id = paper.get('paper_id', '')
        title = paper.get('title', '')
        
        # 检查paper_id是否已存在
        if paper_id and paper_id in self.processed_papers:
            return True
        
        # 检查标题是否重复（备用检查）
        if title:
            # 使用更精确的标题匹配
            existing_papers = self.database.search_papers(title[:30], min_score=0)
            for existing in existing_papers:
                if existing['title'].lower().strip() == title.lower().strip():
                    logger.info(f"发现重复论文（标题匹配）: {title[:50]}...")
                    return True
        
        return False
    
    def process_and_store_paper(self, paper: Dict, search_query: str) -> bool:
        """处理并存储单篇论文"""
        try:
            # 检查是否重复
            if self.is_duplicate(paper):
                logger.info(f"跳过重复论文: {paper.get('title', 'Unknown')[:50]}...")
                return False
            
            # 分析论文
            analysis = self.scorer.analyze_paper(paper)
            
            # 添加搜索查询信息
            analysis['search_query'] = search_query
            
            # 保存到数据库
            success = self.database.save_paper(analysis)
            
            if success:
                # 添加到已处理集合
                paper_id = analysis.get('paper_id', '')
                if paper_id:
                    self.processed_papers.add(paper_id)
                
                logger.info(f"✅ 成功存储: {analysis['title'][:50]}... (评分: {analysis['score']}分)")
                return True
            else:
                logger.error(f"❌ 存储失败: {analysis['title'][:50]}...")
                return False
                
        except Exception as e:
            logger.error(f"处理论文失败: {e}")
            return False
    
    def search_and_store_papers(self, query: str, limit: int = 20) -> Dict:
        """搜索论文并存储到数据库（带去重）"""
        print(f"搜索查询: {query}")
        print("=" * 60)
        
        # 加载已处理论文
        self.load_processed_papers()
        
        # 搜索论文
        papers = self.scorer.search_papers(query, limit)
        
        if not papers:
            print("未找到相关论文")
            return {'success': False, 'message': '未找到相关论文'}
        
        print(f"找到 {len(papers)} 篇论文")
        
        # 处理每篇论文
        processed_count = 0
        duplicate_count = 0
        error_count = 0
        
        for i, paper in enumerate(papers, 1):
            print(f"处理 {i}/{len(papers)}: {paper.get('title', 'Unknown')[:50]}...")
            
            if self.process_and_store_paper(paper, query):
                processed_count += 1
            elif self.is_duplicate(paper):
                duplicate_count += 1
            else:
                error_count += 1
            
            # 避免API速率限制（30%速率）
            time.sleep(2.0)
        
        print(f"\n处理完成:")
        print(f"  新存储: {processed_count} 篇")
        print(f"  重复跳过: {duplicate_count} 篇")
        print(f"  处理失败: {error_count} 篇")
        
        return {
            'success': True,
            'total_found': len(papers),
            'processed': processed_count,
            'duplicates': duplicate_count,
            'errors': error_count
        }
    
    def batch_search_and_store(self, queries: List[str], limit_per_query: int = 20) -> Dict:
        """批量搜索并存储论文（带去重）"""
        print("批量搜索和存储论文（带去重）")
        print("=" * 60)
        
        total_found = 0
        total_processed = 0
        total_duplicates = 0
        total_errors = 0
        
        for i, query in enumerate(queries, 1):
            print(f"\n搜索 {i}/{len(queries)}: {query}")
            
            result = self.search_and_store_papers(query, limit_per_query)
            
            if result['success']:
                total_found += result['total_found']
                total_processed += result['processed']
                total_duplicates += result['duplicates']
                total_errors += result['errors']
            
            # 避免API速率限制（30%速率）
            if i < len(queries):
                print("等待5秒避免速率限制...")
                time.sleep(5)
        
        print(f"\n批量搜索完成:")
        print(f"  总找到: {total_found} 篇")
        print(f"  新存储: {total_processed} 篇")
        print(f"  重复跳过: {total_duplicates} 篇")
        print(f"  处理失败: {total_errors} 篇")
        
        return {
            'success': True,
            'total_found': total_found,
            'total_processed': total_processed,
            'total_duplicates': total_duplicates,
            'total_errors': total_errors
        }
    
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
        
        return stats
    
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
    
    def export_database(self, filename: str = "literature_export.csv"):
        """导出数据库"""
        success = self.database.export_to_csv(filename)
        
        if success:
            print(f"✅ 数据库已导出到: {filename}")
        else:
            print("❌ 导出失败")
        
        return success

def main():
    """主函数 - 演示增强版系统"""
    print("增强版文献检索和数据库系统")
    print("=" * 60)
    
    # 初始化系统
    system = EnhancedLiteratureSystem()
    
    # 获取数据库摘要
    system.get_database_summary()
    
    # 示例：搜索并存储论文
    test_queries = [
        "single crystal growth",
        "flux method crystal",
        "chemical vapor transport"
    ]
    
    print(f"\n开始批量搜索（带去重）...")
    result = system.batch_search_and_store(test_queries, limit_per_query=5)
    
    if result['success']:
        print(f"\n批量搜索完成!")
        
        # 获取下载候选论文
        candidates = system.get_download_candidates(min_score=70, limit=10)
        
        # 搜索数据库
        search_results = system.search_database("crystal growth", min_score=70)
        
        # 导出数据库
        system.export_database("enhanced_literature_export.csv")

if __name__ == "__main__":
    main()
