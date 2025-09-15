#!/usr/bin/env python3
"""
测试开放获取论文的Sci-Hub下载
"""

import requests
import time
import logging
from bs4 import BeautifulSoup

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_open_access_papers():
    """测试开放获取论文"""
    print("测试开放获取论文的Sci-Hub下载")
    print("=" * 50)
    
    # 测试一些开放获取的论文DOI
    test_papers = [
        {
            "doi": "10.1038/s41586-020-2649-2",
            "title": "Nature开放获取论文",
            "expected": "应该能找到"
        },
        {
            "doi": "10.1126/science.abc7424",
            "title": "Science开放获取论文", 
            "expected": "应该能找到"
        },
        {
            "doi": "10.1103/PhysRevLett.125.077001",
            "title": "PRL开放获取论文",
            "expected": "可能找不到"
        },
        {
            "doi": "10.1038/nature12373",
            "title": "Nature经典论文",
            "expected": "应该能找到"
        }
    ]
    
    scihub_url = "https://sci-hub.in/"
    
    for i, paper in enumerate(test_papers, 1):
        print(f"\n测试 {i}/{len(test_papers)}: {paper['title']}")
        print(f"DOI: {paper['doi']}")
        print(f"预期: {paper['expected']}")
        
        try:
            search_url = f"{scihub_url}{paper['doi']}"
            print(f"访问URL: {search_url}")
            
            response = requests.get(search_url, timeout=30)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # 检查页面标题
                title = soup.find('title')
                if title:
                    page_title = title.get_text()
                    print(f"页面标题: {page_title}")
                    
                    if "未找到" in page_title or "отсутствует" in page_title:
                        print("❌ 论文未找到")
                    else:
                        print("✅ 论文找到")
                        
                        # 查找PDF链接
                        pdf_links = soup.find_all('a', href=lambda x: x and '.pdf' in x.lower())
                        if pdf_links:
                            print(f"✅ 找到 {len(pdf_links)} 个PDF链接")
                            for link in pdf_links[:2]:  # 显示前2个
                                print(f"   - {link.get('href')}")
                        else:
                            print("❌ 未找到PDF链接")
                            
                            # 检查iframe
                            iframes = soup.find_all('iframe')
                            if iframes:
                                print(f"找到 {len(iframes)} 个iframe")
                                for iframe in iframes[:2]:
                                    src = iframe.get('src')
                                    if src:
                                        print(f"   - iframe src: {src}")
                else:
                    print("❌ 无法获取页面标题")
            else:
                print(f"❌ 访问失败 (状态码: {response.status_code})")
                
        except Exception as e:
            print(f"❌ 测试失败: {e}")
        
        time.sleep(2)  # 避免请求过快

if __name__ == "__main__":
    test_open_access_papers()
