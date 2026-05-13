"""
音频基础信息提取器入口
用法: python src/analyzers/modules/audio_info/run.py <音频路径> <输出JSON路径>
"""
import sys
import json
from processor import extract_info

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("用法: python src/analyzers/modules/audio_info/run.py <音频路径> <输出JSON路径>")
        sys.exit(1)

    info = extract_info(sys.argv[1])
    with open(sys.argv[2], "w", encoding="utf-8") as f:
        json.dump(info, f, ensure_ascii=False, indent=2)
    print(f"[AudioInfo] 音频信息已保存至 {sys.argv[2]}")
    print(f"  文件名: {info['audio_file']}")
    print(f"  时长: {info['audio_duration_ms']}ms")