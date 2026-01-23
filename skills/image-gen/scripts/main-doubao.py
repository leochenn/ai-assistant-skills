import time
import os
import subprocess
import sys
import socket
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

def run_doubao_task(prompt, output_file):
    if not ensure_browser():
        print("❌ 无法连接浏览器")
        return

    with sync_playwright() as p:
        try:
            browser = p.chromium.connect_over_cdp(f"http://localhost:{CHROME_DEBUG_PORT}")
            context = browser.contexts[0]
            page = context.pages[0] if context.pages else context.new_page()
            
            print(f"🌐 正在访问豆包...")
            page.goto("https://www.doubao.com/chat/create-image", timeout=60000)
            
            # 1. 记录初始状态：最新一条消息的 ID 或索引
            old_msg_count = page.evaluate("() => document.querySelectorAll('[class*=\"message\"]').length")
            
            print(f"✍️ 输入指令: {prompt}")
            page.click('div[data-slate-editor="true"]')
            page.keyboard.press("Control+A")
            page.keyboard.press("Backspace")
            page.keyboard.type(prompt, delay=50)
            page.keyboard.press("Enter")

            # 2. 轮询等待新消息出现并生成完成
            print("👀 等待生成中...")
            target_src = None
            start_time = time.time()
            
            while time.time() - start_time < 180:
                # 在浏览器内部执行复杂的判定逻辑
                res = page.evaluate(
                    """(oldMsgCount) => {
                        // 获取所有潜在的消息容器，但过滤掉操作栏和按钮
                        const allElements = Array.from(document.querySelectorAll('[class*="message"]'));
                        const messages = allElements.filter(el => {
                            const cls = el.className || "";
                            return !cls.includes("action-bar") && 
                                   !cls.includes("action-button") &&
                                   !cls.includes("hidden");
                        });

                        // 只需要关注发送指令后产生的新消息
                        // 注意：由于过滤了元素，oldMsgCount 可能不再准确对应索引，
                        // 但我们需要的是列表末尾的最新消息。
                        // 简单策略：直接取最后一条非用户消息（假设最后一条是 AI 回复）
                        
                        if (messages.length === 0) return { status: "waiting_for_msg" };

                        const lastMsg = messages[messages.length - 1];
                        const text = lastMsg.innerText;

                        // 判断是否还在“加载/生成”状态
                        const isGenerating = text.includes("正在生成") || 
                                           !!lastMsg.querySelector('[class*="loading"]') ||
                                           !!lastMsg.querySelector('svg[class*="spin"]') ||
                                           !!lastMsg.querySelector('[class*="skeleton"]');

                        if (isGenerating) return { status: "generating" };

                        // 寻找图片，必须是渲染成功的图片 (naturalWidth > 0)
                        const imgs = Array.from(lastMsg.querySelectorAll('img')).filter(img => {
                            // 排除头像、图标等小图，必须是 HTTP 链接（排除 data:image/svg 占位符）
                            return img.src.startsWith('http') && 
                                   (img.naturalWidth > 200 || img.width > 200) &&
                                   img.naturalWidth > 0;
                        });

                        if (imgs.length > 0) {
                            // 返回最后一张图（通常是结果图）
                            return { status: "done", src: imgs[imgs.length - 1].src };
                        }

                        return { status: "checking" };
                    }
                """, old_msg_count)
                
                if res['status'] == "done":
                    target_src = res['src']
                    print(f"\n🎯 捕获到生成的图片!")
                    break
                elif res['status'] == "generating":
                    # 显式处于生成状态，可以稍微多等会儿
                    pass
                
                time.sleep(3)
                print(".", end="", flush=True)

            if target_src:
                print(f"⬇️ 正在下载...")
                time.sleep(2) # 最后的稳定性缓冲
                response = page.request.get(target_src)
                if response.status == 200:
                    with open(output_file, "wb") as f:
                        f.write(response.body())
                    print(f"✅ 成功！保存为: {output_file}")
                else:
                    print(f"❌ 下载失败: {response.status}")
            else:
                print("\n❌ 提取失败：生成超时或未能在新消息中找到有效图片")

        except Exception as e:
            print(f"❌ 运行异常: {e}")

if __name__ == "__main__":
    p_text = sys.argv[1] if len(sys.argv) > 1 else "生图：长沙橘子洲动漫图片"
    o_file = sys.argv[2] if len(sys.argv) > 2 else "result.png"
    run_doubao_task(p_text, o_file)
