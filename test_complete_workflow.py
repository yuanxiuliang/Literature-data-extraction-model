#!/usr/bin/env python3
"""
测试完整的工作流程
验证从搜索到PDF下载的端到端流程
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.anti_crawler_bypass import AntiCrawlerBypass
from app.services.pdf_downloader import PDFDownloader
import time

def test_complete_workflow():
    """测试完整的工作流程"""
    print("测试完整的工作流程")
    print("=" * 50)
    
    # 初始化服务
    anti_crawler = AntiCrawlerBypass()
    pdf_downloader = PDFDownloader(download_dir="downloads")
    
    print("步骤1: 搜索单晶生长相关论文")
    print("-" * 30)
    
    try:
        # 搜索论文
        results = anti_crawler.search_alternative_sources("single crystal growth")
        print(f"✅ 搜索成功，找到 {len(results)} 个结果")
        
        # 筛选有PDF URL的论文
        downloadable_papers = []
        for result in results:
            if result.get('pdf_url'):
                downloadable_papers.append(result)
                print(f"  ✅ 可下载: {result.get('title', '')[:60]}...")
                print(f"     PDF URL: {result.get('pdf_url')}")
        
        if not downloadable_papers:
            print("❌ 没有找到可下载的论文")
            return
        
        print(f"\n✅ 找到 {len(downloadable_papers)} 个可下载的论文")
        
    except Exception as e:
        print(f"❌ 搜索失败: {e}")
        return
    
    print("\n步骤2: 测试PDF下载功能")
    print("-" * 30)
    
    success_count = 0
    failed_count = 0
    
    # 测试前3个论文
    for i, paper in enumerate(downloadable_papers[:3], 1):
        print(f"\n测试论文 {i}: {paper.get('title', '')[:60]}...")
        print(f"期刊: {paper.get('venue', 'N/A')}")
        print(f"年份: {paper.get('year', 'N/A')}")
        print(f"PDF URL: {paper.get('pdf_url')}")
        
        try:
            # 下载PDF
            filename = f"workflow_test_{i}_{paper.get('title', '')[:30].replace(' ', '_').replace('/', '_')}.pdf"
            download_result = pdf_downloader.download_pdf(
                paper.get('pdf_url'), 
                filename, 
                "open_access"
            )
            
            if download_result.success:
                print(f"  ✅ PDF下载成功")
                print(f"  文件路径: {download_result.file_path}")
                print(f"  文件大小: {download_result.file_size} bytes")
                success_count += 1
            else:
                print(f"  ❌ PDF下载失败: {download_result.error}")
                failed_count += 1
                
        except Exception as e:
            print(f"  ❌ 下载异常: {e}")
            failed_count += 1
    
    print(f"\n步骤3: 测试结果统计")
    print("-" * 30)
    print(f"总测试论文: {min(3, len(downloadable_papers))}")
    print(f"成功下载: {success_count}")
    print(f"失败下载: {failed_count}")
    print(f"成功率: {success_count/min(3, len(downloadable_papers))*100:.1f}%")
    
    if success_count > 0:
        print("\n🎉 工作流程测试成功！")
        print("✅ 验证了以下功能:")
        print("  1. 论文搜索功能正常")
        print("  2. PDF下载功能正常")
        print("  3. 端到端流程完整")
        
        print("\n📋 下一步建议:")
        print("  1. 完善APS期刊的权限处理")
        print("  2. 实现人工干预机制")
        print("  3. 开始Phase 3.2的其他出版社实现")
    else:
        print("\n❌ 工作流程测试失败")
        print("建议:")
        print("  1. 检查网络连接")
        print("  2. 检查PDF下载器配置")
        print("  3. 尝试其他搜索策略")

if __name__ == "__main__":
    test_complete_workflow()
