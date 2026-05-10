"""数据源依赖检查"""

def check_missing_data(selected_components, available_fields):
    """
    检查所选零件依赖的数据字段是否缺失。
    available_fields: 当前可用的数据字段列表
    返回：{ 零件名: [缺失字段列表] } 的字典
    """
    from services.manifest_loader import load_manifests
    manifests = load_manifests()

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