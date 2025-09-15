#!/usr/bin/env python3
"""
Playwright + Stealth 测试脚本
用于测试Playwright + Stealth方案对APS网站的绕过效果
"""

import asyncio
import time
import logging
from playwright.async_api import async_playwright
from playwright_stealth import Stealth
import json

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PlaywrightStealthTester:
    """Playwright + Stealth 测试器"""
    
    def __init__(self):
        self.browser = None
        self.context = None
        self.page = None
    
    async def setup(self, headless=False):
        """设置Playwright浏览器"""
        try:
            playwright = await async_playwright().start()
            
            # 启动浏览器
            self.browser = await playwright.chromium.launch(
                headless=headless,
                args=[
                    '--no-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-blink-features=AutomationControlled',
                    '--disable-web-security',
                    '--allow-running-insecure-content',
                    '--disable-extensions',
                    '--disable-plugins',
                    '--disable-images',  # 禁用图片加载以提高速度
                ]
            )
            
            # 创建上下文
            self.context = await self.browser.new_context(
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                viewport={'width': 1920, 'height': 1080},
                locale='en-US',
                timezone_id='America/New_York'
            )
            
            # 创建页面
            self.page = await self.context.new_page()
            
            # 应用stealth插件
            stealth_config = Stealth()
            await stealth_config.apply_stealth_async(self.page)
            
            logger.info("Playwright + Stealth 设置完成")
            return True
            
        except Exception as e:
            logger.error(f"Playwright设置失败: {e}")
            return False
    
    async def test_aps_access(self, url):
        """测试APS网站访问"""
        try:
            logger.info(f"测试访问: {url}")
            
            # 访问页面
            response = await self.page.goto(url, wait_until='domcontentloaded', timeout=30000)
            
            # 等待页面加载
            await asyncio.sleep(3)
            
            # 检查页面状态
            title = await self.page.title()
            current_url = self.page.url
            
            logger.info(f"页面标题: {title}")
            logger.info(f"当前URL: {current_url}")
            
            # 检查是否遇到Cloudflare
            page_content = await self.page.content()
            is_cloudflare = self._check_cloudflare(page_content, title)
            
            if is_cloudflare:
                logger.warning("检测到Cloudflare保护")
                return await self._handle_cloudflare()
            else:
                logger.info("成功访问，未遇到Cloudflare")
                return True
                
        except Exception as e:
            logger.error(f"访问失败: {e}")
            return False
    
    def _check_cloudflare(self, content, title):
        """检查是否遇到Cloudflare"""
        cloudflare_indicators = [
            'cloudflare',
            'checking your browser',
            'please wait',
            'ddos protection',
            'security check',
            'cf-',
            'ray id',
            'verify you are human'
        ]
        
        content_lower = content.lower()
        title_lower = title.lower()
        
        return any(indicator in content_lower or indicator in title_lower 
                  for indicator in cloudflare_indicators)
    
    async def _handle_cloudflare(self):
        """处理Cloudflare挑战"""
        try:
            logger.info("开始处理Cloudflare挑战...")
            
            # 等待挑战完成
            max_wait = 60
            start_time = time.time()
            
            while time.time() - start_time < max_wait:
                await asyncio.sleep(2)
                
                # 检查是否通过挑战
                title = await self.page.title()
                content = await self.page.content()
                
                if not self._check_cloudflare(content, title):
                    logger.info("Cloudflare挑战已通过")
                    return True
                
                # 模拟人类行为
                await self._simulate_human_behavior()
                
                # 尝试点击验证按钮
                if await self._click_verify_button():
                    await asyncio.sleep(3)
            
            logger.warning("Cloudflare挑战超时")
            return False
            
        except Exception as e:
            logger.error(f"处理Cloudflare挑战失败: {e}")
            return False
    
    async def _simulate_human_behavior(self):
        """模拟人类行为"""
        try:
            # 随机鼠标移动
            await self.page.mouse.move(
                x=500 + (time.time() % 100),
                y=300 + (time.time() % 100)
            )
            
            # 随机滚动
            await self.page.evaluate(f"window.scrollBy(0, {int(time.time() % 200 - 100)})")
            
            # 随机等待
            await asyncio.sleep(1 + (time.time() % 2))
            
        except Exception as e:
            logger.warning(f"模拟人类行为失败: {e}")
    
    async def _click_verify_button(self):
        """点击验证按钮"""
        try:
            # 查找验证按钮
            button_selectors = [
                "input[type='submit']",
                "button[type='submit']",
                ".cf-button",
                "#cf-button",
                "input[value*='verify']",
                "input[value*='Continue']",
                ".btn-primary",
                ".btn-submit"
            ]
            
            for selector in button_selectors:
                try:
                    button = await self.page.query_selector(selector)
                    if button:
                        is_visible = await button.is_visible()
                        is_enabled = await button.is_enabled()
                        
                        if is_visible and is_enabled:
                            await button.click()
                            logger.info("点击了验证按钮")
                            return True
                except:
                    continue
            
            return False
            
        except Exception as e:
            logger.warning(f"点击验证按钮失败: {e}")
            return False
    
    async def test_pdf_extraction(self, url):
        """测试PDF提取"""
        try:
            logger.info("测试PDF提取...")
            
            # 查找PDF链接
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
                    element = await self.page.query_selector(selector)
                    if element:
                        href = await element.get_attribute('href')
                        if href:
                            pdf_url = href
                            break
                except:
                    continue
            
            if pdf_url:
                logger.info(f"找到PDF链接: {pdf_url}")
                return pdf_url
            else:
                logger.warning("未找到PDF链接")
                return None
                
        except Exception as e:
            logger.error(f"PDF提取失败: {e}")
            return None
    
    async def close(self):
        """关闭浏览器"""
        try:
            if self.browser:
                await self.browser.close()
                logger.info("Playwright浏览器已关闭")
        except Exception as e:
            logger.warning(f"关闭浏览器时出错: {e}")

async def test_playwright_stealth():
    """测试Playwright + Stealth功能"""
    print("测试Playwright + Stealth方案")
    print("=" * 50)
    
    tester = PlaywrightStealthTester()
    
    try:
        # 设置浏览器
        if not await tester.setup(headless=False):
            print("❌ 浏览器设置失败")
            return
        
        print("✅ 浏览器设置成功")
        
        # 测试APS网站访问
        test_urls = [
            "https://journals.aps.org/prb/abstract/10.1103/PhysRevB.64.144524",
            "https://journals.aps.org/prb/abstract/10.1103/PhysRevB.82.064404",
            "https://journals.aps.org/prb/abstract/10.1103/PhysRevB.109.214401"
        ]
        
        success_count = 0
        for i, url in enumerate(test_urls, 1):
            print(f"\n测试 {i}: {url}")
            print("-" * 30)
            
            if await tester.test_aps_access(url):
                print("✅ 访问成功")
                
                # 测试PDF提取
                pdf_url = await tester.test_pdf_extraction(url)
                if pdf_url:
                    print(f"✅ PDF提取成功: {pdf_url}")
                else:
                    print("❌ PDF提取失败")
                
                success_count += 1
            else:
                print("❌ 访问失败")
            
            # 等待一下再测试下一个
            await asyncio.sleep(2)
        
        print(f"\n测试结果: {success_count}/{len(test_urls)} 成功")
        
        if success_count > 0:
            print("✅ Playwright + Stealth方案有效")
        else:
            print("❌ Playwright + Stealth方案无效")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
    
    finally:
        await tester.close()

if __name__ == "__main__":
    asyncio.run(test_playwright_stealth())
