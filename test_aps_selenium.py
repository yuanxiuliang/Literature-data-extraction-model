#!/usr/bin/env python3
"""
使用Selenium测试APS网站访问
尝试绕过Cloudflare保护
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.advanced_selenium_bypass import AdvancedSeleniumBypass
from app.services.aps_pdf_extractor import APSPDFExtractor
from app.services.pdf_downloader import PDFDownloader
import time

def test_aps_selenium():
    """使用Selenium测试APS网站访问"""
    print("使用Selenium测试APS网站访问")
    print("=" * 50)
    
    # 初始化服务
    bypass = AdvancedSeleniumBypass(headless=False)  # 非无头模式，便于观察
    aps_extractor = APSPDFExtractor(use_selenium=True)  # 使用Selenium模式
    pdf_downloader = PDFDownloader(download_dir="downloads")
    
    try:
        print("步骤1: 测试APS网站访问")
        print("-" * 30)
        
        # 测试访问APS主页
        print("访问APS主页...")
        bypass.driver.get("https://journals.aps.org/")
        time.sleep(5)
        
        print(f"当前URL: {bypass.driver.current_url}")
        print(f"页面标题: {bypass.driver.title}")
        
        # 检查是否被阻止
        if "403" in bypass.driver.page_source or "Forbidden" in bypass.driver.title:
            print("❌ 被Cloudflare阻止")
            print("尝试等待Cloudflare验证...")
            time.sleep(10)
            
            # 再次检查
            print(f"等待后URL: {bypass.driver.current_url}")
            print(f"等待后标题: {bypass.driver.title}")
        
        print("\n步骤2: 搜索APS论文")
        print("-" * 30)
        
        # 使用Google Scholar搜索APS论文
        results = bypass.search_google_scholar("site:journals.aps.org/prx single crystal growth", max_results=3)
        
        if results:
            print(f"✅ 找到 {len(results)} 个APS论文")
            
            # 选择第一个论文进行测试
            selected_paper = results[0]
            print(f"\n选择论文: {selected_paper.title}")
            print(f"URL: {selected_paper.url}")
            print(f"期刊: {selected_paper.journal}")
            
            print("\n步骤3: 提取PDF信息")
            print("-" * 30)
            
            # 使用Selenium模式提取PDF信息
            pdf_info = aps_extractor.extract_pdf_info(selected_paper.url)
            
            if pdf_info:
                print(f"✅ PDF信息提取成功")
                print(f"PDF URL: {pdf_info.pdf_url}")
                print(f"标题: {pdf_info.title}")
                print(f"作者: {pdf_info.authors}")
                print(f"期刊: {pdf_info.journal}")
                print(f"访问类型: {pdf_info.access_type}")
                
                print("\n步骤4: 下载PDF")
                print("-" * 30)
                
                # 下载PDF
                filename = f"aps_selenium_{pdf_info.title[:30].replace(' ', '_').replace('/', '_')}.pdf"
                download_result = pdf_downloader.download_pdf(
                    pdf_info.pdf_url, 
                    filename, 
                    pdf_info.access_type
                )
                
                if download_result.success:
                    print(f"✅ PDF下载成功")
                    print(f"文件路径: {download_result.file_path}")
                    print(f"文件大小: {download_result.file_size} bytes")
                    print("🎉 成功从APS网站下载PDF！")
                else:
                    print(f"❌ PDF下载失败: {download_result.error}")
            else:
                print("❌ PDF信息提取失败")
        else:
            print("❌ 未找到APS论文")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        bypass.close()

if __name__ == "__main__":
    test_aps_selenium()
