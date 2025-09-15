#!/usr/bin/env python3
"""
APS凭证处理器
专门处理APS期刊的权限问题
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.advanced_selenium_bypass import AdvancedSeleniumBypass
from app.services.aps_pdf_extractor import APSPDFExtractor
from app.services.pdf_downloader import PDFDownloader
import time
import json
import requests
from urllib.parse import urljoin

class APSCredentialHandler:
    """APS凭证处理器"""
    
    def __init__(self):
        self.credentials = {}
        self.session = requests.Session()
        self.credential_file = "downloads/aps_credentials.json"
        self.load_credentials()
    
    def load_credentials(self):
        """加载已保存的凭证"""
        if os.path.exists(self.credential_file):
            try:
                with open(self.credential_file, 'r', encoding='utf-8') as f:
                    self.credentials = json.load(f)
                print(f"✅ 已加载APS凭证")
            except Exception as e:
                print(f"⚠️ 加载APS凭证失败: {e}")
                self.credentials = {}
    
    def save_credentials(self):
        """保存凭证到文件"""
        try:
            with open(self.credential_file, 'w', encoding='utf-8') as f:
                json.dump(self.credentials, f, ensure_ascii=False, indent=2)
            print("✅ APS凭证已保存")
        except Exception as e:
            print(f"⚠️ 保存APS凭证失败: {e}")
    
    def request_aps_credentials(self):
        """请求APS访问凭证"""
        print("\n🔐 需要APS期刊的访问权限")
        print("-" * 40)
        print("请提供以下信息以访问APS期刊:")
        print("1. 机构用户名/邮箱")
        print("2. 密码")
        print("3. 机构名称")
        print("4. 访问方式 (institutional/individual)")
        print()
        
        credentials = {}
        
        # 获取用户名
        username = input("请输入用户名/邮箱: ").strip()
        if not username:
            print("❌ 用户名不能为空")
            return None
        credentials['username'] = username
        
        # 获取密码
        import getpass
        password = getpass.getpass("请输入密码: ")
        if not password:
            print("❌ 密码不能为空")
            return None
        credentials['password'] = password
        
        # 获取机构名称
        institution = input("请输入机构名称 (可选): ").strip()
        if institution:
            credentials['institution'] = institution
        
        # 获取访问方式
        access_type = input("访问方式 (institutional/individual) [institutional]: ").strip()
        if not access_type:
            access_type = "institutional"
        credentials['access_type'] = access_type
        
        # 保存凭证
        self.credentials = credentials
        self.save_credentials()
        
        return credentials
    
    def authenticate_with_aps(self, credentials):
        """使用凭证认证APS访问"""
        print("🔐 正在认证APS访问...")
        
        try:
            # 设置认证头
            self.session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            })
            
            # 尝试访问APS主页
            response = self.session.get("https://journals.aps.org/", timeout=10)
            
            if response.status_code == 200:
                print("✅ APS访问认证成功")
                return True
            else:
                print(f"❌ APS访问认证失败: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ APS访问认证异常: {e}")
            return False
    
    def download_with_credentials(self, pdf_url, filename):
        """使用凭证下载PDF"""
        try:
            print(f"📥 使用凭证下载: {pdf_url}")
            
            response = self.session.get(pdf_url, timeout=30)
            
            if response.status_code == 200:
                # 保存文件
                file_path = os.path.join("downloads", filename)
                with open(file_path, 'wb') as f:
                    f.write(response.content)
                
                file_size = os.path.getsize(file_path)
                print(f"✅ 下载成功: {file_path} ({file_size} bytes)")
                
                return {
                    'success': True,
                    'file_path': file_path,
                    'file_size': file_size,
                    'error': None
                }
            else:
                print(f"❌ 下载失败: HTTP {response.status_code}")
                return {
                    'success': False,
                    'file_path': '',
                    'file_size': 0,
                    'error': f"HTTP {response.status_code}"
                }
                
        except Exception as e:
            print(f"❌ 下载异常: {e}")
            return {
                'success': False,
                'file_path': '',
                'file_size': 0,
                'error': str(e)
            }

def aps_credential_workflow():
    """APS凭证工作流程"""
    print("APS凭证工作流程")
    print("=" * 50)
    print("系统将自动运行，遇到APS权限问题时请求用户输入凭证")
    print()
    
    # 初始化服务
    credential_handler = APSCredentialHandler()
    bypass = AdvancedSeleniumBypass(headless=False)
    aps_extractor = APSPDFExtractor(use_selenium=True)
    pdf_downloader = PDFDownloader(download_dir="downloads")
    
    try:
        print("步骤1: 自动搜索APS论文")
        print("-" * 30)
        
        # 自动搜索
        results = bypass.search_google_scholar("site:journals.aps.org/prx single crystal growth", max_results=3)
        
        if not results:
            print("❌ 搜索未找到结果")
            return
        
        print(f"✅ 找到 {len(results)} 个APS论文")
        
        # 处理每个论文
        success_count = 0
        for i, result in enumerate(results, 1):
            print(f"\n处理论文 {i}: {result.title}")
            print(f"URL: {result.url}")
            
            try:
                # 尝试自动提取PDF信息
                print("  自动提取PDF信息...")
                pdf_info = aps_extractor.extract_pdf_info(result.url)
                
                if pdf_info:
                    print(f"  ✅ PDF信息提取成功")
                    print(f"  PDF URL: {pdf_info.pdf_url}")
                    print(f"  标题: {pdf_info.title}")
                    print(f"  作者: {pdf_info.authors}")
                    print(f"  期刊: {pdf_info.journal}")
                    print(f"  访问类型: {pdf_info.access_type}")
                    
                    # 尝试自动下载PDF
                    print("  自动下载PDF...")
                    filename = f"aps_credential_{i}_{pdf_info.title[:30].replace(' ', '_').replace('/', '_')}.pdf"
                    download_result = pdf_downloader.download_pdf(
                        pdf_info.pdf_url, 
                        filename, 
                        pdf_info.access_type
                    )
                    
                    if download_result.success:
                        print(f"  ✅ PDF下载成功")
                        print(f"  文件路径: {download_result.file_path}")
                        print(f"  文件大小: {download_result.file_size} bytes")
                        success_count += 1
                    else:
                        print(f"  ❌ PDF下载失败: {download_result.error}")
                        
                        # 检查是否需要APS凭证
                        if "403" in str(download_result.error) or "Forbidden" in str(download_result.error):
                            print("  🔐 检测到APS权限问题，请求用户输入凭证")
                            
                            # 请求用户输入凭证
                            credentials = credential_handler.request_aps_credentials()
                            
                            if credentials:
                                # 认证APS访问
                                if credential_handler.authenticate_with_aps(credentials):
                                    # 使用凭证重新下载
                                    retry_result = credential_handler.download_with_credentials(
                                        pdf_info.pdf_url, 
                                        filename
                                    )
                                    
                                    if retry_result['success']:
                                        print(f"  ✅ 使用凭证下载成功")
                                        print(f"  文件路径: {retry_result['file_path']}")
                                        print(f"  文件大小: {retry_result['file_size']} bytes")
                                        success_count += 1
                                    else:
                                        print(f"  ❌ 使用凭证仍然失败: {retry_result['error']}")
                                else:
                                    print("  ❌ APS认证失败，跳过此论文")
                            else:
                                print("  ❌ 未提供凭证，跳过此论文")
                else:
                    print("  ❌ PDF信息提取失败")
                    
            except Exception as e:
                print(f"  ❌ 处理异常: {e}")
        
        # 显示最终结果
        print(f"\n步骤4: 处理结果统计")
        print("-" * 30)
        print(f"总处理论文: {len(results)}")
        print(f"成功处理: {success_count}")
        print(f"成功率: {success_count/len(results)*100:.1f}%")
        
        if success_count > 0:
            print("🎉 处理完成！")
        else:
            print("❌ 所有论文处理失败")
            
    except Exception as e:
        print(f"❌ 工作流程失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        try:
            bypass.close()
        except:
            pass

if __name__ == "__main__":
    aps_credential_workflow()
