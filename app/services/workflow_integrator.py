"""
工作流程集成器
整合Google Scholar搜索、APS PDF提取和下载功能
"""

import logging
import time
from typing import List, Dict, Optional, Callable
from dataclasses import dataclass
from datetime import datetime
import json
from pathlib import Path

from .google_scholar_service import GoogleScholarService, SearchResult
from .aps_pdf_extractor import APSPDFExtractor, PDFInfo
from .pdf_downloader import PDFDownloader, DownloadResult

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class WorkflowResult:
    """工作流程结果"""
    search_results: List[SearchResult]
    pdf_infos: List[PDFInfo]
    download_results: List[DownloadResult]
    total_processed: int
    successful_downloads: int
    failed_downloads: int
    manual_intervention_required: int
    execution_time: float

class WorkflowIntegrator:
    """工作流程集成器"""
    
    def __init__(self, download_dir: str = "downloads", use_selenium: bool = True):
        self.download_dir = download_dir
        self.use_selenium = use_selenium
        
        # 初始化服务
        self.google_scholar = GoogleScholarService()
        self.aps_extractor = APSPDFExtractor(use_selenium=use_selenium)
        self.pdf_downloader = PDFDownloader(download_dir=download_dir)
        
        # 工作流程日志
        self.workflow_log = []
        
        logger.info("工作流程集成器初始化完成")
    
    def run_complete_workflow(self, max_search_results: int = 20, 
                            progress_callback: Optional[Callable] = None) -> WorkflowResult:
        """
        运行完整的工作流程
        
        Args:
            max_search_results: 最大搜索结果数量
            progress_callback: 进度回调函数
            
        Returns:
            WorkflowResult: 工作流程结果
        """
        start_time = time.time()
        
        try:
            logger.info("开始完整工作流程")
            
            # 步骤1: Google Scholar搜索
            if progress_callback:
                progress_callback(0, 100, "正在搜索2024年APS期刊论文...")
            
            search_results = self._search_aps_papers(max_search_results)
            logger.info(f"搜索完成，找到 {len(search_results)} 篇论文")
            
            if not search_results:
                logger.warning("未找到任何APS论文")
                return self._create_empty_result(start_time)
            
            # 步骤2: 提取PDF信息
            if progress_callback:
                progress_callback(25, 100, "正在提取PDF下载链接...")
            
            pdf_infos = self._extract_pdf_infos(search_results, progress_callback)
            logger.info(f"PDF信息提取完成，成功提取 {len(pdf_infos)} 个PDF链接")
            
            # 步骤3: 下载PDF文件
            if progress_callback:
                progress_callback(50, 100, "正在下载PDF文件...")
            
            download_results = self._download_pdfs(pdf_infos, progress_callback)
            logger.info(f"PDF下载完成，成功下载 {len([r for r in download_results if r.success])} 个文件")
            
            # 创建结果
            result = self._create_workflow_result(
                search_results, pdf_infos, download_results, start_time
            )
            
            # 记录工作流程日志
            self._log_workflow(result)
            
            logger.info("完整工作流程执行完成")
            return result
            
        except Exception as e:
            logger.error(f"工作流程执行失败: {e}")
            return self._create_error_result(str(e), start_time)
    
    def _search_aps_papers(self, max_results: int) -> List[SearchResult]:
        """搜索APS论文"""
        try:
            results = self.google_scholar.search_aps_papers_2024(max_results=max_results)
            
            # 过滤出有效的APS论文
            valid_results = []
            for result in results:
                if result.is_aps and result.url:
                    valid_results.append(result)
            
            logger.info(f"找到 {len(valid_results)} 篇有效的APS论文")
            return valid_results
            
        except Exception as e:
            logger.error(f"搜索APS论文失败: {e}")
            return []
    
    def _extract_pdf_infos(self, search_results: List[SearchResult], 
                          progress_callback: Optional[Callable] = None) -> List[PDFInfo]:
        """提取PDF信息"""
        pdf_infos = []
        total = len(search_results)
        
        for i, result in enumerate(search_results):
            if progress_callback:
                progress_callback(25 + (i * 25 // total), 100, 
                                f"提取PDF信息: {result.title[:50]}...")
            
            try:
                pdf_info = self.aps_extractor.extract_pdf_info(result.url)
                if pdf_info and pdf_info.pdf_url:
                    pdf_infos.append(pdf_info)
                    logger.info(f"成功提取PDF信息: {result.title[:50]}...")
                else:
                    logger.warning(f"无法提取PDF信息: {result.title[:50]}...")
                
                # 添加延迟避免过于频繁的请求
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"提取PDF信息失败: {e}")
                continue
        
        return pdf_infos
    
    def _download_pdfs(self, pdf_infos: List[PDFInfo], 
                      progress_callback: Optional[Callable] = None) -> List[DownloadResult]:
        """下载PDF文件"""
        if not pdf_infos:
            return []
        
        # 准备下载信息
        download_infos = []
        for pdf_info in pdf_infos:
            download_infos.append({
                "pdf_url": pdf_info.pdf_url,
                "filename": pdf_info.file_name,
                "access_type": pdf_info.access_type,
                "requires_auth": pdf_info.requires_auth
            })
        
        # 执行批量下载
        def download_progress_callback(current, total, message):
            if progress_callback:
                progress = 50 + (current * 50 // total)
                progress_callback(progress, 100, message)
        
        return self.pdf_downloader.batch_download(download_infos, download_progress_callback)
    
    def _create_workflow_result(self, search_results: List[SearchResult], 
                              pdf_infos: List[PDFInfo], 
                              download_results: List[DownloadResult], 
                              start_time: float) -> WorkflowResult:
        """创建工作流程结果"""
        execution_time = time.time() - start_time
        
        successful_downloads = sum(1 for r in download_results if r.success)
        failed_downloads = len(download_results) - successful_downloads
        manual_intervention_required = sum(1 for r in download_results if r.requires_manual_intervention)
        
        return WorkflowResult(
            search_results=search_results,
            pdf_infos=pdf_infos,
            download_results=download_results,
            total_processed=len(search_results),
            successful_downloads=successful_downloads,
            failed_downloads=failed_downloads,
            manual_intervention_required=manual_intervention_required,
            execution_time=execution_time
        )
    
    def _create_empty_result(self, start_time: float) -> WorkflowResult:
        """创建空结果"""
        return WorkflowResult(
            search_results=[],
            pdf_infos=[],
            download_results=[],
            total_processed=0,
            successful_downloads=0,
            failed_downloads=0,
            manual_intervention_required=0,
            execution_time=time.time() - start_time
        )
    
    def _create_error_result(self, error_message: str, start_time: float) -> WorkflowResult:
        """创建错误结果"""
        return WorkflowResult(
            search_results=[],
            pdf_infos=[],
            download_results=[],
            total_processed=0,
            successful_downloads=0,
            failed_downloads=0,
            manual_intervention_required=0,
            execution_time=time.time() - start_time
        )
    
    def _log_workflow(self, result: WorkflowResult):
        """记录工作流程日志"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "total_processed": result.total_processed,
            "successful_downloads": result.successful_downloads,
            "failed_downloads": result.failed_downloads,
            "manual_intervention_required": result.manual_intervention_required,
            "execution_time": result.execution_time,
            "success_rate": (result.successful_downloads / result.total_processed * 100) if result.total_processed > 0 else 0
        }
        
        self.workflow_log.append(log_entry)
        
        # 保存到文件
        log_file = Path(self.download_dir) / "workflow_log.json"
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(self.workflow_log, f, indent=2, ensure_ascii=False)
    
    def get_workflow_stats(self) -> Dict:
        """获取工作流程统计信息"""
        if not self.workflow_log:
            return {
                "total_runs": 0, 
                "total_processed": 0,
                "total_successful": 0,
                "average_success_rate": 0.0,
                "recent_runs": []
            }
        
        total_runs = len(self.workflow_log)
        total_processed = sum(log.get("total_processed", 0) for log in self.workflow_log)
        total_successful = sum(log.get("successful_downloads", 0) for log in self.workflow_log)
        average_success_rate = (total_successful / total_processed * 100) if total_processed > 0 else 0.0
        
        return {
            "total_runs": total_runs,
            "total_processed": total_processed,
            "total_successful": total_successful,
            "average_success_rate": average_success_rate,
            "recent_runs": self.workflow_log[-5:]  # 最近5次运行
        }
    
    def get_manual_intervention_list(self) -> List[Dict]:
        """获取需要人工干预的下载列表"""
        return self.pdf_downloader.get_manual_intervention_list()
    
    def retry_failed_downloads(self, progress_callback: Optional[Callable] = None) -> List[DownloadResult]:
        """重试失败的下载"""
        failed_downloads = [r for r in self.pdf_downloader.download_log if not r["success"]]
        
        if not failed_downloads:
            logger.info("没有失败的下载需要重试")
            return []
        
        logger.info(f"开始重试 {len(failed_downloads)} 个失败的下载")
        
        # 准备重试信息
        retry_infos = []
        for log in failed_downloads:
            retry_infos.append({
                "pdf_url": log["pdf_url"],
                "filename": log["filename"],
                "access_type": log.get("access_type", "unknown"),
                "requires_auth": log.get("requires_manual_intervention", False)
            })
        
        # 执行重试
        return self.pdf_downloader.batch_download(retry_infos, progress_callback)
    
    def cleanup(self):
        """清理资源"""
        if hasattr(self, 'aps_extractor'):
            self.aps_extractor.close()
        
        logger.info("工作流程集成器清理完成")

# 测试函数
def test_workflow_integrator():
    """测试工作流程集成器"""
    integrator = WorkflowIntegrator(use_selenium=False)  # 先测试requests模式
    
    def progress_callback(progress, total, message):
        print(f"进度: {progress}% - {message}")
    
    try:
        # 运行完整工作流程
        result = integrator.run_complete_workflow(
            max_search_results=5,  # 测试用，只搜索5篇
            progress_callback=progress_callback
        )
        
        # 显示结果
        print(f"\n工作流程执行完成:")
        print(f"  总处理数: {result.total_processed}")
        print(f"  成功下载: {result.successful_downloads}")
        print(f"  失败下载: {result.failed_downloads}")
        print(f"  需要人工干预: {result.manual_intervention_required}")
        print(f"  执行时间: {result.execution_time:.2f}秒")
        
        # 显示统计信息
        stats = integrator.get_workflow_stats()
        print(f"\n工作流程统计:")
        print(f"  总运行次数: {stats['total_runs']}")
        print(f"  平均成功率: {stats['average_success_rate']:.1f}%")
        
    except Exception as e:
        print(f"工作流程测试失败: {e}")
    
    finally:
        integrator.cleanup()

if __name__ == "__main__":
    test_workflow_integrator()
