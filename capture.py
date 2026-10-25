#!/usr/bin/env python3
"""
流程化创造学习视频 — Playwright 帧捕获 + FFmpeg 渲染
"""
import asyncio
import subprocess
import os
import glob
from playwright.async_api import async_playwright

OUTPUT_DIR = "renders"
TEMP_DIR = "frames"
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(TEMP_DIR, exist_ok=True)

# 配置参数
WIDTH = 1080
HEIGHT = 1920  # 竖版
FPS = 30
DURATION = 20  # 秒
TOTAL_FRAMES = FPS * DURATION  # 600 frames
START_URL = "http://localhost:18899/index.html"

async def main():
    print("=" * 60)
    print("流程化创造学习视频 — Playwright 帧捕获")
    print("=" * 60)
    print(f"分辨率: {WIDTH}x{HEIGHT} (竖版)")
    print(f"帧率: {FPS} FPS")
    print(f"时长: {DURATION}s")
    print(f"总帧数: {TOTAL_FRAMES}")
    print()

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": WIDTH, "height": HEIGHT})
        page = await context.new_page()

        print("[1/3] 打开页面...")
        await page.goto(START_URL, wait_until="load")

        # 等待 GSAP 动画初始化
        await page.wait_for_timeout(2000)

        print(f"[2/3] 开始捕获 {TOTAL_FRAMES} 帧...")

        # 在指定时间点截图
        for i in range(TOTAL_FRAMES):
            timestamp = (i / FPS)
            await page.wait_for_timeout(33)  # ~30fps

            frame_num = f"{i:04d}"
            filepath = os.path.join(TEMP_DIR, f"frame_{frame_num}.png")

            # 截图
            await page.screenshot(path=filepath, full_page=False)

            if (i + 1) % 100 == 0:
                print(f"  进度: {i+1}/{TOTAL_FRAMES} ({(i+1)/TOTAL_FRAMES*100:.0f}%)")

        print(f"[3/3] 用 FFmpeg 合成视频...")

        # 使用 FFmpeg 将帧序列合成为视频
        output_file = os.path.join(OUTPUT_DIR, f"流程化创造学习视频_{os.popen('date +%Y-%m-%d_%H-%M-%S').read().strip()}.mp4")

        cmd = [
            "ffmpeg",
            "-y",
            "-r", str(FPS),
            "-i", os.path.join(TEMP_DIR, "frame_%04d.png"),
            "-vf", f"scale={WIDTH}:{HEIGHT}:flags=lanczos",
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-crf", "18",
            "-preset", "medium",
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
            print("❌ FFmpeg 渲染失败:")
            print(result.stderr)

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
