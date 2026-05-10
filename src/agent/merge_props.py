"""
合并视觉计划与独立数据文件，生成 Remotion 可用的 props.json
用法: python src/agent/merge_props.py <visual_params.json> <props.json>
"""
import sys
import json
import os
from services.data_scanner import scan_data_sources


def set_nested_field(obj, field_path, value):
    keys = field_path.split(".")
    for key in keys[:-1]:
        if key not in obj or obj[key] is None:
            obj[key] = {}
        obj = obj[key]
    obj[keys[-1]] = value


def merge(visual_path, output_path):
    if not os.path.exists(visual_path):
        print(f"错误: 未找到视觉计划文件 {visual_path}")
        sys.exit(1)

    with open(visual_path, "r", encoding="utf-8") as f:
        visual = json.load(f)
    visual_plan = visual.get("visual_plan", visual)

    # 初始化 props，只包含视觉相关字段，其余由动态扫描填充
    props = {
        "visual_params": visual.get("visual_params", {}),
        "visual_plan": visual_plan,
    }

    # 动态扫描数据源，自动加载所有可用数据
    scan_result = scan_data_sources()
    for field, filepath in scan_result.get("data_sources", {}).items():
        if filepath is None:
            continue
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            # 关键修复：如果 data 是一个字典，需要根据字段名提取对应的值
            if isinstance(data, dict):
                if field in data:
                    # 字段名直接匹配（如 field="audio_file", data={"audio_file": "xxx", ...}）
                    set_nested_field(props, field, data[field])
                    print(f"[Merge] 已加载: {filepath} -> {field}")
                else:
                    # 字段名可能嵌套（如 field="lyrics.words"），直接设置整个 data
                    set_nested_field(props, field, data)
                    print(f"[Merge] 已加载: {filepath} -> {field}")
            else:
                # data 是数组或其他类型，直接设置
                set_nested_field(props, field, data)
                print(f"[Merge] 已加载: {filepath} -> {field}")
        except (json.JSONDecodeError, KeyError):
            print(f"[Merge] 警告: 无法读取 {filepath}")

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(props, f, ensure_ascii=False, indent=2)

    print(f"[Merge] props.json 已保存至 {output_path}")


def main():
    if len(sys.argv) != 3:
        print("用法: python src/agent/merge_props.py <visual_params.json> <props.json>")
        sys.exit(1)
    merge(sys.argv[1], sys.argv[2])


if __name__ == "__main__":
    main()