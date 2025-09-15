#!/usr/bin/env python3
"""
使用已知DOI测试Sci-Hub改进效果
"""

import requests
import time
import logging
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re
import os
import json

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SciHubTester:
    """Sci-Hub测试器"""
    
    def __init__(self, base_url="https://sci-hub.in/"):
        self.base_url = base_url
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
    
    def test_paper_download(self, doi, title):
        """测试单篇论文下载"""
        try:
            logger.info(f"测试论文: {title[:50]}...")
            
            # 搜索论文
            search_url = f"{self.base_url}{doi}"
            logger.info(f"访问URL: {search_url}")
            
            response = self.session.get(search_url, timeout=60)  # 增加超时时间
            
            if response.status_code != 200:
                logger.warning(f"搜索失败，状态码: {response.status_code}")
                return False
            
            logger.info("页面加载完成，开始提取PDF链接...")
            
            # 等待页面完全加载
            time.sleep(3)
            
            # 提取PDF链接
            pdf_url = self._extract_pdf_url(response.text)
            if not pdf_url:
                logger.warning("未找到PDF链接，尝试其他方法...")
                # 尝试从页面内容中搜索PDF链接
                pdf_url = self._search_pdf_in_content(response.text)
                if not pdf_url:
                    logger.warning("仍未找到PDF链接")
                    return False
            
            logger.info(f"找到PDF链接: {pdf_url}")
            
            # 测试PDF访问
            pdf_response = self.session.head(pdf_url, timeout=30)
            if pdf_response.status_code == 200:
                logger.info("✅ PDF可访问")
                return True
            else:
                logger.warning(f"PDF不可访问，状态码: {pdf_response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"测试失败: {e}")
            return False
    
    def _extract_pdf_url(self, html_content):
        """从HTML内容中提取PDF链接"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # 查找PDF链接的多种方式
            pdf_selectors = [
                'a[href*=".pdf"]',
                'a[href*="pdf"]',
                'a[title*="PDF"]',
                'a[title*="pdf"]',
                '#pdf',
                '.pdf',
                'a[onclick*="pdf"]'
            ]
            
            pdf_url = None
            for selector in pdf_selectors:
                try:
                    element = soup.select_one(selector)
                    if element and element.get('href'):
                        href = element['href']
                        if href.startswith('//'):
                            pdf_url = 'https:' + href
                        elif href.startswith('/'):
                            pdf_url = self.base_url.rstrip('/') + href
                        elif href.startswith('http'):
                            pdf_url = href
                        else:
                            pdf_url = urljoin(self.base_url, href)
                        break
                except:
                    continue
            
            return pdf_url
            
        except Exception as e:
            logger.error(f"PDF链接提取失败: {e}")
            return None
    
    def _search_pdf_in_content(self, html_content):
        """从页面内容中搜索PDF链接"""
        try:
            # 使用正则表达式搜索PDF链接
            pdf_patterns = [
                r'href="([^"]*\.pdf[^"]*)"',
                r'src="([^"]*\.pdf[^"]*)"',
                r'url\(["\']?([^"\']*\.pdf[^"\']*)["\']?\)',
                r'https?://[^"\s]*\.pdf[^"\s]*',
                r'//[^"\s]*\.pdf[^"\s]*'
            ]
            
            for pattern in pdf_patterns:
                matches = re.findall(pattern, html_content, re.IGNORECASE)
                if matches:
                    pdf_url = matches[0]
                    if pdf_url.startswith('//'):
                        pdf_url = 'https:' + pdf_url
                    elif pdf_url.startswith('/'):
                        pdf_url = self.base_url.rstrip('/') + pdf_url
                    elif not pdf_url.startswith('http'):
                        pdf_url = urljoin(self.base_url, pdf_url)
                    
                    logger.info(f"通过正则表达式找到PDF链接: {pdf_url}")
                    return pdf_url
            
            # 搜索包含PDF的iframe
            iframe_pattern = r'<iframe[^>]*src="([^"]*)"[^>]*>'
            iframe_matches = re.findall(iframe_pattern, html_content, re.IGNORECASE)
            for iframe_src in iframe_matches:
                if '.pdf' in iframe_src.lower():
                    pdf_url = iframe_src
                    if pdf_url.startswith('//'):
                        pdf_url = 'https:' + pdf_url
                    elif pdf_url.startswith('/'):
                        pdf_url = self.base_url.rstrip('/') + pdf_url
                    elif not pdf_url.startswith('http'):
                        pdf_url = urljoin(self.base_url, pdf_url)
                    
                    logger.info(f"通过iframe找到PDF链接: {pdf_url}")
                    return pdf_url
            
            return None
            
        except Exception as e:
            logger.error(f"PDF链接搜索失败: {e}")
            return None

def test_scihub_with_known_dois():
    """使用已知DOI测试Sci-Hub"""
    print("使用已知DOI测试Sci-Hub改进效果")
    print("=" * 50)
    
    # 已知的PRB论文DOI列表
    test_papers = [
        {
            "doi": "10.1103/PhysRevB.64.144524",
            "title": "Crystal growth, transport properties, and crystal structure"
        },
        {
            "doi": "10.1103/PhysRevB.82.064404", 
            "title": "Quantum phase transitions in single-crystal"
        },
        {
            "doi": "10.1103/PhysRevB.109.214401",
            "title": "Single-crystal growth and characterization"
        },
        {
            "doi": "10.1103/PhysRevB.70.024506",
            "title": "Single-crystal growth and investigation"
        },
        {
            "doi": "10.1103/PhysRevB.89.134504",
            "title": "Comprehensive scenario for single-crystal growth"
        },
        {
            "doi": "10.1103/PhysRevB.99.054435",
            "title": "Crystal growth, microstructure, and physical properties"
        },
        {
            "doi": "10.1103/PhysRevB.78.104512",
            "title": "Single-crystal growth and physical properties"
        },
        {
            "doi": "10.1103/PhysRevB.82.134514",
            "title": "Structural trends from a consistent set"
        },
        {
            "doi": "10.1103/PhysRevB.66.144304",
            "title": "Crystal growth and spectroscopic characterization"
        },
        {
            "doi": "10.1103/PhysRevB.88.045120",
            "title": "Single-crystal growth and physical properties"
        }
    ]
    
    tester = SciHubTester()
    success_count = 0
    failed_papers = []
    
    for i, paper in enumerate(test_papers, 1):
        print(f"\n测试 {i}/{len(test_papers)}: {paper['title'][:60]}...")
        print(f"DOI: {paper['doi']}")
        
        if tester.test_paper_download(paper['doi'], paper['title']):
            print("✅ 成功")
            success_count += 1
        else:
            print("❌ 失败")
            failed_papers.append(paper)
        
        # 避免请求过快，增加延迟
        time.sleep(3)
    
    # 输出结果统计
    print(f"\n测试结果统计")
    print("=" * 50)
    print(f"总论文数: {len(test_papers)}")
    print(f"成功下载: {success_count}")
    print(f"失败数量: {len(failed_papers)}")
    print(f"成功率: {success_count/len(test_papers)*100:.1f}%")
    
    if success_count > 0:
        print("✅ Sci-Hub方案可行")
    else:
        print("❌ Sci-Hub方案不可行")

if __name__ == "__main__":
    test_scihub_with_known_dois()
