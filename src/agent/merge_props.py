"""
合并视觉计划与独立数据文件，生成 Remotion 可用的 props.json
用法: python src/agent/merge_props.py <visual_params.json> <props.json>
"""
import sys
import json
import os
from data_scanner import scan_data_sources


def set_nested_field(obj, field_path, value):
    keys = field_path.split(".")
    for key in keys[:-1]:
        if key not in obj or obj[key] is None:
            obj[key] = {}
        obj = obj[key]
    obj[keys[-1]] = value


def merge(visual_path, output_path):
    # 1. 读取视觉计划
    if not os.path.exists(visual_path):
        print(f"错误: 未找到视觉计划文件 {visual_path}")
        sys.exit(1)

    with open(visual_path, "r", encoding="utf-8") as f:
        visual = json.load(f)
    visual_plan = visual.get("visual_plan", visual)

    # 2. 初始化 props（所有字段都由动态扫描填充，不预设任何值）
    props = {
        "visual_params": visual.get("visual_params", {}),
        "visual_plan": visual_plan,
    }

    # 3. 动态扫描数据源并加载
    scan_result = scan_data_sources()

    for field, filepath in scan_result.get("data_sources", {}).items():
        if filepath is None:
            continue
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            # audio_info.json 是一个字典，包含多个字段，需要展开设置
            if field in data and len(data) > 1:
                # 如果 JSON 本身就是一个包含多个字段的对象，逐个设置
                for key, value in data.items():
                    set_nested_field(props, key, value)
                    print(f"[Merge] 已加载: {filepath} -> {key}")
            else:
                set_nested_field(props, field, data)
                print(f"[Merge] 已加载: {filepath} -> {field}")
        except (json.JSONDecodeError, KeyError):
            print(f"[Merge] 警告: 无法读取 {filepath}")

    # 4. 写入 props.json
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