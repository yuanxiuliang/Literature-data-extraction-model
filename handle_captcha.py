#!/usr/bin/env python3
"""
人机验证处理工具
专门用于处理Google Scholar的人机验证问题
"""

import time
from app.services.advanced_selenium_bypass import AdvancedSeleniumBypass

def handle_google_scholar_captcha():
    """专门处理Google Scholar人机验证"""
    print("🔐 Google Scholar 人机验证处理工具")
    print("=" * 50)
    print("此工具将帮助您完成Google Scholar的人机验证")
    print()
    
    # 初始化浏览器
    bypass = AdvancedSeleniumBypass(headless=False)
    
    try:
        # 优化浏览器窗口
        print("步骤1: 优化浏览器窗口")
        print("-" * 30)
        bypass.driver.maximize_window()
        bypass.driver.set_window_size(1920, 1080)
        print("✅ 浏览器窗口已最大化")
        
        # 访问Google Scholar
        print("\n步骤2: 访问Google Scholar")
        print("-" * 30)
        bypass.driver.get("https://scholar.google.com")
        time.sleep(3)
        
        print(f"当前URL: {bypass.driver.current_url}")
        print(f"页面标题: {bypass.driver.title}")
        
        # 检查是否遇到人机验证
        page_source = bypass.driver.page_source.lower()
        title = bypass.driver.title.lower()
        
        captcha_indicators = [
            "请稍候", "captcha", "verify", "robot", "challenge",
            "security check", "unusual traffic", "suspicious activity",
            "not a robot", "unusual traffic", "suspicious activity"
        ]
        
        is_captcha = any(indicator in title or indicator in page_source for indicator in captcha_indicators)
        
        if is_captcha:
            print("\n🔐 检测到人机验证")
            print("=" * 50)
            print("请按照以下步骤完成验证：")
            print()
            print("1. 确保浏览器窗口完全可见")
            print("2. 如果验证页面显示不完整：")
            print("   - 点击浏览器右上角的最大化按钮")
            print("   - 或者按 F11 进入全屏模式")
            print("   - 或者按 F5 刷新页面")
            print()
            print("3. 完成人机验证：")
            print("   - 点击 'I'm not a robot' 复选框")
            print("   - 如果出现图片选择，选择所有包含指定对象的图片")
            print("   - 如果出现文字验证，输入显示的字符")
            print()
            print("4. 等待验证完成，页面应该跳转到Google Scholar搜索界面")
            print("5. 验证完成后，按回车键继续...")
            print()
            
            # 等待用户完成验证
            input("完成验证后按回车键继续...")
            
            # 重新检查页面状态
            print("\n重新检查页面状态...")
            time.sleep(2)
            bypass.driver.refresh()
            time.sleep(3)
            
            print(f"当前URL: {bypass.driver.current_url}")
            print(f"页面标题: {bypass.driver.title}")
            
            # 再次检查是否还在验证页面
            current_page_source = bypass.driver.page_source.lower()
            current_title = bypass.driver.title.lower()
            still_captcha = any(indicator in current_title or indicator in current_page_source for indicator in captcha_indicators)
            
            if still_captcha:
                print("⚠️ 仍在验证页面")
                print("请确保：")
                print("1. 验证已完全完成")
                print("2. 页面已跳转到Google Scholar")
                print("3. 网络连接正常")
                print()
                input("如果确认验证已完成，按回车键继续...")
            else:
                print("✅ 验证成功！页面已跳转到Google Scholar")
        else:
            print("✅ 未检测到人机验证，可以直接使用Google Scholar")
        
        # 测试搜索功能
        print("\n步骤3: 测试搜索功能")
        print("-" * 30)
        test_query = "single crystal growth 2024"
        print(f"测试搜索: {test_query}")
        
        try:
            results = bypass.search_google_scholar(test_query, max_results=3)
            if results:
                print(f"✅ 搜索成功！找到 {len(results)} 个结果")
                for i, result in enumerate(results[:2], 1):
                    print(f"  {i}. {result.title}")
                    print(f"     期刊: {result.journal}")
                    print(f"     URL: {result.url}")
                    print()
            else:
                print("❌ 搜索失败，可能仍有验证问题")
        except Exception as e:
            print(f"❌ 搜索测试失败: {e}")
        
        print("\n步骤4: 完成")
        print("-" * 30)
        print("人机验证处理完成！")
        print("现在可以正常使用Google Scholar搜索功能")
        
    except Exception as e:
        print(f"❌ 处理过程中出现错误: {e}")
        print("建议：")
        print("1. 检查网络连接")
        print("2. 重新运行此脚本")
        print("3. 使用VPN更换IP地址")
    
    finally:
        print("\n按回车键关闭浏览器...")
        input()
        bypass.close()

if __name__ == "__main__":
    handle_google_scholar_captcha()
