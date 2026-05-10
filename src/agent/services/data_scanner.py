"""
VibePV 数据源动态扫描器
扫描 src/analyzers/modules/*/manifest.json，检查输出文件。
返回一个数据字典，供 Agent 使用。
不进行任何文件拷贝操作。
"""
import json
import os


def scan_data_sources(audio_path=None, modules_dir=None):
    """
    扫描数据源目录，返回可用数据信息字典。
    """
    if modules_dir is None:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        modules_dir = os.path.join(current_dir, "..", "..", "analyzers", "modules")

    available_fields = []
    data_sources = {}

    if not os.path.isdir(modules_dir):
        print(f"[Scanner] 警告: 数据源目录不存在 {modules_dir}")
        return {
            "available_fields": available_fields,
            "data_sources": data_sources,
        }

    for folder in sorted(os.listdir(modules_dir)):
        folder_path = os.path.join(modules_dir, folder)
        if not os.path.isdir(folder_path):
            continue
        manifest_path = os.path.join(folder_path, "manifest.json")
        if not os.path.isfile(manifest_path):
            continue
        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                manifest = json.load(f)
        except Exception:
            print(f"[Scanner] 警告: 无法解析 {manifest_path}")
            continue

        for key, info in manifest.get("produces", {}).items():
            filepath = info["file"]
            if os.path.exists(filepath):
                field = info["field"]
                available_fields.append(field)
                data_sources[field] = filepath
                print(f"[Scanner] 发现数据: {field} -> {filepath}")

    return {
        "available_fields": available_fields,
        "data_sources": data_sources,
    }