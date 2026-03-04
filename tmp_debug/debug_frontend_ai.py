"""调试前端AI聊天问题"""
import requests
import time
from playwright.sync_api import sync_playwright

def test_ai_chat():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        
        console_messages = []
        page.on("console", lambda msg: console_messages.append(f"[{msg.type}] {msg.text}"))
        
        page.on("pageerror", lambda exc: console_messages.append(f"[ERROR] {exc}"))
        
        print("=== 1. 访问前端 ===")
        page.goto("http://localhost:8889")
        page.wait_for_load_state("networkidle")
        time.sleep(2)
        
        print("=== 2. 登录 ===")
        page.fill('input[type="text"]', "admin")
        page.fill('input[type="password"]', "123456")
        page.click('button[type="button"]')
        time.sleep(3)
        
        print("=== 3. 导航到AI助手 ===")
        page.click('text=AI助手')
        page.wait_for_load_state("networkidle")
        time.sleep(2)
        
        print("=== 4. 发送消息 ===")
        textarea = page.locator('textarea')
        if textarea.count() > 0:
            textarea.fill("你好")
            page.click('text=发送')
            time.sleep(5)
        
        print("\n=== Console输出 ===")
        for msg in console_messages:
            print(msg)
        
        browser.close()

if __name__ == "__main__":
    test_ai_chat()
