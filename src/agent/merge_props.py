"""
合并 analysis.json 和 visual_params.json 为 Remotion 可用的 props.json
用法: python src/agent/merge_props.py analysis.json visual_params.json props.json
"""

import sys
import json

def merge(analysis_path, visual_path, output_path):
    with open(analysis_path, "r", encoding="utf-8") as f:
        analysis = json.load(f)
    with open(visual_path, "r", encoding="utf-8") as f:
        visual = json.load(f)

    # 提取视觉计划（新格式）
    visual_plan = visual.get("visual_plan", None)

    # 兼容旧格式：如果没有 visual_plan，则整个 visual 当做 visual_params
    if visual_plan is None:
        visual_params = visual
    else:
        # 新格式：提供默认 visual_params，颜色等信息从 visual_plan 提取（暂时使用默认值）
        visual_params = {
            "particle_speed": 1.0,
            "color_scheme": ["#0a0a2a", "#ff00ff", "#00ffff"],
            "energy_sync": "medium",
            "bpm_sync": "quarter_beat",
            "canvas_effects": [],
            "beat_effect": "none",
            "subtitle_animation": "fade_in",
        }

    props = {
        **analysis,
        "visual_params": visual_params,
        "visual_plan": visual_plan,
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(props, f, ensure_ascii=False, indent=2)

    print(f"合并完成，已保存至 {output_path}")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("用法: python src/agent/merge_props.py <analysis.json> <visual_params.json> <output.json>")
        sys.exit(1)
    merge(sys.argv[1], sys.argv[2], sys.argv[3])