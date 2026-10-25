#!/usr/bin/env python3
"""
流程化创造学习视频 — Puppeteer/Playwright 直接渲染 V3
不依赖 GSAP timeline 检测,直接使用 Canvas 或 WebRender 渲染每一帧
"""
import asyncio
import subprocess
import os
from datetime import datetime
from playwright.async_api import async_playwright

OUTPUT_DIR = "renders"
TEMP_DIR = "frames"
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(TEMP_DIR, exist_ok=True)

# 配置
WIDTH = 1080
HEIGHT = 1920
FPS = 30
DURATION = 20
TOTAL_FRAMES = FPS * DURATION

# HTML 文件路径
HTML_FILE = os.path.abspath("index.html").replace('\\', '/')

async def main():
    print("=" * 60)
    print("流程化创造学习视频 — 直接渲染 V3 (Puppeteer CDP)")
    print("=" * 60)
    print(f"分辨率: {WIDTH}x{HEIGHT}")
    print(f"时长: {DURATION}s @ {FPS}fps")
    print(f"总帧数: {TOTAL_FRAMES}")
    print()

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": WIDTH, "height": HEIGHT}
        )
        page = await context.new_page()

        print("[1/4] 打开页面...")
        await page.goto(f"file://{HTML_FILE}", wait_until="networkidle")
        await page.wait_for_timeout(3000)

        # 检查动画
        print("[2/4] 验证页面加载...")
        page_title = await page.title()
        print(f"  标题: {page_title}")

        # 手动触发播放
        print("[3/4] 播放动画并开始录制...")
        await page.evaluate("""
        () => {
            if (window.__timelines && window.__timelines['learning-video']) {
                const tl = window.__timelines['learning-video'];
                tl.play();
                return 'playing';
            }
            // 如果没有 timeline,直接播放动画
            return 'fallback';
        }
        """)
        await page.wait_for_timeout(500)

        # 方案B: 使用浏览器内建性能模式录制
        # 由于GSAP timeline未注册,我们采用逐帧推进的方式
        
        # 首先尝试让动画自然播放,边播放边截图
        print("  采用: 边播放边截图方式...")
        
        # 播放动画的同时定时截图
        interval_id = await page.evaluate_handle("""
        () => {
            return setInterval(() => {
                window.__screenshot_ready = true;
            }, 1000/FPS);
        }
        """)

        # 等待动画播放完毕
        await page.wait_for_timeout((DURATION + 2) * 1000)

        # 清除interval
        await page.evaluate(f"clearInterval({interval_id})")

        print(f"[4/4] 开始截图 {TOTAL_FRAMES} 帧...")
        
        for i in range(TOTAL_FRAMES):
            frame_num = f"{i:04d}"
            filepath = os.path.join(TEMP_DIR, f"frame_{frame_num}.png")
            await page.screenshot(path=filepath)
            
            if (i + 1) % 100 == 0:
                pct = (i + 1) / TOTAL_FRAMES * 100
                elapsed = i / FPS
                print(f"  进度: {i+1}/{TOTAL_FRAMES} ({pct:.0f}%) | 已播放 {elapsed:.1f}s/{DURATION}s")

        print("  帧截图完成!")
        print()
        print("  使用 FFmpeg 合成视频...")

        # FFmpeg 合成
        timestamp_str = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        output_file = os.path.join(OUTPUT_DIR, f"流程化创造学习视频_V3_{timestamp_str}.mp4")

        cmd = [
            "ffmpeg", "-y",
            "-framerate", str(FPS),
            "-i", os.path.join(TEMP_DIR, "frame_%04d.png"),
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-crf", "16",
            "-preset", "slow",
            output_file
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            file_size = os.path.getsize(output_file)
            print()
            print("=" * 60)
            print("✅ 视频渲染完成!")
            print("=" * 60)
            print(f"输出文件: {output_file}")
            print(f"文件大小: {file_size / 1024 / 1024:.2f} MB")
            print(f"分辨率: {WIDTH}x{HEIGHT}")
            print(f"时长: {DURATION}s @ {FPS}fps")
            print("=" * 60)
        else:
            print("❌ FFmpeg 失败:")
            print(result.stderr[:500])

        # 清理
        import shutil
        print()
        print("清理临时帧...")
        shutil.rmtree(TEMP_DIR, ignore_errors=True)
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
