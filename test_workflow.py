"""
测试工作流程脚本
用于测试从Google Scholar搜索到APS PDF下载的完整流程
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.append(str(Path(__file__).parent))

from app.services.workflow_integrator import WorkflowIntegrator

def test_google_scholar_search():
    """测试Google Scholar搜索功能"""
    print("测试Google Scholar搜索功能...")
    
    from app.services.google_scholar_service import GoogleScholarService
    
    service = GoogleScholarService()
    
    try:
        # 搜索少量结果进行测试
        results = service.search_aps_papers_2024(max_results=5)
        
        print(f"搜索到 {len(results)} 篇论文:")
        for i, result in enumerate(results, 1):
            print(f"\n{i}. {result.title}")
            print(f"   作者: {result.authors}")
            print(f"   期刊: {result.journal}")
            print(f"   年份: {result.year}")
            print(f"   URL: {result.url}")
            print(f"   是APS期刊: {result.is_aps}")
        
        return len(results) > 0
        
    except Exception as e:
        print(f"Google Scholar搜索测试失败: {e}")
        return False

def test_aps_pdf_extraction():
    """测试APS PDF提取功能"""
    print("\n测试APS PDF提取功能...")
    
    from app.services.aps_pdf_extractor import APSPDFExtractor
    
    extractor = APSPDFExtractor(use_selenium=False)  # 先测试requests模式
    
    # 测试URL（需要替换为真实的APS文章URL）
    test_urls = [
        "https://journals.aps.org/prb/abstract/10.1103/PhysRevB.123.456789",
        "https://aip.scitation.org/doi/10.1063/5.0123456"
    ]
    
    success_count = 0
    
    for url in test_urls:
        print(f"\n测试URL: {url}")
        try:
            pdf_info = extractor.extract_pdf_info(url)
            if pdf_info:
                print(f"  PDF URL: {pdf_info.pdf_url}")
                print(f"  文件名: {pdf_info.file_name}")
                print(f"  访问类型: {pdf_info.access_type}")
                print(f"  需要认证: {pdf_info.requires_auth}")
                success_count += 1
            else:
                print("  PDF信息提取失败")
        except Exception as e:
            print(f"  PDF提取测试失败: {e}")
    
    extractor.close()
    return success_count > 0

def test_pdf_download():
    """测试PDF下载功能"""
    print("\n测试PDF下载功能...")
    
    from app.services.pdf_downloader import PDFDownloader
    
    downloader = PDFDownloader(download_dir="test_downloads")
    
    # 测试下载信息（使用一个公开的PDF文件进行测试）
    test_pdf_info = {
        "pdf_url": "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf",
        "filename": "test_dummy.pdf",
        "access_type": "open",
        "requires_auth": False
    }
    
    try:
        result = downloader.download_pdf(**test_pdf_info)
        
        if result.success:
            print(f"PDF下载成功:")
            print(f"  文件路径: {result.file_path}")
            print(f"  文件大小: {result.file_size} bytes")
            print(f"  下载时间: {result.download_time:.2f}秒")
            return True
        else:
            print(f"PDF下载失败: {result.error_message}")
            return False
            
    except Exception as e:
        print(f"PDF下载测试失败: {e}")
        return False

def test_complete_workflow():
    """测试完整工作流程"""
    print("\n测试完整工作流程...")
    
    integrator = WorkflowIntegrator(
        download_dir="test_downloads",
        use_selenium=False  # 先测试requests模式
    )
    
    try:
        def progress_callback(progress, total, message):
            print(f"\r进度: {progress}% - {message}", end='', flush=True)
        
        # 运行完整工作流程（只搜索少量结果）
        result = integrator.run_complete_workflow(
            max_search_results=3,  # 只搜索3篇进行测试
            progress_callback=progress_callback
        )
        
        print(f"\n\n工作流程测试结果:")
        print(f"  总处理数: {result.total_processed}")
        print(f"  成功下载: {result.successful_downloads}")
        print(f"  失败下载: {result.failed_downloads}")
        print(f"  需要人工干预: {result.manual_intervention_required}")
        print(f"  执行时间: {result.execution_time:.2f}秒")
        
        return result.total_processed > 0
        
    except Exception as e:
        print(f"\n完整工作流程测试失败: {e}")
        return False
    
    finally:
        integrator.cleanup()

def main():
    """主测试函数"""
    print("开始测试APS PDF下载工作流程")
    print("=" * 50)
    
    test_results = []
    
    # 测试各个组件
    test_results.append(("Google Scholar搜索", test_google_scholar_search()))
    test_results.append(("APS PDF提取", test_aps_pdf_extraction()))
    test_results.append(("PDF下载", test_pdf_download()))
    test_results.append(("完整工作流程", test_complete_workflow()))
    
    # 显示测试结果
    print("\n" + "=" * 50)
    print("测试结果汇总:")
    print("=" * 50)
    
    passed = 0
    for test_name, result in test_results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n总计: {passed}/{len(test_results)} 个测试通过")
    
    if passed == len(test_results):
        print("\n🎉 所有测试都通过了！")
    else:
        print(f"\n⚠️  有 {len(test_results) - passed} 个测试失败，请检查相关功能")

if __name__ == "__main__":
    main()
