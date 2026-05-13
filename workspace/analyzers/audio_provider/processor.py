"""
音频文件提供器核心逻辑
将音频文件拷贝到 Remotion 的 public 目录
"""
import os
import shutil

def provide(audio_path):
    public_dir = os.path.join("src", "renderer", "public")
    os.makedirs(public_dir, exist_ok=True)
    dest = os.path.join(public_dir, os.path.basename(audio_path))

    if not os.path.exists(dest):
        shutil.copy2(audio_path, dest)
        print(f"[AudioProvider] 音频已拷贝到 {dest}")
    else:
        print(f"[AudioProvider] 音频已存在于 {dest}，跳过拷贝")

    print(f"[AudioProvider] 音频文件就绪: {os.path.basename(audio_path)}")