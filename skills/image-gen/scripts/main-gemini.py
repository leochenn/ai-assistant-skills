import time
import os
import subprocess
import sys
import socket
import base64
from playwright.sync_api import sync_playwright

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_ROOT = os.path.dirname(SCRIPT_DIR)
try:
    CHROME_DEBUG_PORT = int(os.environ.get("SKILLS_CHROME_PORT", "9222"))
except ValueError:
    CHROME_DEBUG_PORT = 9222
USER_DATA_DIR = os.environ.get("SKILLS_CHROME_DATA") or os.path.join(SKILL_ROOT, "../env/playwright_chrome_data")

def is_port_open(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def get_chrome_path():
    paths = [
        r"C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
        r"C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\\Google\\Chrome\\Application\\chrome.exe")
    ]
    for p in paths:
        if os.path.exists(p): return p
    return "chrome"

def ensure_browser():
    if is_port_open(CHROME_DEBUG_PORT): return True
    chrome_path = get_chrome_path()
    if not os.path.exists(USER_DATA_DIR): os.makedirs(USER_DATA_DIR)
    cmd = [chrome_path, f"--remote-debugging-port={CHROME_DEBUG_PORT}", f"--user-data-dir={USER_DATA_DIR}", "--no-first-run"]
    subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for _ in range(10):
        if is_port_open(CHROME_DEBUG_PORT): return True
        time.sleep(1)
    return False

