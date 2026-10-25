#!/usr/bin/env python3
"""
流程化创造学习视频 — 高质量最终渲染 V6
使用 index_final_v2.html (setInterval方案,兼容headless)
"""
import asyncio
import subprocess
import os
from datetime import datetime
from playwright.async_api import async_playwright

OUTPUT_DIR = "renders"
TEMP_DIR = "frames_q6"
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(TEMP_DIR, exist_ok=True)

WIDTH = 1080
HEIGHT = 1920
FPS = 30
DURATION = 24
TOTAL_FRAMES = FPS * DURATION
HTML_FILE = os.path.abspath("index_final_v2.html").replace('\\', '/')

async def main():
    print("=" * 60)
    print("流程化创造学习视频 — 最终重渲染 V6 (setInterval版)")
    print("=" * 60)
    print(f"分辨率: {WIDTH}x{HEIGHT} | 帧率: {FPS} | 时长: {DURATION}s")
    print()

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": WIDTH, "height": HEIGHT}
        )
        page = await context.new_page()

        print("[1/4] 加载页面...")
        await page.goto(f"file://{HTML_FILE}", wait_until="domcontentloaded")
        await page.wait_for_timeout(3000)  # 等动画启动

        print("[2/4] 验证页面已加载...")
        title = await page.title()
        print(f"  标题: {title}")

        # 强制刷新页面重新触发动画
        print("[3/4] 重新加载页面触发动画...")
        await page.reload(wait_until="domcontentloaded")
        await page.wait_for_timeout(5000)  # 给足时间让setInterval启动

        # 检查场景1是否已显示
        scene1_opacity = await page.evaluate("() => document.getElementById('s1').style.opacity")
        print(f"  场景1透明度: {scene1_opacity}")

        print(f"  开始捕获 {TOTAL_FRAMES} 帧...")
        for i in range(TOTAL_FRAMES):
            frame_num = f"{i:04d}"
            filepath = os.path.join(TEMP_DIR, f"frame_{frame_num}.png")
            await page.screenshot(path=filepath)

            if (i + 1) % 240 == 0:
                elapsed = (i + 1) / FPS
                print(f"    {i+1}/{TOTAL_FRAMES} ({(i+1)/TOTAL_FRAMES*100:.0f}%) | {elapsed:.0f}s/{DURATION}s")

        print("  ✓ 帧捕获完成")
        print()
        print("[4/4] FFmpeg 高质量合成 (CRF=10)...")

        timestamp_str = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        output_file = os.path.join(OUTPUT_DIR, f"流程化创造学习视频_V6_Final_{timestamp_str}.mp4")

        cmd = [
            "ffmpeg", "-y",
            "-framerate", str(FPS),
            "-i", os.path.join(TEMP_DIR, "frame_%04d.png"),
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-crf", "8",
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
            print("✅ 最终渲染完成!")
            print("=" * 60)
            print(f"📁 输出文件: {output_file}")
            print(f"📦 文件大小: {file_size / 1024 / 1024:.2f} MB")
            print(f"📐 分辨率: {WIDTH}x{HEIGHT} (竖版抖音)")
            print(f"⏱ 时长: {DURATION}s @ {FPS}fps")
            print("=" * 60)
        else:
            print("❌ FFmpeg渲染失败:", result.stderr[:300])

        import shutil
        print()
        print("清理临时帧...")
        shutil.rmtree(TEMP_DIR, ignore_errors=True)
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
