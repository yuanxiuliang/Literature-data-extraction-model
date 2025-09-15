#!/usr/bin/env python3
"""
测试Sci-Hub访问状态
"""

import requests
import time
import logging
from bs4 import BeautifulSoup

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_scihub_access():
    """测试Sci-Hub访问状态"""
    print("测试Sci-Hub访问状态")
    print("=" * 40)
    
    # 测试不同的Sci-Hub镜像
    scihub_urls = [
        "https://sci-hub.in/",
        "https://sci-hub.se/",
        "https://sci-hub.st/",
        "https://sci-hub.ru/"
    ]
    
    # 测试DOI
    test_doi = "10.1103/PhysRevB.105.045103"
    
    for url in scihub_urls:
        print(f"\n测试镜像: {url}")
        try:
            # 测试主页访问
            response = requests.get(url, timeout=30)
            if response.status_code == 200:
                print(f"✅ 主页可访问 (状态码: {response.status_code})")
                
                # 测试DOI搜索
                search_url = f"{url}{test_doi}"
                print(f"测试DOI搜索: {search_url}")
                
                search_response = requests.get(search_url, timeout=30)
                if search_response.status_code == 200:
                    print(f"✅ DOI搜索成功 (状态码: {search_response.status_code})")
                    
                    # 检查页面内容
                    soup = BeautifulSoup(search_response.text, 'html.parser')
                    
                    # 查找PDF链接
                    pdf_links = soup.find_all('a', href=lambda x: x and '.pdf' in x.lower())
                    if pdf_links:
                        print(f"✅ 找到 {len(pdf_links)} 个PDF链接")
                        for link in pdf_links[:3]:  # 显示前3个
                            print(f"   - {link.get('href')}")
                    else:
                        print("❌ 未找到PDF链接")
                        
                        # 检查页面标题
                        title = soup.find('title')
                        if title:
                            print(f"页面标题: {title.get_text()}")
                        
                        # 检查是否有错误信息
                        error_elements = soup.find_all(text=lambda x: x and ('error' in x.lower() or 'not found' in x.lower() or 'unavailable' in x.lower()))
                        if error_elements:
                            print(f"错误信息: {error_elements[0]}")
                        
                        # 输出页面内容的前500字符用于调试
                        print(f"页面内容前500字符: {search_response.text[:500]}")
                else:
                    print(f"❌ DOI搜索失败 (状态码: {search_response.status_code})")
            else:
                print(f"❌ 主页不可访问 (状态码: {response.status_code})")
                
        except Exception as e:
            print(f"❌ 访问失败: {e}")
        
        time.sleep(2)  # 避免请求过快

if __name__ == "__main__":
    test_scihub_access()
