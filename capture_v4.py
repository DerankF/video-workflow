#!/usr/bin/env python3
"""
流程化创造学习视频 — Playwright 截图渲染 V4
使用纯 CSS 动画版本,无需 GSAP,直接播放录制
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

WIDTH = 1080
HEIGHT = 1920
FPS = 30
DURATION = 22  # 留2秒缓冲
TOTAL_FRAMES = FPS * DURATION

HTML_FILE = os.path.abspath("index_v2.html").replace('\\', '/')

async def main():
    print("=" * 60)
    print("流程化创造学习视频 — CSS动画版渲染 V4")
    print("=" * 60)
    print(f"分辨率: {WIDTH}x{HEIGHT}")
    print(f"时长: {DURATION}s | 帧数: {TOTAL_FRAMES}")
    print()

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": WIDTH, "height": HEIGHT})
        page = await context.new_page()

        print("[1/4] 打开CSS动画页面...")
        await page.goto(f"file://{HTML_FILE}", wait_until="domcontentloaded")
        await page.wait_for_timeout(3000)  # 等页面完全加载

        print("[2/4] 验证动画播放...")
        title = await page.title()
        print(f"  标题: {title}")

        # 截图前确认页面可见
        await page.wait_for_timeout(1000)

        print(f"[3/4] 捕获 {TOTAL_FRAMES} 帧...")

        for i in range(TOTAL_FRAMES):
            frame_num = f"{i:04d}"
            filepath = os.path.join(TEMP_DIR, f"frame_{frame_num}.png")
            await page.screenshot(path=filepath)

            if (i + 1) % 150 == 0:
                elapsed = i / FPS
                print(f"  进度: {i+1}/{TOTAL_FRAMES} ({(i+1)/TOTAL_FRAMES*100:.0f}%) | 已播放 {elapsed:.0f}s")

        print("  ✓ 全部帧截图完成")
        print()
        print("[4/4] FFmpeg 合成视频...")

        timestamp_str = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        output_file = os.path.join(OUTPUT_DIR, f"流程化创造学习视频_CSS_V4_{timestamp_str}.mp4")

        cmd = [
            "ffmpeg", "-y",
            "-framerate", str(FPS),
            "-i", os.path.join(TEMP_DIR, "frame_%04d.png"),
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-crf", "14",
            "-preset", "medium",
            "-profile:v", "high",
            "-level", "4.0",
            "-movflags", "+faststart",
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
            print(f"分辨率: {WIDTH}x{HEIGHT} (竖版)")
            print(f"时长: {DURATION}s @ {FPS}fps")
            print("=" * 60)
        else:
            print("❌ FFmpeg 渲染失败:")
            print(result.stderr[:500])

        # 清理
        import shutil
        print()
        print("清理临时帧文件...")
        shutil.rmtree(TEMP_DIR, ignore_errors=True)

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
