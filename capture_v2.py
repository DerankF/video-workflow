#!/usr/bin/env python3
"""
流程化创造学习视频 — Playwright 帧捕获 V2
通过注入 JavaScript 手动控制 GSAP 时间线
"""
import asyncio
import subprocess
import os
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

# 本地文件路径
LOCAL_FILE = "file:///D:/WorkBuddy/%E6%B5%81%E7%A8%8B%E5%8C%96%E5%88%9B%E9%80%A0%E5%AD%A6%E4%B9%A0%E8%A7%86%E9%A2%91/index.html"

async def main():
    print("=" * 60)
    print("流程化创造学习视频 — Playwright 帧捕获 V2")
    print("=" * 60)
    print(f"分辨率: {WIDTH}x{HEIGHT} (竖版)")
    print(f"帧率: {FPS} FPS")
    print(f"时长: {DURATION}s")
    print(f"总帧数: {TOTAL_FRAMES}")
    print()

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": WIDTH, "height": HEIGHT},
            device_scale_factor=1
        )
        page = await context.new_page()

        print("[1/3] 打开本地HTML文件...")
        
        # 直接加载本地文件,不需要HTTP服务器
        await page.goto(LOCAL_FILE, wait_until="load")
        
        # 等待 GSAP 动画初始化
        await page.wait_for_timeout(3000)
        
        # 检查页面是否加载成功
        title = await page.title()
        print(f"  页面标题: {title}")

        # 获取当前动画进度
        current_time = await page.evaluate("() => { return window.__timelines ? window.__timelines['learning-video'].time() : -1; }")
        print(f"  当前动画时间线进度: {current_time}s")

        print()
        print(f"[2/3] 暂停动画,开始逐帧捕获...")
        print()

        # 关键: 将 timeline 设置为 paused 并遍历每一帧
        # 我们注入 JavaScript 来控制 GSAP timeline 的每一帧
        pause_script = """
        () => {
            if (!window.__timelines || !window.__timelines['learning-video']) return 'no timeline';
            const tl = window.__timelines['learning-video'];
            tl.pause();
            return 'paused';
        }
        """
        
        result = await page.evaluate(pause_script)
        print(f"  GSAP 时间线状态: {result}")

        # 遍历每一帧
        for i in range(TOTAL_FRAMES):
            timestamp = i / FPS  # 当前帧的时间戳
            
            # 设置动画进度
            seek_script = f"""
            () => {{
                if (!window.__timelines || !window.__timelines['learning-video']) return 'error';
                const tl = window.__timelines['learning-video'];
                tl.pause();
                tl.seek({timestamp});
                return tl.time();
            }}
            """
            
            await page.evaluate(seek_script)

            # 截图
            frame_num = f"{i:04d}"
            filepath = os.path.join(TEMP_DIR, f"frame_{frame_num}.png")
            await page.screenshot(path=filepath, full_page=False)

            if (i + 1) % 100 == 0:
                pct = (i + 1) / TOTAL_FRAMES * 100
                print(f"  进度: {i+1}/{TOTAL_FRAMES} ({pct:.0f}%)")

        print()
        print(f"[3/3] 用 FFmpeg 合成视频...")

        # 使用 FFmpeg 将帧序列合成为视频
        from datetime import datetime
        timestamp_str = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        output_file = os.path.join(OUTPUT_DIR, f"流程化创造学习视频_20s_{timestamp_str}.mp4")

        cmd = [
            "ffmpeg",
            "-y",
            "-r", str(FPS),
            "-i", os.path.join(TEMP_DIR, "frame_%04d.png"),
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-crf", "18",
            "-preset", "medium",
            "-profile:v", "high",
            "-level", "4.0",
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

        # 清理帧文件
        print()
        print("清理临时帧文件...")
        import shutil
        shutil.rmtree(TEMP_DIR, ignore_errors=True)

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
