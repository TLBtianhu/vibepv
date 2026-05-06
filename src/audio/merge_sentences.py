"""
VibePV 歌词粒度优化（BPM动态版，全局倍率可调）
用法: python src/audio/merge_sentences.py <输入JSON路径> <输出JSON路径> <BPM>
功能: 根据BPM自动计算停顿阈值，倍率统一在此脚本顶部修改。

提示：运行前修改下面的 BEAT_MULTIPLIER 变量值即可（例如1.0、1.5、2.0）。
"""

import sys, json

# ==========【全局：断句倍率】==========
# 倍率含义：停顿超过 (BPM 的一拍时长 × 倍率) 则断句。
# 1.0 = 一拍，1.5 = 一拍半，2.0 = 两拍。可自行修改！
BEAT_MULTIPLIER = 0.672
# =======================================

def merge_to_sentences(input_path: str, output_path: str, bpm: float):
    beat_ms = 60000 / bpm
    pause_threshold_ms = beat_ms * BEAT_MULTIPLIER
    print(f"[VibePV] BPM: {bpm}, 一拍: {beat_ms:.0f}ms, 断句阈值: {pause_threshold_ms:.0f}ms ({BEAT_MULTIPLIER}拍)")

    with open(input_path, "r", encoding="utf-8") as f:
        words = json.load(f)

    sentences = []
    current_sentence_words = []

    for i, word in enumerate(words):
        current_sentence_words.append(word)

        is_last_word = (i == len(words) - 1)
        is_punctuation = word["text"] in "，。！？；、："

        gap_ms = 0
        if not is_last_word:
            next_word = words[i + 1]
            gap_ms = next_word["start_ms"] - word["end_ms"]

        should_split = is_last_word or is_punctuation or (gap_ms > pause_threshold_ms)

        if should_split and current_sentence_words:
            sentence_text = "".join(w["text"] for w in current_sentence_words)
            sentences.append({
                "text": sentence_text,
                "start_ms": current_sentence_words[0]["start_ms"],
                "end_ms": current_sentence_words[-1]["end_ms"]
            })
            current_sentence_words = []

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(sentences, f, ensure_ascii=False, indent=2)

    print(f"[VibePV] 合并完成！{len(words)} 字 → {len(sentences)} 句")
    for sent in sentences[:5]:
        print(f"  [{sent['start_ms']}ms] {sent['text']}")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("用法: python src/audio/merge_sentences.py <输入JSON路径> <输出JSON路径> <BPM>")
        sys.exit(1)

    bpm = float(sys.argv[3])
    merge_to_sentences(sys.argv[1], sys.argv[2], bpm)
