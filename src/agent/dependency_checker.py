"""数据源依赖检查"""

def check_missing_data(selected_components, adata):
    from tool_definitions import load_manifests as load_visual_manifests
    manifests = load_visual_manifests()
    available_fields = adata.get("available_fields", [])
    if "audio_file" not in available_fields:
        available_fields.append("audio_file")

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