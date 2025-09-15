#!/usr/bin/env python3
"""
测试完整的APS工作流程：搜索 -> 识别APS期刊 -> 提取PDF -> 下载
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.advanced_selenium_bypass import AdvancedSeleniumBypass
from app.services.aps_pdf_extractor import APSPDFExtractor
from app.services.pdf_downloader import PDFDownloader
import time

def test_aps_workflow():
    """测试完整的APS工作流程"""
    print("测试完整的APS工作流程")
    print("=" * 60)
    
    # 初始化服务
    bypass = AdvancedSeleniumBypass(headless=False)  # 非无头模式，便于观察
    aps_extractor = APSPDFExtractor(use_selenium=True)  # 使用Selenium模式
    pdf_downloader = PDFDownloader(download_dir="downloads")
    
    try:
        # 1. 搜索APS开放获取期刊的论文
        print("1. 搜索APS开放获取期刊论文...")
        search_queries = [
            "site:journals.aps.org/prx single crystal growth",
            "site:journals.aps.org/prresearch single crystal growth", 
            "site:journals.aps.org/prx quantum crystal growth",
            "site:journals.aps.org/prresearch flux method"
        ]
        
        aps_papers = []
        for query in search_queries:
            print(f"   搜索: {query}")
            results = bypass.search_google_scholar(query, max_results=3)
            
            # 筛选APS期刊论文
            for result in results:
                if any(domain in result.url for domain in ["journals.aps.org", "aip.scitation.org"]):
                    aps_papers.append(result)
                    print(f"   ✅ 找到APS论文: {result.title}")
                    print(f"      URL: {result.url}")
                    print(f"      期刊: {result.journal}")
                    print()
        
        if not aps_papers:
            print("❌ 未找到APS期刊论文，尝试更广泛的搜索...")
            # 尝试更广泛的搜索
            results = bypass.search_google_scholar("APS Physical Review single crystal growth", max_results=10)
            for result in results:
                if any(domain in result.url for domain in ["journals.aps.org", "aip.scitation.org"]):
                    aps_papers.append(result)
                    print(f"   ✅ 找到APS论文: {result.title}")
                    print(f"      URL: {result.url}")
                    print()
        
        if not aps_papers:
            print("❌ 仍然未找到APS期刊论文")
            return
        
        # 2. 选择第一个APS论文进行测试
        selected_paper = aps_papers[0]
        print(f"2. 选择测试论文: {selected_paper.title}")
        print(f"   URL: {selected_paper.url}")
        print()
        
        # 3. 提取PDF信息
        print("3. 提取PDF信息...")
        pdf_info = aps_extractor.extract_pdf_info(selected_paper.url)
        
        if pdf_info:
            print(f"   ✅ PDF信息提取成功")
            print(f"   PDF URL: {pdf_info.pdf_url}")
            print(f"   标题: {pdf_info.title}")
            print(f"   作者: {pdf_info.authors}")
            print(f"   期刊: {pdf_info.journal}")
            print(f"   访问类型: {pdf_info.access_type}")
            print()
            
            # 4. 下载PDF
            print("4. 下载PDF...")
            filename = f"aps_{selected_paper.title[:50].replace(' ', '_').replace('/', '_')}.pdf"
            download_result = pdf_downloader.download_pdf(
                pdf_info.pdf_url, 
                filename, 
                pdf_info.access_type
            )
            
            if download_result.success:
                print(f"   ✅ PDF下载成功")
                print(f"   文件路径: {download_result.file_path}")
                print(f"   文件大小: {download_result.file_size} bytes")
            else:
                print(f"   ❌ PDF下载失败: {download_result.error}")
                
                # 如果是权限问题，尝试其他论文
                if "403" in str(download_result.error) or "Forbidden" in str(download_result.error):
                    print("   可能是权限问题，尝试其他论文...")
                    if len(aps_papers) > 1:
                        print(f"   尝试第二个论文: {aps_papers[1].title}")
                        pdf_info2 = aps_extractor.extract_pdf_info(aps_papers[1].url)
                        if pdf_info2:
                            filename2 = f"aps_{aps_papers[1].title[:50].replace(' ', '_').replace('/', '_')}.pdf"
                            download_result2 = pdf_downloader.download_pdf(
                                pdf_info2.pdf_url, 
                                filename2, 
                                pdf_info2.access_type
                            )
                            if download_result2.success:
                                print(f"   ✅ 第二个PDF下载成功")
                                print(f"   文件路径: {download_result2.file_path}")
                            else:
                                print(f"   ❌ 第二个PDF也下载失败: {download_result2.error}")
        else:
            print("   ❌ PDF信息提取失败")
        
    except Exception as e:
        print(f"❌ 工作流程测试失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        bypass.close()

if __name__ == "__main__":
    test_aps_workflow()
