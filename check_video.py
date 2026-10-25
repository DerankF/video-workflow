#!/usr/bin/env python3
"""
检查视频每3秒的帧质量，确认是否内容堆积在前3秒
"""
import subprocess
import os

VIDEO = "renders/流程化创造学习视频_CSS_V4_2026-06-29_22-20-35.mp4"
OUT_DIR = "debug_frames"
os.makedirs(OUT_DIR, exist_ok=True)

# 每秒提取1帧
seconds = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21]

for sec in seconds:
    outfile = os.path.join(OUT_DIR, f"sec_{sec:02d}s.png")
    cmd = [
        "ffmpeg", "-y",
        "-ss", str(sec),
        "-i", VIDEO,
        "-vframes", "1",
        "-q:v", "2",
        outfile
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if os.path.exists(outfile):
        size = os.path.getsize(outfile)
        print(f"  [{sec:2d}s] {size:>10,} bytes - {outfile}")
    else:
        print(f"  [{sec:2d}s] FAILED")

print("\n检查完成！")
print("查看 debug_frames/ 目录中的截图来确认内容分布")
