#!/usr/bin/env python3
"""
专门搜索APS期刊论文
只使用Google Scholar搜索APS期刊，不搜索其他来源
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.advanced_selenium_bypass import AdvancedSeleniumBypass
from app.services.aps_pdf_extractor import APSPDFExtractor
from app.services.pdf_downloader import PDFDownloader
import time

def check_and_handle_captcha(bypass):
    """检查并处理人机验证"""
    # 检查是否遇到人机验证 - 使用更精确的检测条件
    page_source = bypass.driver.page_source.lower()
    title = bypass.driver.title.lower()
    
    # 更精确的人机验证检测条件
    captcha_indicators = [
        "unusual traffic", "suspicious activity", "not a robot",
        "verify you are human", "security check", "captcha",
        "please complete the security check", "robot detection"
    ]
    
    # 检查页面是否包含人机验证的关键元素
    is_captcha = False
    for indicator in captcha_indicators:
        if indicator in title or indicator in page_source:
            is_captcha = True
            break
    
    # 检查是否有验证码相关的HTML元素
    if not is_captcha:
        try:
            # 检查常见的验证码元素
            captcha_elements = bypass.driver.find_elements("css selector", 
                "iframe[src*='recaptcha'], .g-recaptcha, #captcha, .captcha, [data-callback*='captcha']")
            if captcha_elements:
                is_captcha = True
        except:
            pass
    
    if is_captcha:
        print("🔐 检测到人机验证")
        print("=" * 50)
        print("请按照以下步骤完成验证：")
        print("1. 在浏览器中完成人机验证")
        print("2. 等待验证完成，页面跳转到Google Scholar")
        print("3. 按回车键继续...")
        print()
        
        input("完成验证后按回车键继续...")
        
        # 重新检查页面状态
        print("重新检查页面状态...")
        time.sleep(2)
        print(f"当前URL: {bypass.driver.current_url}")
        print(f"页面标题: {bypass.driver.title}")
        
        return True
    else:
        # 不打印任何信息，避免误报
        return True

def search_aps_only():
    """专门搜索APS期刊论文 - 测试PRB期刊"""
    print("专门搜索APS期刊论文 - 测试PRB期刊")
    print("=" * 50)
    print("只使用Google Scholar搜索APS期刊，不搜索其他来源")
    print("包含人机验证处理能力")
    print()
    print("当前测试：Physical Review B (PRB) 期刊")
    print("其他期刊已注释，正式检索时会启用")
    print()
    
    # 初始化服务
    bypass = AdvancedSeleniumBypass(headless=False)  # 非无头模式，便于处理验证
    aps_extractor = APSPDFExtractor(use_selenium=True, use_cloudflare_bypass=True)
    pdf_downloader = PDFDownloader(download_dir="downloads")
    
    try:
        print("步骤1: 访问Google Scholar")
        print("-" * 30)
        
        # 访问Google Scholar
        bypass.driver.get("https://scholar.google.com")
        time.sleep(3)
        
        print(f"当前URL: {bypass.driver.current_url}")
        print(f"页面标题: {bypass.driver.title}")
        
        # 检查是否遇到人机验证
        if not check_and_handle_captcha(bypass):
            print("❌ 人机验证处理失败，退出程序")
            return
        
        print("\n步骤2: 搜索APS期刊论文")
        print("-" * 30)
        
        # 定义APS期刊搜索查询
        aps_search_queries = [
            # "site:journals.aps.org/prl single crystal growth",           # Physical Review Letters - 测试阶段跳过
            "site:journals.aps.org/prb single crystal growth",           # Physical Review B - 测试目标
            # "site:journals.aps.org/prmaterials single crystal growth",   # Physical Review Materials - 测试阶段跳过
            # "site:journals.aps.org/prresearch single crystal growth",    # Physical Review Research - 测试阶段跳过
            # "site:journals.aps.org/prx single crystal growth",           # Physical Review X - 测试阶段跳过
            # "site:journals.aps.org/prapplied single crystal growth"      # Physical Review Applied - 测试阶段跳过
        ]
        
        all_aps_papers = []
        
        for query in aps_search_queries:
            print(f"搜索: {query}")
            
            try:
                # 静默检查人机验证，只在真正遇到时才提示
                check_and_handle_captcha(bypass)
                
                results = bypass.search_google_scholar(query, max_results=5)
                
                if results:
                    print(f"  ✅ 找到 {len(results)} 个APS论文")
                    
                    for result in results:
                        # 验证确实是APS期刊
                        if any(domain in result.url for domain in ["journals.aps.org", "aip.scitation.org"]):
                            all_aps_papers.append(result)
                            print(f"    - {result.title}")
                            print(f"      期刊: {result.journal}")
                            print(f"      URL: {result.url}")
                            print()
                else:
                    print(f"  ❌ 未找到结果")
                
                time.sleep(5)  # 增加延迟，避免触发验证
                
            except Exception as e:
                print(f"  ❌ 搜索失败: {e}")
                continue
        
        if not all_aps_papers:
            print("❌ 未找到任何APS期刊论文")
            return
        
        print(f"\n✅ 总共找到 {len(all_aps_papers)} 个APS期刊论文")
        
        print("\n步骤3: 处理APS论文")
        print("-" * 30)
        
        success_count = 0
        for i, paper in enumerate(all_aps_papers[:5], 1):  # 处理前5个论文
            print(f"\n处理论文 {i}: {paper.title}")
            print(f"期刊: {paper.journal}")
            print(f"URL: {paper.url}")
            
            try:
                # 提取PDF信息
                print("  提取PDF信息...")
                pdf_info = aps_extractor.extract_pdf_info(paper.url)
                
                if pdf_info:
                    print(f"  ✅ PDF信息提取成功")
                    print(f"  PDF URL: {pdf_info.pdf_url}")
                    print(f"  标题: {pdf_info.title}")
                    print(f"  作者: {pdf_info.authors}")
                    print(f"  期刊: {pdf_info.journal}")
                    print(f"  访问类型: {pdf_info.access_type}")
                    
                    # 下载PDF
                    print("  下载PDF...")
                    filename = f"aps_only_{i}_{pdf_info.title[:30].replace(' ', '_').replace('/', '_')}.pdf"
                    download_result = pdf_downloader.download_pdf(
                        pdf_info.pdf_url, 
                        filename, 
                        pdf_info.access_type
                    )
                    
                    if download_result.success:
                        print(f"  ✅ PDF下载成功")
                        print(f"  文件路径: {download_result.file_path}")
                        print(f"  文件大小: {download_result.file_size} bytes")
                        success_count += 1
                    else:
                        print(f"  ❌ PDF下载失败: {download_result.error}")
                        
                        # 检查是否需要权限
                        if "403" in str(download_result.error) or "Forbidden" in str(download_result.error):
                            print("  🔐 检测到权限问题")
                            print("  💡 建议：")
                            print("     1. 手动访问: {paper.url}")
                            print("     2. 下载PDF并保存为: {filename}")
                            print("     3. 将文件放入 downloads/ 目录")
                else:
                    print("  ❌ PDF信息提取失败")
                    
            except Exception as e:
                print(f"  ❌ 处理异常: {e}")
        
        # 显示最终结果
        print(f"\n步骤4: 处理结果统计")
        print("-" * 30)
        print(f"总处理论文: {min(5, len(all_aps_papers))}")
        print(f"成功处理: {success_count}")
        print(f"成功率: {success_count/min(5, len(all_aps_papers))*100:.1f}%")
        
        if success_count > 0:
            print("🎉 APS期刊论文处理完成！")
        else:
            print("❌ 所有APS论文处理失败")
            
    except Exception as e:
        print(f"❌ 工作流程失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        bypass.close()

if __name__ == "__main__":
    search_aps_only()
