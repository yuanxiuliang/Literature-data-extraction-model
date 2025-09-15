#!/usr/bin/env python3
"""
Sci-Hub大规模测试脚本
从Google Scholar搜索50篇PRB论文，在Sci-Hub上测试下载成功率
"""

import requests
import time
import logging
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re
import os
import json
from dataclasses import dataclass
from typing import List, Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import undetected_chromedriver as uc

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class PaperInfo:
    """论文信息"""
    title: str
    authors: str
    journal: str
    year: str
    doi: str
    url: str

class GoogleScholarSearcher:
    """Google Scholar搜索器"""
    
    def __init__(self):
        self.driver = None
        self._setup_driver()
    
    def _setup_driver(self):
        """设置Selenium驱动"""
        try:
            options = uc.ChromeOptions()
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-blink-features=AutomationControlled')
            
            self.driver = uc.Chrome(options=options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            logger.info("Google Scholar搜索器设置完成")
            
        except Exception as e:
            logger.error(f"Google Scholar搜索器设置失败: {e}")
            raise
    
    def search_prb_papers(self, max_papers=50):
        """搜索PRB论文"""
        try:
            logger.info("开始搜索PRB论文")
            
            # 访问Google Scholar
            self.driver.get("https://scholar.google.com")
            time.sleep(3)
            
            # 搜索PRB论文
            search_query = "site:journals.aps.org/prb single crystal growth"
            search_box = self.driver.find_element(By.NAME, "q")
            search_box.clear()
            search_box.send_keys(search_query)
            search_box.submit()
            
            time.sleep(3)
            
            papers = []
            page_count = 0
            max_pages = 10  # 最多搜索10页
            
            while len(papers) < max_papers and page_count < max_pages:
                logger.info(f"搜索第 {page_count + 1} 页")
                
                # 解析搜索结果
                page_papers = self._parse_search_results()
                papers.extend(page_papers)
                
                logger.info(f"本页找到 {len(page_papers)} 篇论文，总计 {len(papers)} 篇")
                
                # 尝试翻页
                if not self._go_to_next_page():
                    break
                
                page_count += 1
                time.sleep(2)
            
            # 限制到指定数量
            papers = papers[:max_papers]
            logger.info(f"总共找到 {len(papers)} 篇PRB论文")
            
            return papers
            
        except Exception as e:
            logger.error(f"搜索PRB论文失败: {e}")
            return []
    
    def _parse_search_results(self):
        """解析搜索结果"""
        papers = []
        
        try:
            # 查找搜索结果
            result_elements = self.driver.find_elements(By.CSS_SELECTOR, "div.gs_ri")
            
            for element in result_elements:
                try:
                    # 提取标题
                    title_element = element.find_element(By.CSS_SELECTOR, "h3 a")
                    title = title_element.text
                    url = title_element.get_attribute("href")
                    
                    # 提取作者和期刊信息
                    author_info = element.find_element(By.CSS_SELECTOR, "div.gs_a").text
                    
                    # 解析作者信息
                    parts = author_info.split(" - ")
                    authors = parts[0] if len(parts) > 0 else ""
                    journal_year = parts[1] if len(parts) > 1 else ""
                    
                    # 提取期刊和年份
                    journal = ""
                    year = ""
                    if journal_year:
                        # 查找年份
                        year_match = re.search(r'\b(19|20)\d{2}\b', journal_year)
                        if year_match:
                            year = year_match.group()
                            journal = journal_year.replace(year, "").strip()
                        else:
                            journal = journal_year
                    
                    # 提取DOI
                    doi = self._extract_doi_from_url(url)
                    
                    if doi:
                        paper = PaperInfo(
                            title=title,
                            authors=authors,
                            journal=journal,
                            year=year,
                            doi=doi,
                            url=url
                        )
                        papers.append(paper)
                        logger.info(f"找到论文: {title[:50]}...")
                    
                except Exception as e:
                    logger.warning(f"解析论文信息失败: {e}")
                    continue
            
        except Exception as e:
            logger.error(f"解析搜索结果失败: {e}")
        
        return papers
    
    def _extract_doi_from_url(self, url):
        """从URL中提取DOI"""
        try:
            if "journals.aps.org/prb/abstract/" in url:
                # 从APS URL中提取DOI
                doi_match = re.search(r'/abstract/(10\.\d+/[^/]+)', url)
                if doi_match:
                    return doi_match.group(1)
            return None
        except:
            return None
    
    def _go_to_next_page(self):
        """翻到下一页"""
        try:
            next_button = self.driver.find_element(By.CSS_SELECTOR, "a[aria-label='Next']")
            if next_button.is_enabled():
                next_button.click()
                time.sleep(3)
                return True
            return False
        except:
            return False
    
    def close(self):
        """关闭驱动"""
        if self.driver:
            self.driver.quit()

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
    
    def test_paper_download(self, paper: PaperInfo):
        """测试单篇论文下载"""
        try:
            logger.info(f"测试论文: {paper.title[:50]}...")
            
            # 搜索论文
            search_url = f"{self.base_url}{paper.doi}"
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
            
            # 查找PDF链接
            pdf_selectors = [
                'a[href*=".pdf"]',
                'a[href*="pdf"]',
                'a[title*="PDF"]',
                'a[title*="pdf"]',
                '#pdf',
                '.pdf'
            ]
            
            for selector in pdf_selectors:
                try:
                    element = soup.select_one(selector)
                    if element and element.get('href'):
                        href = element['href']
                        if href.startswith('//'):
                            return 'https:' + href
                        elif href.startswith('/'):
                            return self.base_url.rstrip('/') + href
                        elif href.startswith('http'):
                            return href
                        else:
                            return urljoin(self.base_url, href)
                except:
                    continue
            
            return None
            
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

def test_scihub_large_scale():
    """大规模测试Sci-Hub"""
    print("Sci-Hub大规模测试 - 50篇PRB论文")
    print("=" * 60)
    
    # 1. 搜索PRB论文
    print("\n步骤1: 从Google Scholar搜索PRB论文")
    print("-" * 40)
    
    searcher = GoogleScholarSearcher()
    try:
        papers = searcher.search_prb_papers(max_papers=50)
        print(f"✅ 找到 {len(papers)} 篇PRB论文")
        
        if len(papers) == 0:
            print("❌ 未找到任何论文")
            return
        
    except Exception as e:
        print(f"❌ 搜索失败: {e}")
        return
    finally:
        searcher.close()
    
    # 2. 在Sci-Hub上测试下载
    print(f"\n步骤2: 在Sci-Hub上测试 {len(papers)} 篇论文")
    print("-" * 40)
    
    tester = SciHubTester()
    success_count = 0
    failed_papers = []
    
    for i, paper in enumerate(papers, 1):
        print(f"\n测试 {i}/{len(papers)}: {paper.title[:60]}...")
        print(f"DOI: {paper.doi}")
        print(f"年份: {paper.year}")
        
        if tester.test_paper_download(paper):
            print("✅ 成功")
            success_count += 1
        else:
            print("❌ 失败")
            failed_papers.append(paper)
        
        # 避免请求过快，增加延迟
        time.sleep(3)
    
    # 3. 输出结果统计
    print(f"\n测试结果统计")
    print("=" * 60)
    print(f"总论文数: {len(papers)}")
    print(f"成功下载: {success_count}")
    print(f"失败数量: {len(failed_papers)}")
    print(f"成功率: {success_count/len(papers)*100:.1f}%")
    
    # 4. 保存结果到文件
    results = {
        "total_papers": len(papers),
        "success_count": success_count,
        "failed_count": len(failed_papers),
        "success_rate": success_count/len(papers)*100,
        "papers": [
            {
                "title": paper.title,
                "doi": paper.doi,
                "year": paper.year,
                "authors": paper.authors,
                "journal": paper.journal
            }
            for paper in papers
        ],
        "failed_papers": [
            {
                "title": paper.title,
                "doi": paper.doi,
                "year": paper.year,
                "authors": paper.authors,
                "journal": paper.journal
            }
            for paper in failed_papers
        ]
    }
    
    with open("scihub_test_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n📁 详细结果已保存到: scihub_test_results.json")
    
    if success_count > 0:
        print("✅ Sci-Hub方案可行")
    else:
        print("❌ Sci-Hub方案不可行")

if __name__ == "__main__":
    test_scihub_large_scale()
