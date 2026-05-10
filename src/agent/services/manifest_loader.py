"""
VibePV 零件清单加载器
从 renderer/components/*/manifest.json 中读取所有零件的基本信息
"""
import json
import os
from pathlib import Path


def load_manifests(meta_dir=None):
    """扫描零件目录，返回 { 零件名: manifest内容 } 的字典"""
    if meta_dir is None:
        meta_dir = Path(__file__).resolve().parent.parent.parent / "renderer" / "components"

    manifests = {}
    if not os.path.isdir(meta_dir):
        print(f"[ManifestLoader] 警告: 未找到组件目录 {meta_dir}")
        return manifests

    for folder in sorted(os.listdir(meta_dir)):
        folder_path = os.path.join(meta_dir, folder)
        if not os.path.isdir(folder_path):
            continue
        manifest_path = os.path.join(folder_path, "manifest.json")
        if os.path.isfile(manifest_path):
            try:
                with open(manifest_path, "r", encoding="utf-8") as f:
                    meta = json.load(f)
                    name = meta.get("name", folder)
                    manifests[name] = meta
            except json.JSONDecodeError:
                print(f"[ManifestLoader] 警告: 无法解析 manifest 文件 {manifest_path}")

    return manifests