def run_gemini_task(prompt, output_file):
    if not ensure_browser():
        print("❌ 无法连接浏览器")
        return

    print(f"🚀 启动任务: {prompt}")
    with sync_playwright() as p:
        try:
            browser = p.chromium.connect_over_cdp(f"http://localhost:{CHROME_DEBUG_PORT}")
            context = browser.contexts[0]
            
            # 1. Open new tab
            page = context.new_page()
            
            url = "https://business.gemini.google/home/cid/eae54c8a-9921-4d9d-9353-115315265a1a?csesidx=789314859&mods"
            print(f"🌐 正在访问: {url}")
            page.goto(url, timeout=60000)
            
            # Wait for basic load
            time.sleep(5)

            # 2. Find input box (Generic attempt to ensure page is interactive)
            print("🔍 寻找输入区域...")
            # Try to find the rich text editor often used in these apps
            input_locator = page.locator('div[contenteditable="true"], textarea, input[type="text"]').first
            if input_locator.count() > 0:
                print("✅ 找到输入框")
                input_locator.click()
            else:
                print("⚠️ 未明确找到输入框，继续尝试...")

            # 3. Find 'Select tools' button
            print("🔍 寻找 'Select tools' 按钮...")
            # Exact match from user instruction
            tools_btn = page.locator('button[aria-label="Select tools"]')
            if tools_btn.count() == 0:
                print("❌ 未找到 'Select tools' 按钮")
                # Debug: Print all buttons
                # btns = page.locator("button").all_inner_texts()
                # print(f"Available buttons: {btns}")
                return
            
            # 4. Click it
            tools_btn.click()
            print("✅ 点击工具按钮")
            time.sleep(2) # Wait for menu

            # 5 & 6. Click '生成图片 (Pro)'
            print("🔍 寻找 '生成图片 (Pro)' 菜单...")
            # Try exact text or partial
            menu_item = page.locator("text=生成图片 (Pro)")
            if not menu_item.count():
                 menu_item = page.locator("text=生成图片")
            
            if menu_item.count():
                menu_item.click()
                print("✅ 选择 '生成图片 (Pro)'")
            else:
                print("❌ 未找到 '生成图片' 菜单项")
                return

            time.sleep(2)

            # 7. Input prompt
            print(f"✍️ 输入指令: {prompt}")
            # Ensure focus is back on input (clicking menu might have shifted it, but usually selecting a tool puts focus back or inserts a chip)
            # We assume we just need to type now.
            page.keyboard.type(prompt, delay=50)

            # 8. Find Submit button
            print("🔍 寻找提交按钮...")
            submit_btn = page.locator('button[aria-label="提交"]')
            if not submit_btn.count():
                 print("⚠️ 未找到 aria-label='提交' 按钮，尝试图标按钮...")
                 # Often the submit button is an icon button at the bottom right of input
                 submit_btn = page.locator('button.icon-button').last
            
            # 9. Click Submit
            if submit_btn.count():
                submit_btn.click()
                print("✅ 点击提交")
            else:
                print("❌ 无法点击提交")
                return

            # 10. Wait and Poll
            print("👀 等待生成中 (160s)...")
            target_src = None
            
            for i in range(80):
                time.sleep(2)
                print(f"[{i+1}/80] Probing...", end="\r")
                
                # Iterate over all frames (main frame + iframes)
                # Use locator to pierce Shadow DOM within each frame
                for f_idx, frame in enumerate(page.frames):
                    try:
                        # Find all images in this frame (pierces Shadow DOM)
                        imgs = frame.locator("img").all()
                        if len(imgs) > 0 and i % 5 == 0:
                            print(f"\nFrame {f_idx}: Found {len(imgs)} images")
                            
                        for img_loc in imgs:
                            try:
                                if img_loc.is_visible():
                                    box = img_loc.bounding_box()
                                    if box and box['width'] > 200 and box['height'] > 200:
                                        src = img_loc.get_attribute("src")
                                        if src:
                                            print(f"\n🎯 候选发现 (Frame {f_idx}): {box['width']}x{box['height']} | {src[:50]}...")
                                            target_src = src
                                            # We found a good candidate.
                                            # In a real run, we might want to wait for the *newest* one or ensure it's the right one.
                                            # But for now, if we find a large image, it's likely the result.
                            except:
                                pass
                    except Exception as e:
                        pass
                
                if target_src:
                     # Double check if we want to stop immediately
                     if i > 2:
                         print(f"\n✅ 最终确认图片: {target_src[:60]}...")
                         break
            
            if target_src:
                # 13. Download
                print(f"\n⬇️ 正在下载...")
                try:
                    if target_src.startswith("blob:"):
                        # Handle blob URL download via browser context
                        data_url = page.evaluate("""async (url) => {
                            const response = await fetch(url);
                            const blob = await response.blob();
                            return new Promise((resolve, reject) => {
                                const reader = new FileReader();
                                reader.onloadend = () => resolve(reader.result);
                                reader.onerror = reject;
                                reader.readAsDataURL(blob);
                            });
                        }""", target_src)
                        
                        # data_url format: data:image/png;base64,......
                        header, encoded = data_url.split(",", 1)
                        data = base64.b64decode(encoded)
                        
                        with open(output_file, "wb") as f:
                            f.write(data)
                        print(f"✅ 任务完成！图片保存为: {output_file}")
                        
                    else:
                        # Standard HTTP URL
                        resp = page.request.get(target_src)
                        if resp.status == 200:
                            with open(output_file, "wb") as f:
                                f.write(resp.body())
                            print(f"✅ 任务完成！图片保存为: {output_file}")
                        else:
                            print(f"❌ 下载响应错误: {resp.status}")
                except Exception as e:
                    print(f"❌ 下载异常: {e}")
            else:
                print("\n❌ 未能提取到图片 (超时或未找到)")

            # 14. Do not close window
            print("👋 脚本结束 (窗口保持打开)")

        except Exception as e:
            print(f"\n❌ 运行错误: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    # Allow arguments or defaults
    prompt = sys.argv[1] if len(sys.argv) > 1 else "{生图内容：长沙夜景图}"
    # Cleanup prompt braces if present
    prompt = prompt.replace("{", "").replace("}", "").replace("生图内容：", "")
    
    filename = sys.argv[2] if len(sys.argv) > 2 else "gemini_gen_result.png"
    
    run_gemini_task(prompt, filename)
