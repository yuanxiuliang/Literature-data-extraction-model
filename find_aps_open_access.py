#!/usr/bin/env python3
"""
寻找APS开放获取论文
通过多种方式搜索真正的APS开放获取论文进行测试
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.advanced_selenium_bypass import AdvancedSeleniumBypass
from app.services.anti_crawler_bypass import AntiCrawlerBypass
from app.services.aps_pdf_extractor import APSPDFExtractor
from app.services.pdf_downloader import PDFDownloader
import time

def find_aps_open_access():
    """寻找APS开放获取论文"""
    print("寻找APS开放获取论文")
    print("=" * 50)
    
    # 初始化服务
    anti_crawler = AntiCrawlerBypass()
    aps_extractor = APSPDFExtractor(use_selenium=False)
    pdf_downloader = PDFDownloader(download_dir="downloads")
    
    # 搜索策略
    search_queries = [
        "site:journals.aps.org/prx single crystal growth",
        "site:journals.aps.org/prresearch single crystal growth",
        "site:journals.aps.org/prx quantum crystal",
        "site:journals.aps.org/prresearch flux method",
        "APS Physical Review X open access",
        "APS Physical Review Research open access"
    ]
    
    print("策略1：使用替代搜索源搜索APS论文")
    print("-" * 40)
    
    aps_papers = []
    for query in search_queries:
        print(f"搜索: {query}")
        try:
            results = anti_crawler.search_alternative_sources(query)
            
            for result in results:
                url = result.get('url', '')
                if any(domain in url for domain in ["journals.aps.org", "aip.scitation.org"]):
                    aps_papers.append({
                        'title': result.get('title', ''),
                        'url': url,
                        'authors': ', '.join([author.get('name', '') for author in result.get('authors', [])]),
                        'journal': result.get('venue', ''),
                        'year': result.get('year', ''),
                        'abstract': result.get('abstract', ''),
                        'pdf_url': result.get('pdf_url', '')
                    })
                    print(f"  ✅ 找到APS论文: {result.get('title', '')[:60]}...")
                    print(f"     URL: {url}")
            
            time.sleep(2)  # 温和延迟
        except Exception as e:
            print(f"  ⚠️ 搜索失败: {e}")
            continue
    
    if not aps_papers:
        print("❌ 替代搜索源未找到APS论文")
        print("\n策略2：使用Google Scholar搜索APS论文")
        print("-" * 40)
        
        # 使用Google Scholar搜索
        bypass = AdvancedSeleniumBypass(headless=False)
        try:
            for query in search_queries[:3]:  # 只测试前3个查询
                print(f"Google Scholar搜索: {query}")
                results = bypass.search_google_scholar(query, max_results=5)
                
                for result in results:
                    if any(domain in result.url for domain in ["journals.aps.org", "aip.scitation.org"]):
                        aps_papers.append({
                            'title': result.title,
                            'url': result.url,
                            'authors': result.authors,
                            'journal': result.journal,
                            'year': result.year,
                            'abstract': getattr(result, 'abstract', ''),
                            'pdf_url': ''
                        })
                        print(f"  ✅ 找到APS论文: {result.title[:60]}...")
                        print(f"     URL: {result.url}")
                
                time.sleep(3)  # 温和延迟
        except Exception as e:
            print(f"  ❌ Google Scholar搜索失败: {e}")
        finally:
            bypass.close()
    
    if not aps_papers:
        print("❌ 所有搜索策略都未找到APS论文")
        print("\n策略3：使用已知的APS开放获取论文进行测试")
        print("-" * 40)
        
        # 使用一些已知的APS开放获取论文URL进行测试
        known_aps_papers = [
            {
                'title': 'Physical Review X - Open Access Journal',
                'url': 'https://journals.aps.org/prx/',
                'journal': 'Physical Review X',
                'note': '这是期刊主页，需要找到具体论文'
            },
            {
                'title': 'Physical Review Research - Open Access Journal',
                'url': 'https://journals.aps.org/prresearch/',
                'journal': 'Physical Review Research',
                'note': '这是期刊主页，需要找到具体论文'
            }
        ]
        
        print("已知的APS开放获取期刊:")
        for paper in known_aps_papers:
            print(f"  - {paper['title']}")
            print(f"    URL: {paper['url']}")
            print(f"    说明: {paper['note']}")
        
        print("\n建议:")
        print("1. 手动访问这些期刊主页，查找开放获取的论文")
        print("2. 或者使用其他开放获取期刊进行测试")
        print("3. 或者先测试订阅期刊的访问机制")
        
        return
    
    print(f"\n✅ 找到 {len(aps_papers)} 个APS论文")
    print("开始测试PDF提取和下载...")
    print("-" * 40)
    
    # 测试前3个论文
    for i, paper in enumerate(aps_papers[:3], 1):
        print(f"\n测试论文 {i}: {paper['title']}")
        print(f"URL: {paper['url']}")
        print(f"期刊: {paper['journal']}")
        
        try:
            # 提取PDF信息
            print("提取PDF信息...")
            pdf_info = aps_extractor.extract_pdf_info(paper['url'])
            
            if pdf_info:
                print(f"  ✅ PDF信息提取成功")
                print(f"  PDF URL: {pdf_info.pdf_url}")
                print(f"  标题: {pdf_info.title}")
                print(f"  作者: {pdf_info.authors}")
                print(f"  期刊: {pdf_info.journal}")
                print(f"  访问类型: {pdf_info.access_type}")
                
                # 下载PDF
                print("下载PDF...")
                filename = f"aps_{i}_{pdf_info.title[:30].replace(' ', '_').replace('/', '_')}.pdf"
                download_result = pdf_downloader.download_pdf(
                    pdf_info.pdf_url, 
                    filename, 
                    pdf_info.access_type
                )
                
                if download_result.success:
                    print(f"  ✅ PDF下载成功")
                    print(f"  文件路径: {download_result.file_path}")
                    print(f"  文件大小: {download_result.file_size} bytes")
                    print("  🎉 成功完成APS PDF下载测试！")
                    return
                else:
                    print(f"  ❌ PDF下载失败: {download_result.error}")
                    if "403" in str(download_result.error) or "Forbidden" in str(download_result.error):
                        print("  💡 这可能是权限问题，需要开放获取的论文")
                    elif "404" in str(download_result.error):
                        print("  💡 这可能是URL不存在或PDF链接无效")
            else:
                print("  ❌ PDF信息提取失败")
                
        except Exception as e:
            print(f"  ❌ 测试失败: {e}")
    
    print("\n❌ 所有APS论文测试都失败了")
    print("建议:")
    print("1. 手动查找一些真正的APS开放获取论文URL")
    print("2. 或者使用其他开放获取期刊进行测试")
    print("3. 或者先测试订阅期刊的访问机制")

if __name__ == "__main__":
    find_aps_open_access()
