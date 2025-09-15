"""
高级Selenium反爬虫绕过模块
专门用于绕过Google Scholar的反爬虫机制
"""

import time
import random
import logging
from typing import List, Dict, Optional
from dataclasses import dataclass
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
import undetected_chromedriver as uc

logger = logging.getLogger(__name__)

@dataclass
class ScholarSearchResult:
    """Google Scholar搜索结果"""
    title: str
    authors: str
    journal: str
    year: int
    abstract: str
    url: str
    pdf_url: Optional[str] = None
    is_aps: bool = False

class AdvancedSeleniumBypass:
    """高级Selenium反爬虫绕过类"""
    
    def __init__(self, headless: bool = False):
        self.headless = headless
        self.driver = None
        self.wait = None
        self.actions = None
        
        # 自动初始化驱动
        self._setup_driver()
        
        # APS期刊关键词
        self.aps_keywords = [
            "Physical Review B", "Physical Review Materials",
            "Applied Physics Letters", "Journal of Applied Physics",
            "PRB", "PRMaterials", "APL", "JAP"
        ]
        
        # 单晶生长关键词
        self.crystal_growth_keywords = [
            "single crystal growth",
            "crystal growth method", 
            "flux method",
            "chemical vapor transport",
            "CVT",
            "solution growth",
            "crystal synthesis"
        ]
    
    def _setup_driver(self):
        """设置高级Selenium驱动"""
        try:
            # 使用undetected-chromedriver绕过检测
            options = uc.ChromeOptions()
            
            if self.headless:
                options.add_argument('--headless')
            
            # 反检测配置
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-blink-features=AutomationControlled')
            
            # 真实浏览器配置
            options.add_argument('--disable-web-security')
            options.add_argument('--allow-running-insecure-content')
            options.add_argument('--disable-extensions')
            options.add_argument('--disable-plugins')
            options.add_argument('--disable-images')  # 提高速度
            
            # 设置窗口大小
            options.add_argument('--window-size=1920,1080')
            
            # 创建驱动
            self.driver = uc.Chrome(options=options)
            
            # 设置等待
            self.wait = WebDriverWait(self.driver, 20)
            
            # 设置动作链
            self.actions = ActionChains(self.driver)
            
            # 执行反检测脚本
            self._execute_anti_detection_scripts()
            
            logger.info("高级Selenium驱动设置完成")
            
        except Exception as e:
            logger.error(f"设置Selenium驱动失败: {e}")
            raise
    
    def _execute_anti_detection_scripts(self):
        """执行反检测脚本"""
        try:
            # 隐藏webdriver属性
            self.driver.execute_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
            """)
            
            # 修改navigator属性
            self.driver.execute_script("""
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5]
                });
            """)
            
            # 修改chrome属性
            self.driver.execute_script("""
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['en-US', 'en']
                });
            """)
            
            logger.info("反检测脚本执行完成")
            
        except Exception as e:
            logger.warning(f"反检测脚本执行失败: {e}")
    
    def _human_like_delay(self, min_delay: float = 1.0, max_delay: float = 3.0):
        """模拟人类延迟"""
        delay = random.uniform(min_delay, max_delay)
        time.sleep(delay)
    
    def _random_mouse_movement(self):
        """随机鼠标移动"""
        try:
            # 获取窗口大小
            window_size = self.driver.get_window_size()
            width = window_size['width']
            height = window_size['height']
            
            # 随机移动鼠标（限制在安全范围内）
            for _ in range(random.randint(2, 5)):
                x = random.randint(100, width - 100)  # 避免边界
                y = random.randint(100, height - 100)  # 避免边界
                try:
                    self.actions.move_by_offset(x - width//2, y - height//2).perform()
                    self._human_like_delay(0.1, 0.3)
                except Exception as e:
                    logger.warning(f"鼠标移动失败: {e}")
                    break
            
        except Exception as e:
            logger.warning(f"鼠标移动失败: {e}")
    
    def _simulate_human_typing(self, element, text: str):
        """模拟人类打字"""
        try:
            element.clear()
            for char in text:
                element.send_keys(char)
                time.sleep(random.uniform(0.05, 0.15))
        except Exception as e:
            logger.warning(f"模拟打字失败: {e}")
    
    def search_google_scholar(self, query: str, max_results: int = 20) -> List[ScholarSearchResult]:
        """搜索Google Scholar"""
        if not self.driver:
            self._setup_driver()
        
        try:
            logger.info(f"开始搜索Google Scholar: {query}")
            
            # 访问Google Scholar
            self.driver.get("https://scholar.google.com")
            self._human_like_delay(2, 4)
            
            # 随机鼠标移动
            self._random_mouse_movement()
            
            # 查找搜索框
            search_box = self.wait.until(
                EC.presence_of_element_located((By.NAME, "q"))
            )
            
            # 模拟人类输入
            self._simulate_human_typing(search_box, query)
            self._human_like_delay(1, 2)
            
            # 点击搜索按钮
            search_button = self.driver.find_element(By.NAME, "btnG")
            self.actions.move_to_element(search_button).click().perform()
            
            # 等待搜索结果 - 使用更通用的选择器
            try:
                # 等待搜索结果容器出现
                self.wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "[id*='gs_res']"))
                )
            except TimeoutException:
                # 如果上面的选择器失败，尝试等待页面标题变化
                self.wait.until(
                    lambda driver: "scholar.google.com/scholar" in driver.current_url
                )
            
            # 解析搜索结果
            results = self._parse_search_results(max_results)
            
            logger.info(f"搜索完成，找到 {len(results)} 个结果")
            return results
            
        except TimeoutException:
            logger.error("搜索超时，可能被反爬虫机制阻止")
            return []
        except Exception as e:
            logger.error(f"搜索失败: {e}")
            return []
    
    def _parse_search_results(self, max_results: int) -> List[ScholarSearchResult]:
        """解析搜索结果"""
        results = []
        
        try:
            # 查找所有搜索结果
            search_items = self.driver.find_elements(By.CSS_SELECTOR, "div.gs_ri")
            
            for item in search_items[:max_results]:
                try:
                    result = self._parse_single_result(item)
                    if result:
                        results.append(result)
                except Exception as e:
                    logger.warning(f"解析单个结果失败: {e}")
                    continue
            
        except Exception as e:
            logger.error(f"解析搜索结果失败: {e}")
        
        return results
    
    def _parse_single_result(self, item) -> Optional[ScholarSearchResult]:
        """解析单个搜索结果"""
        try:
            # 标题和链接
            title_elem = item.find_element(By.CSS_SELECTOR, "h3.gs_rt a")
            title = title_elem.text.strip()
            url = title_elem.get_attribute('href')
            
            # 作者和期刊信息
            authors_elem = item.find_element(By.CSS_SELECTOR, "div.gs_a")
            authors_text = authors_elem.text.strip()
            
            # 提取期刊和年份
            journal, year = self._extract_journal_and_year(authors_text)
            
            # 摘要
            abstract_elem = item.find_element(By.CSS_SELECTOR, "div.gs_rs")
            abstract = abstract_elem.text.strip()
            
            # PDF链接
            pdf_url = self._extract_pdf_link(item)
            
            # 判断是否为APS期刊
            is_aps = self._is_aps_journal(title, journal)
            
            return ScholarSearchResult(
                title=title,
                authors=authors_text,
                journal=journal,
                year=year,
                abstract=abstract,
                url=url,
                pdf_url=pdf_url,
                is_aps=is_aps
            )
            
        except Exception as e:
            logger.warning(f"解析单个结果失败: {e}")
            return None
    
    def _extract_journal_and_year(self, authors_text: str) -> tuple:
        """提取期刊和年份"""
        import re
        
        # 匹配期刊和年份模式
        pattern = r'(.+?)\s*-\s*(.+?),\s*(\d{4})'
        match = re.search(pattern, authors_text)
        
        if match:
            journal = match.group(2).strip()
            year = int(match.group(3))
            return journal, year
        
        # 如果没有匹配到，尝试其他模式
        year_match = re.search(r'(\d{4})', authors_text)
        year = int(year_match.group(1)) if year_match else 2024
        
        return "Unknown Journal", year
    
    def _extract_pdf_link(self, item) -> Optional[str]:
        """提取PDF链接"""
        try:
            pdf_links = item.find_elements(By.CSS_SELECTOR, "a[href*='.pdf']")
            if pdf_links:
                return pdf_links[0].get_attribute('href')
        except Exception:
            pass
        return None
    
    def _is_aps_journal(self, title: str, journal: str) -> bool:
        """判断是否为APS期刊"""
        text_to_check = f"{title} {journal}".lower()
        return any(keyword.lower() in text_to_check for keyword in self.aps_keywords)
    
    def search_aps_papers_2024(self, max_results: int = 20) -> List[ScholarSearchResult]:
        """搜索2024年APS期刊论文"""
        all_results = []
        
        for keyword in self.crystal_growth_keywords:
            logger.info(f"搜索关键词: {keyword}")
            
            # 构建搜索查询
            query = f"{keyword} 2024"
            
            # 搜索
            results = self.search_google_scholar(query, max_results // len(self.crystal_growth_keywords))
            
            # 过滤APS相关结果
            aps_results = [r for r in results if r.is_aps]
            all_results.extend(aps_results)
            
            # 延迟避免被检测
            self._human_like_delay(3, 6)
        
        # 去重
        unique_results = self._deduplicate_results(all_results)
        
        logger.info(f"总共找到 {len(unique_results)} 篇APS论文")
        return unique_results[:max_results]
    
    def _deduplicate_results(self, results: List[ScholarSearchResult]) -> List[ScholarSearchResult]:
        """去重搜索结果"""
        seen_urls = set()
        unique_results = []
        
        for result in results:
            if result.url not in seen_urls:
                seen_urls.add(result.url)
                unique_results.append(result)
        
        return unique_results
    
    def test_google_scholar_access(self) -> bool:
        """测试Google Scholar访问"""
        try:
            if not self.driver:
                self._setup_driver()
            
            logger.info("测试Google Scholar访问...")
            
            # 访问Google Scholar
            self.driver.get("https://scholar.google.com")
            self._human_like_delay(3, 5)
            
            # 检查页面标题和URL
            title = self.driver.title
            current_url = self.driver.current_url
            
            # 支持任何语言的Google Scholar
            if ("scholar.google.com" in current_url or 
                "Google Scholar" in title or 
                "Google 学术搜索" in title or
                "Google Scholar" in title or
                "Google Scholar" in title):
                logger.info("✅ Google Scholar访问成功")
                logger.info(f"页面标题: {title}")
                logger.info(f"当前URL: {current_url}")
                return True
            else:
                logger.warning(f"⚠️ 页面标题异常: {title}")
                logger.warning(f"当前URL: {current_url}")
                return False
                
        except TimeoutException:
            logger.error("❌ 访问超时，可能被反爬虫机制阻止")
            return False
        except Exception as e:
            logger.error(f"❌ 访问失败: {e}")
            return False
    
    def close(self):
        """关闭驱动"""
        if self.driver:
            self.driver.quit()
            logger.info("Selenium驱动已关闭")

# 测试函数
def test_advanced_selenium_bypass():
    """测试高级Selenium绕过功能"""
    bypass = AdvancedSeleniumBypass(headless=False)  # 显示浏览器窗口
    
    try:
        # 测试访问
        if bypass.test_google_scholar_access():
            print("✅ Google Scholar访问成功")
            
            # 测试搜索
            results = bypass.search_aps_papers_2024(max_results=5)
            print(f"找到 {len(results)} 篇APS论文")
            
            for i, result in enumerate(results, 1):
                print(f"\n{i}. {result.title}")
                print(f"   作者: {result.authors}")
                print(f"   期刊: {result.journal}")
                print(f"   年份: {result.year}")
                print(f"   URL: {result.url}")
                print(f"   PDF: {result.pdf_url}")
        else:
            print("❌ Google Scholar访问失败")
    
    except Exception as e:
        print(f"测试失败: {e}")
    
    finally:
        bypass.close()

if __name__ == "__main__":
    test_advanced_selenium_bypass()
