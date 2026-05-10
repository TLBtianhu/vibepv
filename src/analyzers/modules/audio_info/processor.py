"""
音频基础信息提取器
从音频文件中提取文件名和时长
"""
import os
import librosa

def extract_info(audio_path: str) -> dict:
    """提取音频基础信息，返回可序列化的字典"""
    audio_file = os.path.basename(audio_path)
    y, sr = librosa.load(audio_path, sr=None)
    duration_ms = int(len(y) / sr * 1000)

    return {
        "audio_file": audio_file,
        "audio_duration_ms": duration_ms,
    }