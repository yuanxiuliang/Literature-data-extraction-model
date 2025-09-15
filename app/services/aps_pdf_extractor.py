"""
APS PDF提取器
用于从APS期刊网站提取PDF下载链接
"""

import requests
from bs4 import BeautifulSoup
import time
import random
import logging
from typing import Optional, Dict, Any
from urllib.parse import urljoin, urlparse
import re
from dataclasses import dataclass
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from .cloudflare_bypass import CloudflareBypass

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class PDFInfo:
    """PDF信息数据类"""
    pdf_url: str
    file_name: str
    file_size: Optional[int] = None
    access_type: str = "unknown"  # open, subscription, mixed
    requires_auth: bool = False
    error_message: Optional[str] = None

class APSPDFExtractor:
    """APS PDF提取器"""
    
    def __init__(self, use_selenium: bool = True, use_cloudflare_bypass: bool = True):
        self.use_selenium = use_selenium
        self.use_cloudflare_bypass = use_cloudflare_bypass
        self.session = requests.Session()
        self.driver = None
        self.cloudflare_bypass = None
        self._setup_session()
        
        if use_selenium:
            if use_cloudflare_bypass:
                self.cloudflare_bypass = CloudflareBypass(headless=False)
                self.driver = self.cloudflare_bypass.driver
            else:
                self._setup_selenium()
    
    def _setup_session(self):
        """设置请求会话"""
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        })
    
    def _setup_selenium(self):
        """设置Selenium WebDriver"""
        try:
            chrome_options = Options()
            chrome_options.add_argument('--headless')  # 无头模式
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
            
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.set_page_load_timeout(30)
            
        except Exception as e:
            logger.warning(f"Selenium设置失败，将使用requests: {e}")
            self.use_selenium = False
    
    def extract_pdf_info(self, article_url: str) -> Optional[PDFInfo]:
        """
        提取PDF信息
        
        Args:
            article_url: 文章URL
            
        Returns:
            PDFInfo: PDF信息，如果失败返回None
        """
        try:
            # 识别出版社类型
            publisher = self._identify_publisher(article_url)
            
            if publisher == "aps_journals":
                return self._extract_aps_journals_pdf(article_url)
            elif publisher == "aip_scitation":
                return self._extract_aip_scitation_pdf(article_url)
            else:
                logger.warning(f"未知的APS出版社: {publisher}")
                return None
                
        except Exception as e:
            logger.error(f"PDF信息提取失败: {e}")
            return PDFInfo(
                pdf_url="",
                file_name="",
                error_message=str(e)
            )
    
    def _identify_publisher(self, url: str) -> str:
        """识别出版社类型"""
        if "journals.aps.org" in url:
            return "aps_journals"
        elif "aip.scitation.org" in url:
            return "aip_scitation"
        else:
            return "unknown"
    
    def _extract_aps_journals_pdf(self, article_url: str) -> Optional[PDFInfo]:
        """提取APS Journals PDF信息"""
        try:
            if self.use_selenium and self.driver:
                if self.use_cloudflare_bypass and self.cloudflare_bypass:
                    return self._extract_with_cloudflare_bypass(article_url, "aps_journals")
                else:
                    return self._extract_with_selenium(article_url, "aps_journals")
            else:
                return self._extract_with_requests(article_url, "aps_journals")
                
        except Exception as e:
            logger.error(f"APS Journals PDF提取失败: {e}")
            return None
    
    def _extract_with_cloudflare_bypass(self, article_url: str, publisher: str) -> Optional[PDFInfo]:
        """使用Cloudflare绕过提取PDF信息"""
        try:
            logger.info(f"使用Cloudflare绕过访问: {article_url}")
            
            # 绕过Cloudflare
            success = self.cloudflare_bypass.bypass_cloudflare(article_url)
            if not success:
                logger.error("Cloudflare绕过失败")
                return PDFInfo(
                    pdf_url="",
                    file_name="",
                    error_message="Cloudflare绕过失败"
                )
            
            # 等待页面完全加载
            time.sleep(3)
            
            # 获取页面内容
            page_source = self.cloudflare_bypass.get_page_content()
            if not page_source:
                logger.error("无法获取页面内容")
                return PDFInfo(
                    pdf_url="",
                    file_name="",
                    error_message="无法获取页面内容"
                )
            
            # 解析PDF链接
            soup = BeautifulSoup(page_source, 'html.parser')
            
            if publisher == "aps_journals":
                return self._parse_aps_journals_pdf_from_soup(soup, article_url)
            else:
                logger.warning(f"不支持的出版社类型: {publisher}")
                return None
                
        except Exception as e:
            logger.error(f"Cloudflare绕过提取失败: {e}")
            return PDFInfo(
                pdf_url="",
                file_name="",
                error_message=str(e)
            )
    
    def _parse_aps_journals_pdf_from_soup(self, soup: BeautifulSoup, article_url: str) -> Optional[PDFInfo]:
        """从BeautifulSoup解析APS Journals PDF信息"""
        try:
            # 查找PDF下载链接
            pdf_selectors = [
                'a[href*=".pdf"]',
                'a[href*="pdf"]',
                'a[title*="PDF"]',
                'a[title*="pdf"]',
                '.pdf-download',
                '.download-pdf',
                '[data-pdf]'
            ]
            
            pdf_url = None
            for selector in pdf_selectors:
                try:
                    pdf_link = soup.select_one(selector)
                    if pdf_link and pdf_link.get('href'):
                        pdf_url = urljoin(article_url, pdf_link['href'])
                        break
                except:
                    continue
            
            if not pdf_url:
                # 尝试从页面中查找PDF相关的文本链接
                pdf_links = soup.find_all('a', href=True)
                for link in pdf_links:
                    href = link.get('href', '')
                    if 'pdf' in href.lower() or 'download' in href.lower():
                        pdf_url = urljoin(article_url, href)
                        break
            
            if pdf_url:
                # 生成文件名
                file_name = self._generate_filename(article_url, pdf_url)
                
                logger.info(f"找到PDF链接: {pdf_url}")
                return PDFInfo(
                    pdf_url=pdf_url,
                    file_name=file_name,
                    access_type="unknown",
                    requires_auth=False
                )
            else:
                logger.warning("未找到PDF下载链接")
                return PDFInfo(
                    pdf_url="",
                    file_name="",
                    error_message="未找到PDF下载链接"
                )
                
        except Exception as e:
            logger.error(f"解析APS Journals PDF失败: {e}")
            return PDFInfo(
                pdf_url="",
                file_name="",
                error_message=str(e)
            )
    
    def _extract_aip_scitation_pdf(self, article_url: str) -> Optional[PDFInfo]:
        """提取AIP Scitation PDF信息"""
        try:
            if self.use_selenium and self.driver:
                return self._extract_with_selenium(article_url, "aip_scitation")
            else:
                return self._extract_with_requests(article_url, "aip_scitation")
                
        except Exception as e:
            logger.error(f"AIP Scitation PDF提取失败: {e}")
            return None
    
    def _extract_with_selenium(self, article_url: str, publisher: str) -> Optional[PDFInfo]:
        """使用Selenium提取PDF信息"""
        try:
            self.driver.get(article_url)
            
            # 等待页面加载
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            if publisher == "aps_journals":
                return self._parse_aps_journals_selenium()
            elif publisher == "aip_scitation":
                return self._parse_aip_scitation_selenium()
            else:
                return None
                
        except TimeoutException:
            logger.error("页面加载超时")
            return None
        except Exception as e:
            logger.error(f"Selenium提取失败: {e}")
            return None
    
    def _extract_with_requests(self, article_url: str, publisher: str) -> Optional[PDFInfo]:
        """使用requests提取PDF信息"""
        try:
            response = self.session.get(article_url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            if publisher == "aps_journals":
                return self._parse_aps_journals_requests(soup, article_url)
            elif publisher == "aip_scitation":
                return self._parse_aip_scitation_requests(soup, article_url)
            else:
                return None
                
        except Exception as e:
            logger.error(f"Requests提取失败: {e}")
            return None
    
    def _parse_aps_journals_selenium(self) -> Optional[PDFInfo]:
        """解析APS Journals页面（Selenium）"""
        try:
            # 查找PDF下载链接
            pdf_links = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='/pdf/']")
            
            if not pdf_links:
                # 尝试其他选择器
                pdf_links = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='.pdf']")
            
            if pdf_links:
                pdf_url = pdf_links[0].get_attribute('href')
                if not pdf_url.startswith('http'):
                    pdf_url = urljoin("https://journals.aps.org", pdf_url)
                
                # 生成文件名
                file_name = self._generate_filename(self.driver.current_url)
                
                # 检查访问权限
                access_type = self._check_access_type_aps_journals()
                
                return PDFInfo(
                    pdf_url=pdf_url,
                    file_name=file_name,
                    access_type=access_type,
                    requires_auth=access_type == "subscription"
                )
            else:
                logger.warning("未找到PDF下载链接")
                return None
                
        except Exception as e:
            logger.error(f"APS Journals解析失败: {e}")
            return None
    
    def _parse_aip_scitation_selenium(self) -> Optional[PDFInfo]:
        """解析AIP Scitation页面（Selenium）"""
        try:
            # 查找PDF下载链接
            pdf_links = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='/doi/pdf/']")
            
            if not pdf_links:
                # 尝试其他选择器
                pdf_links = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='.pdf']")
            
            if pdf_links:
                pdf_url = pdf_links[0].get_attribute('href')
                if not pdf_url.startswith('http'):
                    pdf_url = urljoin("https://aip.scitation.org", pdf_url)
                
                # 生成文件名
                file_name = self._generate_filename(self.driver.current_url)
                
                # 检查访问权限
                access_type = self._check_access_type_aip_scitation()
                
                return PDFInfo(
                    pdf_url=pdf_url,
                    file_name=file_name,
                    access_type=access_type,
                    requires_auth=access_type == "subscription"
                )
            else:
                logger.warning("未找到PDF下载链接")
                return None
                
        except Exception as e:
            logger.error(f"AIP Scitation解析失败: {e}")
            return None
    
    def _parse_aps_journals_requests(self, soup: BeautifulSoup, article_url: str) -> Optional[PDFInfo]:
        """解析APS Journals页面（requests）"""
        try:
            # 查找PDF下载链接
            pdf_links = soup.find_all('a', href=re.compile(r'/pdf/'))
            
            if not pdf_links:
                # 尝试其他选择器
                pdf_links = soup.find_all('a', href=re.compile(r'\.pdf'))
            
            if pdf_links:
                pdf_url = pdf_links[0].get('href')
                if not pdf_url.startswith('http'):
                    pdf_url = urljoin("https://journals.aps.org", pdf_url)
                
                # 生成文件名
                file_name = self._generate_filename(article_url)
                
                # 检查访问权限
                access_type = self._check_access_type_aps_journals_requests(soup)
                
                return PDFInfo(
                    pdf_url=pdf_url,
                    file_name=file_name,
                    access_type=access_type,
                    requires_auth=access_type == "subscription"
                )
            else:
                logger.warning("未找到PDF下载链接")
                return None
                
        except Exception as e:
            logger.error(f"APS Journals解析失败: {e}")
            return None
    
    def _parse_aip_scitation_requests(self, soup: BeautifulSoup, article_url: str) -> Optional[PDFInfo]:
        """解析AIP Scitation页面（requests）"""
        try:
            # 查找PDF下载链接
            pdf_links = soup.find_all('a', href=re.compile(r'/doi/pdf/'))
            
            if not pdf_links:
                # 尝试其他选择器
                pdf_links = soup.find_all('a', href=re.compile(r'\.pdf'))
            
            if pdf_links:
                pdf_url = pdf_links[0].get('href')
                if not pdf_url.startswith('http'):
                    pdf_url = urljoin("https://aip.scitation.org", pdf_url)
                
                # 生成文件名
                file_name = self._generate_filename(article_url)
                
                # 检查访问权限
                access_type = self._check_access_type_aip_scitation_requests(soup)
                
                return PDFInfo(
                    pdf_url=pdf_url,
                    file_name=file_name,
                    access_type=access_type,
                    requires_auth=access_type == "subscription"
                )
            else:
                logger.warning("未找到PDF下载链接")
                return None
                
        except Exception as e:
            logger.error(f"AIP Scitation解析失败: {e}")
            return None
    
    def _check_access_type_aps_journals(self) -> str:
        """检查APS Journals访问权限（Selenium）"""
        try:
            # 查找开放获取标识
            open_access_indicators = self.driver.find_elements(By.CSS_SELECTOR, 
                "[class*='open'], [class*='free'], [class*='access']")
            
            if open_access_indicators:
                return "open"
            
            # 查找订阅标识
            subscription_indicators = self.driver.find_elements(By.CSS_SELECTOR,
                "[class*='subscription'], [class*='paywall'], [class*='locked']")
            
            if subscription_indicators:
                return "subscription"
            
            return "mixed"
            
        except Exception:
            return "unknown"
    
    def _check_access_type_aip_scitation(self) -> str:
        """检查AIP Scitation访问权限（Selenium）"""
        try:
            # 查找开放获取标识
            open_access_indicators = self.driver.find_elements(By.CSS_SELECTOR,
                "[class*='open'], [class*='free'], [class*='access']")
            
            if open_access_indicators:
                return "open"
            
            # 查找订阅标识
            subscription_indicators = self.driver.find_elements(By.CSS_SELECTOR,
                "[class*='subscription'], [class*='paywall'], [class*='locked']")
            
            if subscription_indicators:
                return "subscription"
            
            return "mixed"
            
        except Exception:
            return "unknown"
    
    def _check_access_type_aps_journals_requests(self, soup: BeautifulSoup) -> str:
        """检查APS Journals访问权限（requests）"""
        try:
            # 查找开放获取标识
            open_access_indicators = soup.find_all(class_=re.compile(r'open|free|access'))
            
            if open_access_indicators:
                return "open"
            
            # 查找订阅标识
            subscription_indicators = soup.find_all(class_=re.compile(r'subscription|paywall|locked'))
            
            if subscription_indicators:
                return "subscription"
            
            return "mixed"
            
        except Exception:
            return "unknown"
    
    def _check_access_type_aip_scitation_requests(self, soup: BeautifulSoup) -> str:
        """检查AIP Scitation访问权限（requests）"""
        try:
            # 查找开放获取标识
            open_access_indicators = soup.find_all(class_=re.compile(r'open|free|access'))
            
            if open_access_indicators:
                return "open"
            
            # 查找订阅标识
            subscription_indicators = soup.find_all(class_=re.compile(r'subscription|paywall|locked'))
            
            if subscription_indicators:
                return "subscription"
            
            return "mixed"
            
        except Exception:
            return "unknown"
    
    def _generate_filename(self, url: str) -> str:
        """生成文件名"""
        try:
            # 从URL中提取DOI或文章ID
            if '/prb/' in url:
                # Physical Review B
                match = re.search(r'/prb/(?:abstract/)?(10\.1103/PhysRevB\.\d+\.\d+)', url)
                if match:
                    return f"PRB_{match.group(1).replace('.', '_')}.pdf"
            elif '/prmaterials/' in url:
                # Physical Review Materials
                match = re.search(r'/prmaterials/(?:abstract/)?(10\.1103/PhysRevMaterials\.\d+\.\d+)', url)
                if match:
                    return f"PRMaterials_{match.group(1).replace('.', '_')}.pdf"
            elif '/doi/' in url:
                # AIP Scitation
                match = re.search(r'/doi/(10\.\d+/[^/]+)', url)
                if match:
                    return f"AIP_{match.group(1).replace('.', '_').replace('/', '_')}.pdf"
            
            # 默认文件名
            return f"APS_Paper_{int(time.time())}.pdf"
            
        except Exception:
            return f"APS_Paper_{int(time.time())}.pdf"
    
    def close(self):
        """关闭资源"""
        if self.driver:
            self.driver.quit()
        self.session.close()

# 测试函数
def test_aps_pdf_extractor():
    """测试APS PDF提取器"""
    extractor = APSPDFExtractor(use_selenium=False)  # 先测试requests模式
    
    # 测试URL（需要替换为真实的APS文章URL）
    test_urls = [
        "https://journals.aps.org/prb/abstract/10.1103/PhysRevB.123.456789",
        "https://aip.scitation.org/doi/10.1063/5.0123456"
    ]
    
    for url in test_urls:
        print(f"\n测试URL: {url}")
        pdf_info = extractor.extract_pdf_info(url)
        
        if pdf_info:
            print(f"PDF URL: {pdf_info.pdf_url}")
            print(f"文件名: {pdf_info.file_name}")
            print(f"访问类型: {pdf_info.access_type}")
            print(f"需要认证: {pdf_info.requires_auth}")
        else:
            print("PDF信息提取失败")
    
    extractor.close()

if __name__ == "__main__":
    test_aps_pdf_extractor()
