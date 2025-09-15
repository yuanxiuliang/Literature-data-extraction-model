"""
改进的工作流程
集成反爬虫绕过策略和替代搜索源
"""

import logging
from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime
import json
from pathlib import Path

from .anti_crawler_bypass import AntiCrawlerBypass
from .pdf_downloader import PDFDownloader, DownloadResult

logger = logging.getLogger(__name__)

@dataclass
class ImprovedSearchResult:
    """改进的搜索结果"""
    title: str
    authors: str
    year: int
    abstract: str
    pdf_url: Optional[str]
    doi: Optional[str]
    source: str  # Semantic Scholar, arXiv, PubMed等
    is_aps: bool = False

class ImprovedWorkflow:
    """改进的工作流程"""
    
    def __init__(self, download_dir: str = "downloads"):
        self.download_dir = download_dir
        self.bypass = AntiCrawlerBypass()
        self.downloader = PDFDownloader(download_dir=download_dir)
        self.results = []
        
        # 创建下载目录
        Path(download_dir).mkdir(exist_ok=True)
    
    def search_crystal_growth_papers(self, max_results: int = 20) -> List[ImprovedSearchResult]:
        """搜索单晶生长相关论文"""
        logger.info("开始搜索单晶生长相关论文...")
        
        # 搜索关键词
        keywords = [
            "single crystal growth",
            "crystal growth method",
            "flux method",
            "chemical vapor transport",
            "CVT",
            "solution growth",
            "crystal synthesis"
        ]
        
        all_results = []
        
        for keyword in keywords:
            logger.info(f"搜索关键词: {keyword}")
            
            # 使用替代搜索源
            results = self.bypass.search_alternative_sources(keyword)
            
            # 转换为统一格式
            for result in results:
                search_result = ImprovedSearchResult(
                    title=result['title'],
                    authors=result['authors'],
                    year=result['year'],
                    abstract=result['abstract'],
                    pdf_url=result['pdf_url'],
                    doi=result['doi'],
                    source=result['source'],
                    is_aps=self._is_aps_journal(result['title'], result['source'])
                )
                all_results.append(search_result)
        
        # 去重和排序
        unique_results = self._deduplicate_results(all_results)
        sorted_results = sorted(unique_results, key=lambda x: x.year, reverse=True)
        
        # 过滤APS相关论文
        aps_results = [r for r in sorted_results if r.is_aps or self._contains_aps_keywords(r.title)]
        
        logger.info(f"总共找到 {len(sorted_results)} 篇论文，其中 {len(aps_results)} 篇APS相关")
        
        return aps_results[:max_results]
    
    def _is_aps_journal(self, title: str, source: str) -> bool:
        """判断是否为APS期刊"""
        aps_keywords = [
            "Physical Review B",
            "Physical Review Materials",
            "Applied Physics Letters",
            "Journal of Applied Physics",
            "PRB",
            "PRMaterials",
            "APL",
            "JAP"
        ]
        
        title_lower = title.lower()
        for keyword in aps_keywords:
            if keyword.lower() in title_lower:
                return True
        
        return False
    
    def _contains_aps_keywords(self, title: str) -> bool:
        """检查标题是否包含APS相关关键词"""
        aps_keywords = [
            "physical review",
            "applied physics",
            "journal of applied physics"
        ]
        
        title_lower = title.lower()
        return any(keyword in title_lower for keyword in aps_keywords)
    
    def _deduplicate_results(self, results: List[ImprovedSearchResult]) -> List[ImprovedSearchResult]:
        """去重搜索结果"""
        seen_titles = set()
        unique_results = []
        
        for result in results:
            # 使用标题作为去重键
            title_key = result.title.lower().strip()
            if title_key not in seen_titles:
                seen_titles.add(title_key)
                unique_results.append(result)
        
        return unique_results
    
    def download_papers(self, search_results: List[ImprovedSearchResult]) -> List[DownloadResult]:
        """下载论文PDF"""
        logger.info(f"开始下载 {len(search_results)} 篇论文...")
        
        download_results = []
        
        for i, result in enumerate(search_results, 1):
            logger.info(f"下载 {i}/{len(search_results)}: {result.title[:50]}...")
            
            if not result.pdf_url:
                logger.warning(f"论文 {result.title[:50]}... 没有PDF链接")
                download_results.append(DownloadResult(
                    success=False,
                    error_message="没有PDF链接",
                    access_type="unknown"
                ))
                continue
            
            # 生成文件名
            filename = self._generate_filename(result)
            
            # 下载PDF
            download_result = self.downloader.download_pdf(
                pdf_url=result.pdf_url,
                filename=filename,
                access_type="open" if result.source in ["arXiv", "Semantic Scholar"] else "unknown"
            )
            
            download_results.append(download_result)
            
            if download_result.success:
                logger.info(f"✅ 下载成功: {filename}")
            else:
                logger.warning(f"❌ 下载失败: {download_result.error_message}")
        
        return download_results
    
    def _generate_filename(self, result: ImprovedSearchResult) -> str:
        """生成文件名"""
        # 清理标题
        clean_title = "".join(c for c in result.title if c.isalnum() or c in (' ', '-', '_')).rstrip()
        clean_title = clean_title[:50]  # 限制长度
        
        # 添加年份和来源
        filename = f"{result.year}_{result.source}_{clean_title}.pdf"
        
        # 替换不合法字符
        filename = filename.replace(' ', '_').replace('/', '_').replace('\\', '_')
        
        return filename
    
    def run_complete_workflow(self, max_results: int = 20) -> Dict:
        """运行完整工作流程"""
        start_time = datetime.now()
        
        try:
            # 1. 搜索论文
            search_results = self.search_crystal_growth_papers(max_results)
            
            if not search_results:
                logger.warning("未找到任何论文")
                return {
                    "success": False,
                    "message": "未找到任何论文",
                    "search_results": [],
                    "download_results": [],
                    "execution_time": 0
                }
            
            # 2. 下载PDF
            download_results = self.download_papers(search_results)
            
            # 3. 统计结果
            successful_downloads = sum(1 for r in download_results if r.success)
            failed_downloads = len(download_results) - successful_downloads
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            result = {
                "success": True,
                "message": f"工作流程完成，成功下载 {successful_downloads}/{len(download_results)} 篇论文",
                "search_results": search_results,
                "download_results": download_results,
                "statistics": {
                    "total_searched": len(search_results),
                    "successful_downloads": successful_downloads,
                    "failed_downloads": failed_downloads,
                    "success_rate": (successful_downloads / len(download_results) * 100) if download_results else 0,
                    "execution_time": execution_time
                }
            }
            
            # 4. 保存结果
            self._save_results(result)
            
            return result
            
        except Exception as e:
            logger.error(f"工作流程执行失败: {e}")
            return {
                "success": False,
                "message": f"工作流程执行失败: {e}",
                "search_results": [],
                "download_results": [],
                "execution_time": 0
            }
    
    def _save_results(self, result: Dict):
        """保存结果到文件"""
        # 保存搜索结果
        search_file = Path(self.download_dir) / "search_results.json"
        with open(search_file, 'w', encoding='utf-8') as f:
            json.dump([
                {
                    "title": r.title,
                    "authors": r.authors,
                    "year": r.year,
                    "abstract": r.abstract,
                    "pdf_url": r.pdf_url,
                    "doi": r.doi,
                    "source": r.source,
                    "is_aps": r.is_aps
                }
                for r in result["search_results"]
            ], f, indent=2, ensure_ascii=False)
        
        # 保存下载结果
        download_file = Path(self.download_dir) / "download_results.json"
        with open(download_file, 'w', encoding='utf-8') as f:
            json.dump([
                {
                    "success": r.success,
                    "file_path": r.file_path,
                    "file_size": r.file_size,
                    "download_time": r.download_time,
                    "error_message": r.error_message,
                    "access_type": r.access_type
                }
                for r in result["download_results"]
            ], f, indent=2, ensure_ascii=False)
        
        logger.info(f"结果已保存到 {self.download_dir}")
    
    def close(self):
        """关闭资源"""
        self.bypass.close()
        self.downloader.cleanup_failed_downloads()

# 测试函数
def test_improved_workflow():
    """测试改进的工作流程"""
    workflow = ImprovedWorkflow(download_dir="test_downloads")
    
    try:
        print("开始测试改进的工作流程...")
        result = workflow.run_complete_workflow(max_results=5)
        
        print(f"\n工作流程结果:")
        print(f"成功: {result['success']}")
        print(f"消息: {result['message']}")
        
        if result['success']:
            stats = result['statistics']
            print(f"搜索论文数: {stats['total_searched']}")
            print(f"成功下载: {stats['successful_downloads']}")
            print(f"失败下载: {stats['failed_downloads']}")
            print(f"成功率: {stats['success_rate']:.1f}%")
            print(f"执行时间: {stats['execution_time']:.2f}秒")
            
            print(f"\n搜索结果示例:")
            for i, paper in enumerate(result['search_results'][:3], 1):
                print(f"{i}. {paper.title[:60]}...")
                print(f"   来源: {paper.source}")
                print(f"   年份: {paper.year}")
                print(f"   PDF: {'有' if paper.pdf_url else '无'}")
    
    finally:
        workflow.close()

if __name__ == "__main__":
    test_improved_workflow()
