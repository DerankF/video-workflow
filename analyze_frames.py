#!/usr/bin/env python3
"""
逐帧对比分析：检查每3秒内的帧差异，确认动画是否真的在播放
"""
import subprocess
import os
import hashlib
from PIL import Image
import numpy as np

VIDEO = "renders/流程化创造学习视频_CSS_V4_2026-06-29_22-20-35.mp4"
OUT_DIR = "debug_frames"
FRAME_SAMPLES = 5  # 每个3秒区间取5帧

os.makedirs(OUT_DIR, exist_ok=True)

# 提取所有帧到临时目录
TEMP_FRAMES = "temp_frames"
os.makedirs(TEMP_FRAMES, exist_ok=True)

cmd = [
    "ffmpeg", "-y",
    "-i", VIDEO,
    "-vf", "scale=360:640",  # 缩小到360x640加快处理
    os.path.join(TEMP_FRAMES, "frame_%04d.png")
]
subprocess.run(cmd, capture_output=True, text=True)

print("=" * 60)
print("逐帧差异分析 (动画是否真的在动?)")
print("=" * 60)

# 读取所有帧
frames = []
frame_files = sorted([f for f in os.listdir(TEMP_FRAMES) if f.startswith("frame_")])
for ff in frame_files:
    img = Image.open(os.path.join(TEMP_FRAMES, ff))
    frames.append(np.array(img))

total = len(frames)
print(f"\n总帧数: {total}")
print()

# 计算相邻帧之间的差异
diffs = []
for i in range(1, total):
    diff = np.sum(np.abs(frames[i].astype(int) - frames[i-1].astype(int)))
    diffs.append(diff)

# 统计
avg_diff = np.mean(diffs)
max_diff = np.max(diffs)
min_diff = np.min(diffs)

print(f"相邻帧平均差异值: {avg_diff:.0f}")
print(f"最小差异: {min_diff:.0f}")
print(f"最大差异: {max_diff:.0f}")
print()

if avg_diff < 50:
    print("⚠️ 警告: 帧差异极小，说明动画几乎不动/内容重复！")
elif avg_diff < 500:
    print("⚠️ 注意: 帧差异偏小，动画变化不够明显")
else:
    print("✅ 帧差异正常，动画在持续变化")

print()

# 检查前3秒 vs 后3秒的差异分布
third = total // 3
sections = [
    ("前3秒 (0-3s)", range(0, third)),
    ("中3秒 (3-7s)", range(third, 2*third)),
    ("后3秒 (7-10s+)", range(2*third, total))
]

for label, indices in sections:
    section_diffs = [diffs[i] for i in indices if i < len(diffs)]
    if section_diffs:
        avg = np.mean(section_diffs)
        print(f"  {label}: 平均帧差异 = {avg:.0f} (共{len(section_diffs)}个采样)")

# 清理
import shutil
shutil.rmtree(TEMP_FRAMES, ignore_errors=True)
