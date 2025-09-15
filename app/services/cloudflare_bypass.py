"""
Cloudflare绕过模块
专门用于绕过APS网站的Cloudflare反爬虫机制
"""

import time
import random
import logging
from typing import Optional, Dict, Any
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import undetected_chromedriver as uc
from bs4 import BeautifulSoup
import requests

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CloudflareBypass:
    """Cloudflare绕过器"""
    
    def __init__(self, headless: bool = False):
        self.headless = headless
        self.driver = None
        self._setup_driver()
    
    def _setup_driver(self):
        """设置反检测Chrome驱动"""
        try:
            options = uc.ChromeOptions()
            
            if self.headless:
                options.add_argument('--headless')
            
            # 基本设置
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-blink-features=AutomationControlled')
            
            # 设置用户代理
            user_agents = [
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            ]
            options.add_argument(f'--user-agent={random.choice(user_agents)}')
            
            # 创建驱动
            self.driver = uc.Chrome(options=options)
            
            # 执行反检测脚本
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            self.driver.execute_script("Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]})")
            self.driver.execute_script("Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']})")
            
            logger.info("Cloudflare绕过驱动设置完成")
            
        except Exception as e:
            logger.error(f"Cloudflare绕过驱动设置失败: {e}")
            raise
    
    def bypass_cloudflare(self, url: str, max_wait: int = 30) -> bool:
        """绕过Cloudflare保护"""
        try:
            logger.info(f"尝试访问URL: {url}")
            self.driver.get(url)
            
            # 等待页面加载
            time.sleep(3)
            
            # 检查是否遇到Cloudflare
            if self._is_cloudflare_challenge():
                logger.info("检测到Cloudflare挑战，开始绕过...")
                return self._handle_cloudflare_challenge(max_wait)
            else:
                logger.info("未检测到Cloudflare挑战，直接访问成功")
                return True
                
        except Exception as e:
            logger.error(f"访问URL失败: {e}")
            return False
    
    def _is_cloudflare_challenge(self) -> bool:
        """检查是否遇到Cloudflare挑战"""
        try:
            # 检查页面标题
            title = self.driver.title.lower()
            if any(keyword in title for keyword in ['cloudflare', 'checking your browser', 'please wait']):
                return True
            
            # 检查页面内容
            page_source = self.driver.page_source.lower()
            cloudflare_indicators = [
                'cloudflare',
                'checking your browser',
                'please wait',
                'ddos protection',
                'security check',
                'cf-',
                'ray id'
            ]
            
            if any(indicator in page_source for indicator in cloudflare_indicators):
                return True
            
            # 检查特定元素
            try:
                self.driver.find_element(By.CSS_SELECTOR, "[data-ray]")
                return True
            except NoSuchElementException:
                pass
            
            return False
            
        except Exception as e:
            logger.warning(f"检查Cloudflare挑战时出错: {e}")
            return False
    
    def _handle_cloudflare_challenge(self, max_wait: int = 30) -> bool:
        """处理Cloudflare挑战"""
        try:
            logger.info("开始处理Cloudflare挑战...")
            
            # 等待挑战完成
            start_time = time.time()
            while time.time() - start_time < max_wait:
                time.sleep(1)
                
                # 检查是否通过挑战
                if not self._is_cloudflare_challenge():
                    logger.info("Cloudflare挑战已通过")
                    return True
                
                # 模拟人类行为
                self._simulate_human_behavior()
                
                # 检查是否有验证按钮需要点击
                if self._click_verify_button():
                    time.sleep(2)
            
            logger.warning("Cloudflare挑战超时")
            return False
            
        except Exception as e:
            logger.error(f"处理Cloudflare挑战失败: {e}")
            return False
    
    def _simulate_human_behavior(self):
        """模拟人类行为"""
        try:
            # 随机鼠标移动
            actions = ActionChains(self.driver)
            window_size = self.driver.get_window_size()
            x = random.randint(100, window_size['width'] - 100)
            y = random.randint(100, window_size['height'] - 100)
            actions.move_by_offset(x, y).perform()
            
            # 随机滚动
            scroll_amount = random.randint(-300, 300)
            self.driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
            
            # 随机等待
            time.sleep(random.uniform(0.5, 2.0))
            
        except Exception as e:
            logger.warning(f"模拟人类行为失败: {e}")
    
    def _click_verify_button(self) -> bool:
        """点击验证按钮"""
        try:
            # 查找常见的验证按钮
            button_selectors = [
                "input[type='submit']",
                "button[type='submit']",
                ".cf-button",
                "#cf-button",
                "input[value*='verify']",
                "button:contains('Verify')",
                "input[value*='Continue']"
            ]
            
            for selector in button_selectors:
                try:
                    button = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if button.is_displayed() and button.is_enabled():
                        button.click()
                        logger.info("点击了验证按钮")
                        return True
                except NoSuchElementException:
                    continue
            
            return False
            
        except Exception as e:
            logger.warning(f"点击验证按钮失败: {e}")
            return False
    
    def get_page_content(self) -> Optional[str]:
        """获取页面内容"""
        try:
            return self.driver.page_source
        except Exception as e:
            logger.error(f"获取页面内容失败: {e}")
            return None
    
    def get_current_url(self) -> Optional[str]:
        """获取当前URL"""
        try:
            return self.driver.current_url
        except Exception as e:
            logger.error(f"获取当前URL失败: {e}")
            return None
    
    def close(self):
        """关闭驱动"""
        try:
            if self.driver:
                self.driver.quit()
                logger.info("Cloudflare绕过驱动已关闭")
        except Exception as e:
            logger.warning(f"关闭驱动时出错: {e}")

def test_cloudflare_bypass():
    """测试Cloudflare绕过功能"""
    print("测试Cloudflare绕过功能")
    print("=" * 50)
    
    bypass = CloudflareBypass(headless=False)
    
    try:
        # 测试访问APS网站
        test_url = "https://journals.aps.org/prb/abstract/10.1103/PhysRevB.64.144524"
        success = bypass.bypass_cloudflare(test_url)
        
        if success:
            print("✅ Cloudflare绕过成功")
            print(f"当前URL: {bypass.get_current_url()}")
            print(f"页面标题: {bypass.driver.title}")
        else:
            print("❌ Cloudflare绕过失败")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
    
    finally:
        input("按回车键关闭浏览器...")
        bypass.close()

if __name__ == "__main__":
    test_cloudflare_bypass()
