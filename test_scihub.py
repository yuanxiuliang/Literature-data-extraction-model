#!/usr/bin/env python3
"""
Sci-Hub测试脚本
用于测试Sci-Hub获取APS论文PDF的可行性
"""

import requests
import time
import logging
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re
import os

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
    
    def test_scihub_access(self):
        """测试Sci-Hub网站访问"""
        try:
            logger.info(f"测试访问Sci-Hub: {self.base_url}")
            response = self.session.get(self.base_url, timeout=30)
            
            if response.status_code == 200:
                logger.info("✅ Sci-Hub网站访问成功")
                return True
            else:
                logger.warning(f"⚠️ Sci-Hub访问失败，状态码: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Sci-Hub访问失败: {e}")
            return False
    
    def search_paper(self, doi):
        """搜索论文"""
        try:
            logger.info(f"搜索论文DOI: {doi}")
            
            # 构建搜索URL
            search_url = f"{self.base_url}{doi}"
            
            # 发送请求
            response = self.session.get(search_url, timeout=30)
            
            if response.status_code == 200:
                logger.info("✅ 论文搜索成功")
                return response.text
            else:
                logger.warning(f"⚠️ 论文搜索失败，状态码: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"❌ 论文搜索失败: {e}")
            return None
    
    def extract_pdf_url(self, html_content):
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
            
            # 如果没找到，尝试从页面内容中搜索PDF链接
            if not pdf_url:
                pdf_patterns = [
                    r'href="([^"]*\.pdf[^"]*)"',
                    r'src="([^"]*\.pdf[^"]*)"',
                    r'url\(["\']?([^"\']*\.pdf[^"\']*)["\']?\)'
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
                        break
            
            if pdf_url:
                logger.info(f"✅ 找到PDF链接: {pdf_url}")
                return pdf_url
            else:
                logger.warning("⚠️ 未找到PDF链接")
                return None
                
        except Exception as e:
            logger.error(f"❌ PDF链接提取失败: {e}")
            return None
    
    def download_pdf(self, pdf_url, filename):
        """下载PDF文件"""
        try:
            logger.info(f"下载PDF: {pdf_url}")
            
            response = self.session.get(pdf_url, timeout=60, stream=True)
            
            if response.status_code == 200:
                # 创建下载目录
                os.makedirs("downloads", exist_ok=True)
                
                # 保存文件
                filepath = os.path.join("downloads", filename)
                with open(filepath, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                file_size = os.path.getsize(filepath)
                logger.info(f"✅ PDF下载成功: {filepath} ({file_size} bytes)")
                return True
            else:
                logger.warning(f"⚠️ PDF下载失败，状态码: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ PDF下载失败: {e}")
            return False
    
    def test_complete_workflow(self, doi, filename):
        """测试完整工作流程"""
        try:
            logger.info(f"开始测试完整工作流程: {doi}")
            
            # 1. 搜索论文
            html_content = self.search_paper(doi)
            if not html_content:
                return False
            
            # 2. 提取PDF链接
            pdf_url = self.extract_pdf_url(html_content)
            if not pdf_url:
                return False
            
            # 3. 下载PDF
            success = self.download_pdf(pdf_url, filename)
            return success
            
        except Exception as e:
            logger.error(f"❌ 完整工作流程失败: {e}")
            return False

def test_scihub():
    """测试Sci-Hub功能"""
    print("测试Sci-Hub获取APS论文PDF")
    print("=" * 50)
    
    tester = SciHubTester()
    
    # 1. 测试网站访问
    print("\n步骤1: 测试Sci-Hub网站访问")
    print("-" * 30)
    if not tester.test_scihub_access():
        print("❌ Sci-Hub网站访问失败")
        return
    print("✅ Sci-Hub网站访问成功")
    
    # 2. 测试论文搜索和下载
    print("\n步骤2: 测试论文搜索和下载")
    print("-" * 30)
    
    # 使用之前找到的APS论文DOI进行测试
    test_papers = [
        {
            "doi": "10.1103/PhysRevB.64.144524",
            "title": "Crystal growth, transport properties, and crystal structure",
            "filename": "PhysRevB.64.144524.pdf"
        },
        {
            "doi": "10.1103/PhysRevB.82.064404", 
            "title": "Quantum phase transitions in single-crystal",
            "filename": "PhysRevB.82.064404.pdf"
        },
        {
            "doi": "10.1103/PhysRevB.109.214401",
            "title": "Single-crystal growth and characterization",
            "filename": "PhysRevB.109.214401.pdf"
        }
    ]
    
    success_count = 0
    for i, paper in enumerate(test_papers, 1):
        print(f"\n测试论文 {i}: {paper['title']}")
        print(f"DOI: {paper['doi']}")
        
        if tester.test_complete_workflow(paper['doi'], paper['filename']):
            print("✅ 论文下载成功")
            success_count += 1
        else:
            print("❌ 论文下载失败")
        
        # 等待一下再测试下一个
        time.sleep(2)
    
    print(f"\n测试结果: {success_count}/{len(test_papers)} 成功")
    
    if success_count > 0:
        print("✅ Sci-Hub方案可行")
        print("📁 下载的文件保存在 downloads/ 目录中")
    else:
        print("❌ Sci-Hub方案不可行")

if __name__ == "__main__":
    test_scihub()
