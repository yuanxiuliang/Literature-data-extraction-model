"""
PDF下载器
用于下载和管理PDF文件
"""

import os
import requests
import time
import logging
from typing import List, Dict, Optional, Callable
from pathlib import Path
from urllib.parse import urlparse
import hashlib
from dataclasses import dataclass
from datetime import datetime
import PyPDF2
import json

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class DownloadResult:
    """下载结果数据类"""
    success: bool
    file_path: Optional[str] = None
    file_size: Optional[int] = None
    download_time: Optional[float] = None
    error_message: Optional[str] = None
    requires_manual_intervention: bool = False
    access_type: str = "unknown"

class PDFDownloader:
    """PDF下载器"""
    
    def __init__(self, download_dir: str = "downloads", max_retries: int = 3):
        self.download_dir = Path(download_dir)
        self.max_retries = max_retries
        self.session = requests.Session()
        self.download_log = []
        
        # 创建下载目录
        self.download_dir.mkdir(exist_ok=True)
        
        # 设置会话
        self._setup_session()
    
    def _setup_session(self):
        """设置请求会话"""
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/pdf,application/octet-stream,*/*',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Cache-Control': 'no-cache'
        })
    
    def download_pdf(self, pdf_url: str, filename: str, 
                    access_type: str = "unknown", 
                    requires_auth: bool = False,
                    progress_callback: Optional[Callable] = None) -> DownloadResult:
        """
        下载PDF文件
        
        Args:
            pdf_url: PDF下载URL
            filename: 文件名
            access_type: 访问类型
            requires_auth: 是否需要认证
            progress_callback: 进度回调函数
            
        Returns:
            DownloadResult: 下载结果
        """
        start_time = time.time()
        
        try:
            # 检查是否需要人工干预
            if requires_auth and access_type == "subscription":
                logger.warning(f"需要认证访问: {pdf_url}")
                return DownloadResult(
                    success=False,
                    error_message="需要认证访问",
                    requires_manual_intervention=True,
                    access_type=access_type
                )
            
            # 检查文件是否已存在
            file_path = self.download_dir / filename
            if file_path.exists():
                logger.info(f"文件已存在: {file_path}")
                return DownloadResult(
                    success=True,
                    file_path=str(file_path),
                    file_size=file_path.stat().st_size,
                    download_time=0.0,
                    access_type=access_type
                )
            
            # 执行下载
            result = self._download_with_retry(pdf_url, file_path, progress_callback)
            
            if result.success:
                # 验证PDF文件
                if self._validate_pdf(file_path):
                    download_time = time.time() - start_time
                    result.download_time = download_time
                    result.file_size = file_path.stat().st_size
                    
                    # 记录下载日志
                    self._log_download(pdf_url, filename, result)
                    
                    logger.info(f"PDF下载成功: {filename} ({result.file_size} bytes)")
                else:
                    result.success = False
                    result.error_message = "PDF文件验证失败"
                    if file_path.exists():
                        file_path.unlink()  # 删除无效文件
            
            return result
            
        except Exception as e:
            logger.error(f"PDF下载失败: {e}")
            return DownloadResult(
                success=False,
                error_message=str(e),
                access_type=access_type
            )
    
    def _download_with_retry(self, pdf_url: str, file_path: Path, 
                           progress_callback: Optional[Callable] = None) -> DownloadResult:
        """带重试的下载"""
        for attempt in range(self.max_retries):
            try:
                logger.info(f"下载尝试 {attempt + 1}/{self.max_retries}: {pdf_url}")
                
                response = self.session.get(pdf_url, stream=True, timeout=30)
                response.raise_for_status()
                
                # 检查响应内容类型
                content_type = response.headers.get('content-type', '').lower()
                if 'pdf' not in content_type and not pdf_url.endswith('.pdf'):
                    logger.warning(f"可能不是PDF文件: {content_type}")
                
                # 下载文件
                total_size = int(response.headers.get('content-length', 0))
                downloaded_size = 0
                
                with open(file_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            downloaded_size += len(chunk)
                            
                            # 调用进度回调
                            if progress_callback and total_size > 0:
                                progress = (downloaded_size / total_size) * 100
                                progress_callback(progress)
                
                return DownloadResult(success=True, file_path=str(file_path))
                
            except requests.exceptions.RequestException as e:
                logger.warning(f"下载尝试 {attempt + 1} 失败: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)  # 指数退避
                else:
                    return DownloadResult(
                        success=False,
                        error_message=f"下载失败: {e}"
                    )
            except Exception as e:
                logger.error(f"下载过程中发生错误: {e}")
                return DownloadResult(
                    success=False,
                    error_message=f"下载错误: {e}"
                )
        
        return DownloadResult(success=False, error_message="所有重试尝试都失败了")
    
    def _validate_pdf(self, file_path: Path) -> bool:
        """验证PDF文件"""
        try:
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                
                # 检查页数
                if len(reader.pages) < 1:
                    logger.warning("PDF文件没有页面")
                    return False
                
                # 检查文件大小
                if file_path.stat().st_size < 1024:  # 小于1KB
                    logger.warning("PDF文件太小")
                    return False
                
                # 尝试提取第一页文本
                try:
                    first_page = reader.pages[0]
                    text = first_page.extract_text()
                    if len(text.strip()) < 10:  # 文本太少
                        logger.warning("PDF文件文本内容太少")
                        return False
                except Exception:
                    logger.warning("无法提取PDF文本")
                    return False
                
                return True
                
        except Exception as e:
            logger.error(f"PDF验证失败: {e}")
            return False
    
    def _log_download(self, pdf_url: str, filename: str, result: DownloadResult):
        """记录下载日志"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "pdf_url": pdf_url,
            "filename": filename,
            "success": result.success,
            "file_size": result.file_size,
            "download_time": result.download_time,
            "error_message": result.error_message,
            "access_type": result.access_type
        }
        
        self.download_log.append(log_entry)
        
        # 保存到文件
        log_file = self.download_dir / "download_log.json"
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(self.download_log, f, indent=2, ensure_ascii=False)
    
    def batch_download(self, pdf_infos: List[Dict], 
                      progress_callback: Optional[Callable] = None) -> List[DownloadResult]:
        """
        批量下载PDF文件
        
        Args:
            pdf_infos: PDF信息列表，每个元素包含pdf_url, filename, access_type等
            progress_callback: 进度回调函数
            
        Returns:
            List[DownloadResult]: 下载结果列表
        """
        results = []
        total = len(pdf_infos)
        
        logger.info(f"开始批量下载 {total} 个PDF文件")
        
        for i, pdf_info in enumerate(pdf_infos):
            if progress_callback:
                progress_callback(i, total, f"下载 {pdf_info.get('filename', 'unknown')}")
            
            result = self.download_pdf(
                pdf_url=pdf_info.get('pdf_url'),
                filename=pdf_info.get('filename'),
                access_type=pdf_info.get('access_type', 'unknown'),
                requires_auth=pdf_info.get('requires_auth', False)
            )
            
            results.append(result)
            
            # 添加延迟避免过于频繁的请求
            time.sleep(1)
        
        # 统计结果
        successful = sum(1 for r in results if r.success)
        failed = total - successful
        manual_intervention = sum(1 for r in results if r.requires_manual_intervention)
        
        logger.info(f"批量下载完成: 成功 {successful}, 失败 {failed}, 需要人工干预 {manual_intervention}")
        
        return results
    
    def get_download_stats(self) -> Dict:
        """获取下载统计信息"""
        if not self.download_log:
            return {"total": 0, "successful": 0, "failed": 0, "success_rate": 0.0}
        
        total = len(self.download_log)
        successful = sum(1 for log in self.download_log if log["success"])
        failed = total - successful
        success_rate = (successful / total) * 100 if total > 0 else 0.0
        
        # 按访问类型统计
        access_types = {}
        for log in self.download_log:
            access_type = log.get("access_type", "unknown")
            if access_type not in access_types:
                access_types[access_type] = {"total": 0, "successful": 0}
            access_types[access_type]["total"] += 1
            if log["success"]:
                access_types[access_type]["successful"] += 1
        
        return {
            "total": total,
            "successful": successful,
            "failed": failed,
            "success_rate": success_rate,
            "access_types": access_types
        }
    
    def cleanup_failed_downloads(self):
        """清理失败的下载文件"""
        cleaned_count = 0
        
        for log in self.download_log:
            if not log["success"] and log.get("file_path"):
                file_path = Path(log["file_path"])
                if file_path.exists():
                    file_path.unlink()
                    cleaned_count += 1
        
        logger.info(f"清理了 {cleaned_count} 个失败的下载文件")
    
    def get_manual_intervention_list(self) -> List[Dict]:
        """获取需要人工干预的下载列表"""
        return [
            log for log in self.download_log 
            if log.get("requires_manual_intervention", False)
        ]

# 测试函数
def test_pdf_downloader():
    """测试PDF下载器"""
    downloader = PDFDownloader()
    
    # 测试PDF信息
    test_pdf_infos = [
        {
            "pdf_url": "https://example.com/test1.pdf",
            "filename": "test1.pdf",
            "access_type": "open",
            "requires_auth": False
        },
        {
            "pdf_url": "https://example.com/test2.pdf", 
            "filename": "test2.pdf",
            "access_type": "subscription",
            "requires_auth": True
        }
    ]
    
    def progress_callback(current, total, message):
        print(f"进度: {current}/{total} - {message}")
    
    # 执行批量下载
    results = downloader.batch_download(test_pdf_infos, progress_callback)
    
    # 显示结果
    for i, result in enumerate(results):
        print(f"\n结果 {i+1}:")
        print(f"  成功: {result.success}")
        print(f"  文件路径: {result.file_path}")
        print(f"  文件大小: {result.file_size}")
        print(f"  下载时间: {result.download_time}")
        print(f"  错误信息: {result.error_message}")
        print(f"  需要人工干预: {result.requires_manual_intervention}")
    
    # 显示统计信息
    stats = downloader.get_download_stats()
    print(f"\n下载统计:")
    print(f"  总计: {stats['total']}")
    print(f"  成功: {stats['successful']}")
    print(f"  失败: {stats['failed']}")
    print(f"  成功率: {stats['success_rate']:.1f}%")

if __name__ == "__main__":
    test_pdf_downloader()
