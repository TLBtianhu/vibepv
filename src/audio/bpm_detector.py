"""
VibePV BPM检测模块 (DeepRhythm)
用法: python src/audio/bpm_detector.py <音频路径>
输出: JSON格式的BPM
"""

import sys
import json
from deeprhythm import DeepRhythmPredictor

def detect_bpm(audio_path: str):
    print(f"[VibePV] 正在用 DeepRhythm 检测音频BPM...")
    
    model = DeepRhythmPredictor()
    tempo = model.predict(audio_path)  # 直接返回 BPM 数值
    
    bpm_data = {
        "detected_bpm": round(float(tempo), 1),
        "model": "DeepRhythm"
    }
    
    print(f"[VibePV] 检测到 BPM: {bpm_data['detected_bpm']}")
    return bpm_data

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("用法: python src/audio/bpm_detector.py <音频路径>")
        sys.exit(1)
    
    result = detect_bpm(sys.argv[1])
    print(json.dumps(result, ensure_ascii=False, indent=2))
