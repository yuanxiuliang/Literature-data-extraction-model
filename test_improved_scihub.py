#!/usr/bin/env python3
"""
改进版Sci-Hub测试
尝试解决PDF链接提取问题
"""

import requests
import time
import logging
from bs4 import BeautifulSoup
import re
import random

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ImprovedSciHubTester:
    """改进版Sci-Hub测试器"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        # 多个Sci-Hub镜像
        self.scihub_urls = [
            "https://sci-hub.in/",
            "https://sci-hub.se/",
            "https://sci-hub.ru/",
            "https://sci-hub.st/",
            "https://sci-hub.si/"
        ]
    
    def test_scihub_mirrors(self):
        """测试不同Sci-Hub镜像的可用性"""
        print("测试Sci-Hub镜像可用性")
        print("=" * 50)
        
        working_mirrors = []
        
        for url in self.scihub_urls:
            try:
                print(f"测试镜像: {url}")
                response = self.session.get(url, timeout=30)
                
                if response.status_code == 200:
                    print(f"✅ 可访问 (状态码: {response.status_code})")
                    working_mirrors.append(url)
                else:
                    print(f"❌ 不可访问 (状态码: {response.status_code})")
                    
            except Exception as e:
                print(f"❌ 访问失败: {e}")
            
            time.sleep(2)
        
        print(f"\n可用镜像: {len(working_mirrors)} 个")
        return working_mirrors
    
    def test_paper_download_improved(self, doi, title):
        """改进版论文下载测试"""
        print(f"\n测试论文: {title[:50]}...")
        print(f"DOI: {doi}")
        
        working_mirrors = self.test_scihub_mirrors()
        
        for mirror_url in working_mirrors:
            try:
                print(f"\n尝试镜像: {mirror_url}")
                
                # 搜索论文
                search_url = f"{mirror_url}{doi}"
                print(f"访问URL: {search_url}")
                
                response = self.session.get(search_url, timeout=60)
                
                if response.status_code != 200:
                    print(f"搜索失败，状态码: {response.status_code}")
                    continue
                
                print("页面加载完成，开始分析...")
                
                # 等待页面加载
                time.sleep(5)
                
                # 分析页面内容
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # 检查页面标题
                title_tag = soup.find('title')
                if title_tag:
                    page_title = title_tag.get_text()
                    print(f"页面标题: {page_title}")
                    
                    if "未找到" in page_title or "not found" in page_title or "отсутствует" in page_title:
                        print("❌ 论文未找到")
                        continue
                
                # 多种方法查找PDF链接
                pdf_url = self._find_pdf_url_advanced(soup, mirror_url)
                
                if pdf_url:
                    print(f"✅ 找到PDF链接: {pdf_url}")
                    
                    # 测试PDF访问
                    if self._test_pdf_access(pdf_url):
                        print("✅ PDF可访问")
                        return True
                    else:
                        print("❌ PDF不可访问")
                else:
                    print("❌ 未找到PDF链接")
                    
                    # 输出调试信息
                    self._debug_page_content(soup)
                
            except Exception as e:
                print(f"❌ 测试失败: {e}")
            
            time.sleep(3)
        
        return False
    
    def _find_pdf_url_advanced(self, soup, base_url):
        """高级PDF链接查找"""
        pdf_url = None
        
        # 方法1: 查找所有包含PDF的链接
        pdf_links = soup.find_all('a', href=lambda x: x and '.pdf' in x.lower())
        if pdf_links:
            pdf_url = self._process_url(pdf_links[0]['href'], base_url)
            print(f"方法1找到PDF: {pdf_url}")
            return pdf_url
        
        # 方法2: 查找iframe中的PDF
        iframes = soup.find_all('iframe')
        for iframe in iframes:
            src = iframe.get('src')
            if src and '.pdf' in src.lower():
                pdf_url = self._process_url(src, base_url)
                print(f"方法2找到PDF: {pdf_url}")
                return pdf_url
        
        # 方法3: 查找嵌入的PDF对象
        objects = soup.find_all('object')
        for obj in objects:
            data = obj.get('data')
            if data and '.pdf' in data.lower():
                pdf_url = self._process_url(data, base_url)
                print(f"方法3找到PDF: {pdf_url}")
                return pdf_url
        
        # 方法4: 使用正则表达式搜索
        page_text = str(soup)
        pdf_patterns = [
            r'href="([^"]*\.pdf[^"]*)"',
            r'src="([^"]*\.pdf[^"]*)"',
            r'url\(["\']?([^"\']*\.pdf[^"\']*)["\']?\)',
            r'https?://[^"\s]*\.pdf[^"\s]*'
        ]
        
        for pattern in pdf_patterns:
            matches = re.findall(pattern, page_text, re.IGNORECASE)
            if matches:
                pdf_url = self._process_url(matches[0], base_url)
                print(f"方法4找到PDF: {pdf_url}")
                return pdf_url
        
        return None
    
    def _process_url(self, url, base_url):
        """处理URL"""
        if url.startswith('//'):
            return 'https:' + url
        elif url.startswith('/'):
            return base_url.rstrip('/') + url
        elif url.startswith('http'):
            return url
        else:
            return base_url.rstrip('/') + '/' + url
    
    def _test_pdf_access(self, pdf_url):
        """测试PDF访问"""
        try:
            response = self.session.head(pdf_url, timeout=30)
            return response.status_code == 200
        except:
            return False
    
    def _debug_page_content(self, soup):
        """调试页面内容"""
        print("\n调试信息:")
        
        # 查找所有链接
        all_links = soup.find_all('a', href=True)
        print(f"页面链接总数: {len(all_links)}")
        
        # 查找包含PDF的链接
        pdf_links = [link for link in all_links if '.pdf' in link['href'].lower()]
        print(f"包含PDF的链接: {len(pdf_links)}")
        
        if pdf_links:
            print("PDF链接示例:")
            for link in pdf_links[:3]:
                print(f"  - {link['href']}")
        
        # 查找iframe
        iframes = soup.find_all('iframe')
        print(f"iframe数量: {len(iframes)}")
        
        if iframes:
            print("iframe示例:")
            for iframe in iframes[:2]:
                src = iframe.get('src', 'No src')
                print(f"  - {src}")

def main():
    """主函数"""
    print("改进版Sci-Hub测试")
    print("=" * 60)
    
    tester = ImprovedSciHubTester()
    
    # 测试论文列表
    test_papers = [
        {
            "doi": "10.1103/PhysRevB.105.045103",
            "title": "Electronic structure and physical properties of EuAuAs single crystal"
        },
        {
            "doi": "10.1038/nature12373",
            "title": "Nature经典论文"
        },
        {
            "doi": "10.1126/science.abc7424",
            "title": "Science开放获取论文"
        }
    ]
    
    success_count = 0
    
    for i, paper in enumerate(test_papers, 1):
        print(f"\n{'='*60}")
        print(f"测试 {i}/{len(test_papers)}")
        
        if tester.test_paper_download_improved(paper['doi'], paper['title']):
            success_count += 1
            print("✅ 成功")
        else:
            print("❌ 失败")
    
    print(f"\n测试结果: {success_count}/{len(test_papers)} 成功")
    
    if success_count > 0:
        print("✅ Sci-Hub方案可行，可以继续优化")
    else:
        print("❌ Sci-Hub方案需要进一步改进")

if __name__ == "__main__":
    main()
