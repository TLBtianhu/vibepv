"""
数据源依赖检查
"""
import json
import os

PROJECT_BUNDLE_PATH = "output/project_bundle.json"


def check_missing_data(selected_components):
    """检查所选零件依赖的数据字段是否缺失，返回 {零件名: [缺失字段列表]}"""
    from agent.perception.components.manifest_loader import load_manifests

    manifests = load_manifests()

    # 读大JSON获取可用字段
    available_fields = []
    if os.path.exists(PROJECT_BUNDLE_PATH):
        try:
            with open(PROJECT_BUNDLE_PATH, "r", encoding="utf-8") as f:
                bundle = json.load(f)
            available_fields = bundle.get("available_fields", [])
        except (json.JSONDecodeError, KeyError):
            pass

    missing_map = {}
    for comp_name in selected_components:
        if comp_name not in manifests:
            continue
        meta = manifests[comp_name]
        requires = meta.get("requires", {}).get("data", [])
        missing = [f for f in requires if f not in available_fields]
        if missing:
            missing_map[comp_name] = missing
    return missing_map