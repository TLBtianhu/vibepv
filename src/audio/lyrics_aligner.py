"""
VibePV 歌词对齐管线
用法: python src/audio/lyrics_aligner.py <音频路径> <输出JSON路径>
"""

import sys, json, torch
from qwen_asr import Qwen3ASRModel

def align(audio_path: str, output_path: str):
    print("[VibePV] 正在加载模型 (ASR + ForcedAligner)...")
    model = Qwen3ASRModel.from_pretrained(
        "models/Qwen3-ASR-0.6B",
        forced_aligner="models/Qwen3-ForcedAligner-0.6B",
        dtype=torch.bfloat16,
        device_map="cuda:0",
    )

    print("[VibePV] 正在进行带时间戳的歌词识别...")
    results = model.transcribe(
        audio=[audio_path],
        language="Chinese",
        return_time_stamps=True,
    )

    lyrics_data = []
    for segment in results[0].time_stamps:
        lyrics_data.append({
            "text": segment.text,
            "start_ms": round(segment.start_time * 1000),
            "end_ms": round(segment.end_time * 1000)
        })

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(lyrics_data, f, ensure_ascii=False, indent=2)

    print(f"[VibePV] 识别完成！共 {len(lyrics_data)} 段歌词，已保存至 {output_path}")
    for item in lyrics_data[:5]:
        print(f"  [{item['start_ms']}ms] {item['text']}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("用法: python src/audio/lyrics_aligner.py <音频路径> <输出JSON路径>")
        sys.exit(1)
    align(sys.argv[1], sys.argv[2])
