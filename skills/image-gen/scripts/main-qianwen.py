import os
import sys
import time
import argparse
import subprocess
import socket
import base64
from playwright.sync_api import sync_playwright

# --- Configuration ---
try:
    CHROME_DEBUG_PORT = int(os.environ.get("SKILLS_CHROME_PORT", "9222"))
except ValueError:
    CHROME_DEBUG_PORT = 9222
# 计算项目根目录
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_ROOT = os.path.dirname(SCRIPT_DIR)
USER_DATA_DIR = os.environ.get("SKILLS_CHROME_DATA") or os.path.join(SKILL_ROOT, "../env/playwright_chrome_data")
TARGET_URL = "https://www.qianwen.com/?ch=webtongyi@sem_bdsempinzhuan&st=null&bizPassParams=ch%3Dwebtongyi%40sem_bdsempinzhuan%26x-platform%3DexternalH5"

def is_port_open(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def get_chrome_path():
    paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe")
    ]
    for p in paths:
        if os.path.exists(p): return p
    return "chrome"

def ensure_browser():
    """确保 Chrome 以调试模式运行"""
    if is_port_open(CHROME_DEBUG_PORT):
        # print(f"✅ Chrome 调试端口 {CHROME_DEBUG_PORT} 已开启")
        return True
    
    print("🚀 正在启动 Chrome (调试模式)...")
    chrome_path = get_chrome_path()
    if not os.path.exists(USER_DATA_DIR):
        os.makedirs(USER_DATA_DIR)
        
    cmd = [
        chrome_path, 
        f"--remote-debugging-port={CHROME_DEBUG_PORT}", 
        f"--user-data-dir={USER_DATA_DIR}", 
        "--no-first-run"
    ]
    subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    for i in range(10):
        if is_port_open(CHROME_DEBUG_PORT):
            print("✅ Chrome 启动成功")
            return True
        time.sleep(1)
    return False

def save_image(page, img_locator, output_path):
    """提取并保存图片"""
    try:
        src = img_locator.get_attribute("src")
        if not src: return False
        
        # 排除头像和小图标
        box = img_locator.bounding_box()
        if not box or box['width'] < 200 or box['height'] < 200:
            return False

        print(f"📷 正在下载图片 (尺寸: {int(box['width'])}x{int(box['height'])})...")
        
        # 统一使用 page.evaluate + fetch 方案，因为这能处理 blob: 和带有鉴权的 URL
        # 并且将结果转为 base64 返回
        data_url = page.evaluate("""async (url) => {
            const response = await fetch(url);
            const blob = await response.blob();
            return new Promise((resolve, reject) => {
                const reader = new FileReader();
                reader.onloadend = () => resolve(reader.result);
                reader.onerror = reject;
                reader.readAsDataURL(blob);
            });
        }""", src)
        
        if not data_url: return False
        
        header, encoded = data_url.split(",", 1)
        data = base64.b64decode(encoded)
        
        abs_output_path = os.path.abspath(output_path)
        with open(abs_output_path, "wb") as f:
            f.write(data)
        return abs_output_path
        
    except Exception as e:
        # print(f"⚠️ 下载尝试失败: {e}")
        return False

def run_task(prompt, output_file):
    if not ensure_browser():
        print("❌ 无法启动浏览器")
        sys.exit(1)

    with sync_playwright() as p:
        try:
            print("🔗 连接浏览器...")
            browser = p.chromium.connect_over_cdp(f"http://localhost:{CHROME_DEBUG_PORT}")
            context = browser.contexts[0]
            if not context.pages:
                page = context.new_page()
            else:
                page = context.pages[0]

            # 1. 确保在千问页面
            if "qianwen.com" not in page.url:
                print("🌐 跳转至千问首页...")
                page.goto(TARGET_URL)
                time.sleep(3)

            # 2. 开启新对话
            print("✨ 正在开启新对话...")
            try:
                # 优先匹配 "新对话"
                new_chat_btn = page.locator("text=新对话").first
                if new_chat_btn.is_visible():
                    new_chat_btn.click()
                    time.sleep(2)
                else:
                    # 尝试寻找 "+" 号图标或其他可能的按钮
                    print("⚠️ 未找到 '新对话' 文本按钮，尝试继续...")
            except Exception as e:
                print(f"⚠️ 开启新对话遇到问题: {e}")

            # 3. 切换生图模式 (可选)
            # 用户要求切换到生图模式，尝试寻找相关入口
            # 常见入口： "万相", "图像生成", "文生图"
            modes = ["图像", "文生图", "Image Generation"]
            mode_switched = False
            for mode in modes:
                try:
                    # 使用正则全匹配，防止匹配到侧边栏历史记录 (如 "AI绘制猫图像")
                    # ^\s*...\s*$ 匹配整个文本内容，允许前后有空白
                    btn = page.locator(f"text=/^\\s*{mode}\\s*$/").first
                    if btn.is_visible():
                        print(f"🔄 切换模式: 点击 '{mode}'...")
                        btn.click()
                        time.sleep(1)
                        mode_switched = True
                        break
                except: pass
            
            if not mode_switched:
                print("ℹ️ 未找到显式的生图模式切换按钮，将直接发送提示词 (通常千问能自动识别)...")

            # 4. 输入提示词
            print(f"⌨️ 输入提示词: {prompt}")
            
            # 尝试多种定位方式
            textarea = None
            
            # 方式1: 具体的 Placeholder (针对生图模式)
            try:
                # 使用部分匹配，更稳健
                t = page.locator("textarea[placeholder*='图像生成']").first
                if t.is_visible(): textarea = t
            except: pass
            
            # 方式2: 原有的 Placeholder (针对普通对话模式)
            if not textarea:
                try:
                    t = page.locator("textarea[placeholder*='千问']").first
                    if t.is_visible(): textarea = t
                except: pass

            # 方式3: 任何可见的 textarea
            if not textarea:
                try:
                    textareas = page.locator("textarea").all()
                    for t in textareas:
                        if t.is_visible():
                            textarea = t
                            break
                except: pass
            
            if not textarea:
                # 备用：寻找 contenteditable
                textarea = page.locator("div[contenteditable='true']").first
            
            if not textarea or not textarea.is_visible():
                print("❌ 无法定位输入框")
                sys.exit(1)

            textarea.click()
            # 使用 type 模拟逐字输入，适配 Ant Design 组件
            textarea.type(prompt, delay=50)
            time.sleep(1)
            textarea.press("Enter")

            # 5. 等待并提取图片
            print("⏳ 等待图片生成 (超时 120秒)...")
            start_time = time.time()
            
            # 记录初始图片数量，以便对比 (可选，但直接找最后一张通常有效)
            
            while time.time() - start_time < 120:
                # 查找所有 img 标签
                images = page.locator("img").all()
                
                # 倒序遍历（优先检查最新的）
                for img in reversed(images):
                    saved_path = save_image(page, img, output_file)
                    if saved_path:
                        print(f"✅ 成功提取图片至: {saved_path}")
                        return

                time.sleep(2)
                print(f"   ...已等待 {int(time.time() - start_time)}秒", end="\r")
            
            print("\n❌ 超时：未检测到生成的新图片")
            sys.exit(1)

        except Exception as e:
            print(f"❌ 执行过程出错: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Qwen Image Generation Automation")
    parser.add_argument("prompt", help="Prompt for image generation")
    parser.add_argument("output", help="Output file path")
    args = parser.parse_args()
    
    run_task(args.prompt, args.output)
