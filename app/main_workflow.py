"""
主工作流程程序
用于执行从Google Scholar搜索到APS PDF下载的完整流程
"""

import argparse
import logging
import sys
from pathlib import Path
from typing import Optional

# 添加项目根目录到Python路径
sys.path.append(str(Path(__file__).parent.parent))

from app.services.workflow_integrator import WorkflowIntegrator, WorkflowResult

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('workflow.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def print_workflow_result(result: WorkflowResult):
    """打印工作流程结果"""
    print("\n" + "="*60)
    print("工作流程执行结果")
    print("="*60)
    
    print(f"总处理论文数: {result.total_processed}")
    print(f"成功下载PDF: {result.successful_downloads}")
    print(f"失败下载: {result.failed_downloads}")
    print(f"需要人工干预: {result.manual_intervention_required}")
    print(f"执行时间: {result.execution_time:.2f}秒")
    
    if result.total_processed > 0:
        success_rate = (result.successful_downloads / result.total_processed) * 100
        print(f"成功率: {success_rate:.1f}%")
    
    print("\n搜索结果详情:")
    for i, search_result in enumerate(result.search_results, 1):
        print(f"\n{i}. {search_result.title}")
        print(f"   作者: {search_result.authors}")
        print(f"   期刊: {search_result.journal}")
        print(f"   年份: {search_result.year}")
        print(f"   URL: {search_result.url}")
        print(f"   DOI: {search_result.doi}")
    
    print("\nPDF下载结果详情:")
    for i, download_result in enumerate(result.download_results, 1):
        status = "✓ 成功" if download_result.success else "✗ 失败"
        print(f"\n{i}. {status}")
        print(f"   文件路径: {download_result.file_path}")
        print(f"   文件大小: {download_result.file_size} bytes" if download_result.file_size else "   文件大小: 未知")
        print(f"   下载时间: {download_result.download_time:.2f}秒" if download_result.download_time else "   下载时间: 未知")
        print(f"   访问类型: {download_result.access_type}")
        print(f"   需要人工干预: {'是' if download_result.requires_manual_intervention else '否'}")
        if download_result.error_message:
            print(f"   错误信息: {download_result.error_message}")

def print_manual_intervention_list(integrator: WorkflowIntegrator):
    """打印需要人工干预的列表"""
    manual_list = integrator.get_manual_intervention_list()
    
    if not manual_list:
        print("\n没有需要人工干预的下载")
        return
    
    print(f"\n需要人工干预的下载 ({len(manual_list)} 个):")
    print("-" * 50)
    
    for i, item in enumerate(manual_list, 1):
        print(f"\n{i}. {item.get('filename', 'Unknown')}")
        print(f"   URL: {item.get('pdf_url', 'Unknown')}")
        print(f"   访问类型: {item.get('access_type', 'Unknown')}")
        print(f"   时间: {item.get('timestamp', 'Unknown')}")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='APS PDF下载工作流程')
    parser.add_argument('--max-results', type=int, default=20, 
                       help='最大搜索结果数量 (默认: 20)')
    parser.add_argument('--download-dir', type=str, default='downloads',
                       help='下载目录 (默认: downloads)')
    parser.add_argument('--use-selenium', action='store_true',
                       help='使用Selenium (默认: 使用requests)')
    parser.add_argument('--retry-failed', action='store_true',
                       help='重试失败的下载')
    parser.add_argument('--show-manual', action='store_true',
                       help='显示需要人工干预的列表')
    parser.add_argument('--stats', action='store_true',
                       help='显示工作流程统计信息')
    
    args = parser.parse_args()
    
    # 创建下载目录
    download_dir = Path(args.download_dir)
    download_dir.mkdir(exist_ok=True)
    
    # 初始化工作流程集成器
    integrator = WorkflowIntegrator(
        download_dir=str(download_dir),
        use_selenium=args.use_selenium
    )
    
    try:
        if args.retry_failed:
            # 重试失败的下载
            print("重试失败的下载...")
            results = integrator.retry_failed_downloads()
            print(f"重试完成，处理了 {len(results)} 个下载")
            
        elif args.show_manual:
            # 显示需要人工干预的列表
            print_manual_intervention_list(integrator)
            
        elif args.stats:
            # 显示统计信息
            stats = integrator.get_workflow_stats()
            print("\n工作流程统计信息:")
            print("-" * 30)
            print(f"总运行次数: {stats['total_runs']}")
            print(f"总处理论文数: {stats['total_processed']}")
            print(f"总成功下载数: {stats['total_successful']}")
            print(f"平均成功率: {stats['average_success_rate']:.1f}%")
            
            if stats['recent_runs']:
                print("\n最近运行记录:")
                for run in stats['recent_runs']:
                    print(f"  {run['timestamp']}: 处理{run['total_processed']}篇, 成功{run['successful_downloads']}篇")
        
        else:
            # 运行完整工作流程
            print("开始APS PDF下载工作流程...")
            print(f"最大搜索结果: {args.max_results}")
            print(f"下载目录: {args.download_dir}")
            print(f"使用Selenium: {args.use_selenium}")
            print("-" * 50)
            
            def progress_callback(progress, total, message):
                print(f"\r进度: {progress}% - {message}", end='', flush=True)
            
            # 执行工作流程
            result = integrator.run_complete_workflow(
                max_search_results=args.max_results,
                progress_callback=progress_callback
            )
            
            # 打印结果
            print_workflow_result(result)
            
            # 如果有需要人工干预的下载，显示列表
            if result.manual_intervention_required > 0:
                print_manual_intervention_list(integrator)
    
    except KeyboardInterrupt:
        print("\n\n工作流程被用户中断")
        logger.info("工作流程被用户中断")
        
    except Exception as e:
        print(f"\n工作流程执行失败: {e}")
        logger.error(f"工作流程执行失败: {e}")
        sys.exit(1)
    
    finally:
        # 清理资源
        integrator.cleanup()
        print("\n工作流程完成")

if __name__ == "__main__":
    main()
