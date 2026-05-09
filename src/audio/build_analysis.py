"""
VibePV 数据组装模块（动态扫描版）
将分散的音频分析结果自动组装为统一的 analysis.json
用法: python src/audio/build_analysis.py <音频路径> <输出JSON路径>
示例: python src/audio/build_analysis.py test_audio/gouqiqishi.wav output/analysis.json
数据源由 src/audio/*_manifest.json 动态声明，本模块自动扫描并组装。
"""

import sys, json, os, shutil, glob
import librosa


def load_manifests(audio_dir):
    """扫描 src/audio/ 下所有 *_manifest.json"""
    manifests = []
    pattern = os.path.join(audio_dir, "*_manifest.json")
    for filepath in sorted(glob.glob(pattern)):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                manifests.append(json.load(f))
        except (json.JSONDecodeError, KeyError):
            print(f"[Build] 警告: 无法解析 {filepath}")
    return manifests


def set_nested_field(obj, field_path, value):
    """将 value 设置到 obj 的嵌套字段路径上，如 'lyrics.words'"""
    keys = field_path.split(".")
    for key in keys[:-1]:
        if key not in obj or obj[key] is None:
            obj[key] = {}
        obj = obj[key]
    obj[keys[-1]] = value


def assemble(audio_path, output_path):
    audio_dir = os.path.dirname(os.path.abspath(__file__))
    manifests = load_manifests(audio_dir)
    print(f"[Build] 已加载 {len(manifests)} 个数据源定义")

    # 1. 拷贝音频到 public 目录
    remotion_public = os.path.join("src", "renderer", "public")
    os.makedirs(remotion_public, exist_ok=True)
    shutil.copy2(audio_path, os.path.join(remotion_public, os.path.basename(audio_path)))
    print(f"[Build] 音频已拷贝到 {remotion_public}")

    # 2. 读取音频时长
    y, sr = librosa.load(audio_path, sr=None)
    audio_duration_ms = int(len(y) / sr * 1000)

    # 3. 初始化输出
    output = {
        "audio_duration_ms": audio_duration_ms,
        "audio_file": os.path.basename(audio_path),
        "bpm": None,
        "lyrics": None,
        "merge_multiplier": None,
    }

    # 4. 根据 manifest 动态加载数据
    for manifest in manifests:
        for key, info in manifest.get("produces", {}).items():
            filepath = info["file"]
            if os.path.exists(filepath):
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    set_nested_field(output, info["field"], data)
                    print(f"[Build] 已加载: {filepath} -> {info['field']}")
                except (json.JSONDecodeError, KeyError):
                    print(f"[Build] 警告: 无法读取 {filepath}")
            else:
                print(f"[Build] 跳过: {filepath}（文件不存在）")

    # 5. 写入 analysis.json
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"[Build] 数据组装完成！已保存至 {output_path}")
    has_lyrics = output["lyrics"] is not None
    has_bpm = output["bpm"] is not None
    has_words = has_lyrics and output["lyrics"] is not None and "words" in output["lyrics"]
    has_sentences = has_lyrics and output["lyrics"] is not None and "sentences" in output["lyrics"] and len(output["lyrics"]["sentences"]) > 0
    print(f"  歌词: {'有' if has_words else '无'} ({len(output['lyrics']['words']) if has_words else 0} 字)")
    if has_words:
        print(f"  句子: {'有' if has_sentences else '无'} ({len(output['lyrics']['sentences']) if has_sentences else 0} 句)")
    print(f"  BPM: {output['bpm']['detected_bpm'] if has_bpm else '未检测'}")
    print(f"  音频时长: {audio_duration_ms}ms")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("用法: python src/audio/build_analysis.py <音频路径> <输出JSON路径>")
        print("示例: python src/audio/build_analysis.py test_audio/gouqiqishi.wav output/analysis.json")
        sys.exit(1)

    audio_path = sys.argv[1]
    output_path = sys.argv[2]

    if not os.path.exists(audio_path):
        print(f"错误: 音频文件不存在: {audio_path}")
        sys.exit(1)

    assemble(audio_path, output_path)