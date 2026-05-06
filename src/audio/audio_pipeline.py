"""
VibePV 完整音频分析管线（自动合并版）
用法: python src/audio/audio_pipeline.py <音频路径> <输出JSON路径> [--bpm <手动BPM值>] [--multiplier <倍率>]
示例: python src/audio/audio_pipeline.py test_audio/song.wav output/analysis.json
      python src/audio/audio_pipeline.py test_audio/song.wav output/analysis.json --bpm 140 --multiplier 0.672
"""

import sys, json, os
from multiprocessing import Process

# ========== 默认合并倍率 ==========
DEFAULT_MULTIPLIER = 0.672
# ===================================

def run_lyrics(audio_path):
    print("[VibePV] ===== 第一阶段（并发）：歌词识别与对齐 =====")
    aligned_lyrics_path = "output/temp_aligned.json"
    os.system(f"python src/audio/lyrics_aligner.py {audio_path} {aligned_lyrics_path}")

def run_bpm(audio_path, manual_bpm=None):
    print("\n[VibePV] ===== 第二阶段（并发）：BPM检测 =====")
    from bpm_detector import detect_bpm
    bpm_data = detect_bpm(audio_path)

    if manual_bpm:
        bpm_data["detected_bpm"] = manual_bpm
        bpm_data["manual_override"] = True
    else:
        bpm_data["manual_override"] = False
    return bpm_data

def merge_sentences(input_path: str, bpm: float, multiplier: float):
    """内联合并函数，直接使用全局倍率"""
    beat_ms = 60000 / bpm
    pause_threshold_ms = beat_ms * multiplier
    print(f"[VibePV] 自动合并中... BPM: {bpm}, 断句阈值: {pause_threshold_ms:.0f}ms ({multiplier}拍)")

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

    print(f"[VibePV] 合并完成！{len(words)} 字 → {len(sentences)} 句")
    return sentences

def run():
    if len(sys.argv) < 3:
        print("用法: python src/audio/audio_pipeline.py <音频路径> <输出JSON路径> [--bpm <手动BPM值>] [--multiplier <倍率>]")
        sys.exit(1)

    audio_path = sys.argv[1]
    output_path = sys.argv[2]
    manual_bpm = None
    multiplier = DEFAULT_MULTIPLIER

    # 解析命令行参数
    args = sys.argv[3:]
    i = 0
    while i < len(args):
        if args[i] == "--bpm" and i + 1 < len(args):
            manual_bpm = float(args[i + 1])
            i += 2
        elif args[i] == "--multiplier" and i + 1 < len(args):
            multiplier = float(args[i + 1])
            i += 2
        else:
            i += 1

    # 启动歌词对齐进程（GPU）
    p1 = Process(target=run_lyrics, args=(audio_path,))
    p1.start()

    # 同时启动BPM检测（CPU）
    bpm_data = run_bpm(audio_path, manual_bpm)

    # 等待歌词对齐完成
    p1.join()

    # 读取逐字歌词
    aligned_lyrics_path = "output/temp_aligned.json"
    with open(aligned_lyrics_path, "r", encoding="utf-8") as f:
        words_data = json.load(f)

    # 自动合并为句子
    bpm = bpm_data["detected_bpm"]
    sentences_data = merge_sentences(aligned_lyrics_path, bpm, multiplier)

    # 组装最终输出（同时保留逐字和逐句两种粒度）
    output = {
        "lyrics": {
            "words": words_data,        # 逐字（卡拉OK逐字高亮用）
            "sentences": sentences_data # 逐句（滚动字幕用）
        },
        "bpm": bpm_data,
        "merge_multiplier": multiplier  # 记录合并倍率，方便追溯
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\n[VibePV] 全部分析完成！已保存至 {output_path}")
    print(f"  - 逐字歌词: {len(words_data)} 段")
    print(f"  - 逐句歌词: {len(sentences_data)} 段")
    print(f"  - BPM: {bpm}")

if __name__ == "__main__":
    run()
