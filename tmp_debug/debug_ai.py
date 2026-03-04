"""
调试前端AI对话功能
"""
from playwright.sync_api import sync_playwright
import time

def main():
    with sync_playwright() as p:
        # 启动无头浏览器
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        # 开启控制台日志
        page.on("console", lambda msg: print(f"[Browser Console] {msg.type}: {msg.text}"))
        page.on("pageerror", lambda err: print(f"[Page Error] {err}"))
        
        try:
            # 访问前端登录页
            print("正在打开前端页面...")
            page.goto('http://localhost:8888', wait_until='networkidle', timeout=30000)
            time.sleep(2)
            
            # 截取登录页面
            page.screenshot(path='c:/Users/hanbin/main/Core/DevHome/m2.5/TestPlatform/debug_login.png', full_page=True)
            print("登录页截图已保存")
            
            # 查看页面内容
            content = page.content()
            print(f"页面标题: {page.title()}")
            
            # 查找登录表单元素
            username_input = page.locator('input[type="text"], input[placeholder*="账"], input[placeholder*="用户"]').first
            password_input = page.locator('input[type="password"]').first
            login_button = page.locator('button:has-text("登录"), button:has-text("登录"), .el-button--primary').first
            
            print(f"找到用户名输入框: {username_input.count() > 0}")
            print(f"找到密码输入框: {password_input.count() > 0}")
            print(f"找到登录按钮: {login_button.count() > 0}")
            
            if username_input.count() > 0 and password_input.count() > 0:
                # 输入登录信息
                username_input.fill("admin")
                password_input.fill("123456")
                time.sleep(1)
                
                # 点击登录
                login_button.click()
                time.sleep(3)
                
                # 截取登录后页面
                page.screenshot(path='c:/Users/hanbin/main/Core/DevHome/m2.5/TestPlatform/debug_after_login.png', full_page=True)
                print("登录后截图已保存")
                
                # 尝试导航到AI助手页面
                # 查找AI助手相关链接
                ai_links = page.locator('a:has-text("AI"), a:has-text("智能"), a:has-text("助手")')
                print(f"找到AI相关链接: {ai_links.count()}")
                
                # 尝试直接访问AI页面
                page.goto('http://localhost:8888/#/aiAssistant', wait_until='networkidle', timeout=30000)
                time.sleep(2)
                
                page.screenshot(path='c:/Users/hanbin/main/Core/DevHome/m2.5/TestPlatform/debug_ai_page.png', full_page=True)
                print("AI页面截图已保存")
                
                # 查找发送消息的输入框
                textarea = page.locator('textarea, input[placeholder*="问题"], input[placeholder*="消息"]')
                print(f"找到输入框: {textarea.count()}")
                
                if textarea.count() > 0:
                    textarea.first.fill("你好，测试一下AI对话")
                    time.sleep(1)
                    
                    # 查找发送按钮
                    send_btn = page.locator('button:has-text("发送"), button[type="submit"]')
                    if send_btn.count() > 0:
                        send_btn.first.click()
                        time.sleep(5)
                        
                        page.screenshot(path='c:/Users/hanbin/main/Core/DevHome/m2.5/TestPlatform/debug_after_send.png', full_page=True)
                        print("发送消息后截图已保存")
            
        except Exception as e:
            print(f"错误: {e}")
            page.screenshot(path='c:/Users/hanbin/main/Core/DevHome/m2.5/TestPlatform/debug_error.png', full_page=True)
        
        browser.close()

if __name__ == "__main__":
    main()
