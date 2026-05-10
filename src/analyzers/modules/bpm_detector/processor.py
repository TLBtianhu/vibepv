"""
VibePV BPM检测模块
用法: python src/audio/bpm_detector.py <音频路径> <输出JSON路径>
输出: BPM JSON 文件
"""

import sys, json
from deeprhythm import DeepRhythmPredictor

def detect_bpm(audio_path: str, output_path: str):
    print(f"[VibePV] 正在用 DeepRhythm 检测音频BPM...")
    
    try:
        model = DeepRhythmPredictor()
        tempo = model.predict(audio_path)
        bpm_data = {
            "detected_bpm": round(float(tempo), 1),
            "model": "DeepRhythm",
            "manual_override": False
        }
    except Exception as e:
        print(f"[VibePV] BPM 检测失败: {e}")
        bpm_data = {
            "detected_bpm": None,
            "model": "DeepRhythm",
            "error": str(e)
        }
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(bpm_data, f, ensure_ascii=False, indent=2)

    print(f"[VibePV] 检测到 BPM: {bpm_data.get('detected_bpm', '无')}")
    return bpm_data

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("用法: python src/audio/bpm_detector.py <音频路径> <输出JSON路径>")
        sys.exit(1)
    detect_bpm(sys.argv[1], sys.argv[2])