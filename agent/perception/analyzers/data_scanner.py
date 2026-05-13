"""
VibePV 数据源扫描器
读大JSON的 data_sources 字段，返回可用数据字段列表。
"""
import json
import os

PROJECT_BUNDLE_PATH = "output/project_bundle.json"


def scan_data_sources():
    """读取 project_bundle.json，返回可用数据字段清单"""
    available_fields = []
    data_sources = {}

    if not os.path.exists(PROJECT_BUNDLE_PATH):
        print(f"[Scanner] 警告: {PROJECT_BUNDLE_PATH} 不存在")
        return {"available_fields": available_fields, "data_sources": data_sources}

    try:
        with open(PROJECT_BUNDLE_PATH, "r", encoding="utf-8") as f:
            bundle = json.load(f)
    except (json.JSONDecodeError, KeyError):
        print(f"[Scanner] 警告: 无法解析 {PROJECT_BUNDLE_PATH}")
        return {"available_fields": available_fields, "data_sources": data_sources}

    data_sources = bundle.get("data_sources", {})
    available_fields = bundle.get("available_fields", [])

    for field in available_fields:
        print(f"[Scanner] 发现数据: {field}")

    return {
        "available_fields": available_fields,
        "data_sources": data_sources,
    }