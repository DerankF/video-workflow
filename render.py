#!/usr/bin/env python3
"""
流程化创造学习视频 — FFmpeg 直接渲染脚本
通过 Canvas 帧生成视频
"""
import subprocess
import os
import sys

OUTPUT_DIR = "renders"
os.makedirs(OUTPUT_DIR, exist_ok=True)

print("=" * 60)
print("流程化创造学习视频 — 视频渲染")
print("=" * 60)
print()
print("方案说明:")
print("1. HTML+GSAP 动画已编写完成 (index.html)")
print("2. 建议使用浏览器 DevTools 录制: ")
print("   - 打开 http://localhost:18899/index.html")
print("   - 按 F12 打开 DevTools -> Performance 标签")
print("   - 点击录制按钮,等待20秒动画播放完毕")
print("   - 导出为视频或使用 MediaRecorder API")
print()
print("3. 或使用 FFmpeg + Screen Capturer:")
print(f"   ffmpeg -f dshow -i video=\"屏幕_capture\" -t 20 -vf \"scale=1080:1920:flags=lanczos\" \"{OUTPUT_DIR}/流程化创造学习视频.mp4\"")
print()
print("或者:")
print("   使用 Playwright 截取每一帧,然后用 FFmpeg 合成视频")
print("=" * 60)
