"""前端调试脚本"""

import time
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()

    # 捕获所有网络请求
    def log_request(request):
        print(f"REQ: {request.method} {request.url}")

    def log_response(response):
        try:
            status = response.status
            if status >= 400:
                print(f"RES: {status} {response.url}")
        except:
            pass

    page.on("request", log_request)
    page.on("response", log_response)

    # 捕获console
    page.on("console", lambda msg: print(f"CON: [{msg.type}] {msg.text}"))
    page.on("pageerror", lambda exc: print(f"ERR: {exc}"))

    print("=== 1. 访问前端 ===")
    page.goto("http://localhost:8889")
    page.wait_for_load_state("networkidle")
    time.sleep(2)

    print("\n=== 2. 登录 ===")
    page.fill('input[type="text"]', "admin")
    page.fill('input[type="password"]', "123456")
    page.click('button:has-text("登")')
    time.sleep(3)

    print("\n=== 3. 导航到AI助手 ===")
    page.click("text=AI助手")
    page.wait_for_load_state("networkidle")
    time.sleep(2)

    print("\n=== 4. 发送消息 ===")
    try:
        page.fill("textarea", "你好")
        page.click('button:has-text("发送")')
        time.sleep(8)
    except Exception as e:
        print(f"发送失败: {e}")

    print("\n=== 完成 ===")
    input("按回车键关闭浏览器...")
    browser.close()
