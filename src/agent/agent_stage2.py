"""
VibePV Agent 阶段二：视觉计划生成
用法:
  全量生成: python src/agent/agent_stage2.py <输出JSON路径> --components-file output/component_selection.json --prompt '风格描述'
  增量生成: python src/agent/agent_stage2.py <输出JSON路径> --components-file output/component_selection.json --edit-target output/edit_target.json
"""
import sys
import json
import os
import shutil
import asyncio
from services.data_scanner import scan_data_sources
from core.component_selector import load_selection
from core.full_planner import generate_visual_plan as full_generate
from core.incremental_planner import generate_visual_plan as incremental_generate


async def run():
    if len(sys.argv) < 3 or "--components-file" not in sys.argv:
        print("用法:")
        print("  全量生成: python src/agent/agent_stage2.py <输出JSON路径> --components-file output/component_selection.json --prompt '风格描述'")
        print("  增量生成: python src/agent/agent_stage2.py <输出JSON路径> --components-file output/component_selection.json --edit-target output/edit_target.json")
        sys.exit(1)

    output_path = sys.argv[1]
    file_index = sys.argv.index("--components-file")
    components_file = sys.argv[file_index + 1]

    # 全量生成参数
    user_prompt = ""
    if "--prompt" in sys.argv:
        idx = sys.argv.index("--prompt")
        user_prompt = " ".join(sys.argv[idx + 1:])

    # 增量生成参数
    incremental_components = []
    incremental_prompt = ""
    if "--edit-target" in sys.argv:
        idx = sys.argv.index("--edit-target")
        edit_target_file = sys.argv[idx + 1]
        if os.path.exists(edit_target_file):
            with open(edit_target_file, "r", encoding="utf-8-sig") as f:
                edit_target = json.load(f)
                incremental_components = edit_target.get("components", [])
                incremental_prompt = edit_target.get("prompt", "")
            print(f"[Agent] 增量生成模式")
            print(f"  目标零件: {incremental_components}")
            print(f"  调整提示: {incremental_prompt}")
        else:
            print(f"[Agent] 警告: 编辑目标文件不存在: {edit_target_file}")

    if not os.path.exists(components_file):
        print(f"错误: 零件选择文件不存在: {components_file}")
        print("请先运行阶段一生成该文件。")
        sys.exit(1)

    selected_components = load_selection(components_file)
    print(f"[Agent] 用户指定的零件列表: {selected_components}")

    # 加载之前的视觉计划（供增量生成使用）
    previous_plan = None
    if os.path.exists(output_path):
        with open(output_path, "r", encoding="utf-8") as f:
            previous_plan = json.load(f)

    adata = scan_data_sources()

    # 根据模式选择生成器
    if incremental_components and incremental_prompt and previous_plan:
        visual_plan = await incremental_generate(
            adata, incremental_prompt, incremental_components, previous_plan
        )
    else:
        visual_plan = await full_generate(adata, user_prompt, selected_components)

    if visual_plan is None:
        raise RuntimeError("未能生成有效的视觉计划")

    result = {"visual_plan": visual_plan}

    # 1. 保存到 output/ 目录
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"[Agent] 视觉计划已保存至 {output_path}")

    # 2. 自动拷贝到 renderer/public/ (供 Remotion Studio 使用)
    ui_dir = os.path.join("src", "renderer", "public")
    os.makedirs(ui_dir, exist_ok=True)
    ui_path = os.path.join(ui_dir, "visual_params.json")
    try:
        shutil.copy2(output_path, ui_path)
        print(f"[Agent] 已同步拷贝至 {ui_path}（Remotion Studio 可自动读取）")
    except Exception as e:
        print(f"[Agent] 拷贝到 Remotion 目录失败（可忽略）: {e}")

    # 3. 自动拷贝到 vibe_ui/public/ (供独立 UI 项目使用)
    vibe_ui_dir = os.path.join("vibe_ui", "public")
    os.makedirs(vibe_ui_dir, exist_ok=True)
    vibe_ui_path = os.path.join(vibe_ui_dir, "visual_params.json")
    try:
        shutil.copy2(output_path, vibe_ui_path)
        print(f"[Agent] 已同步拷贝至 {vibe_ui_path}（独立 UI 可自动读取）")
    except Exception as e:
        print(f"[Agent] 拷贝到 vibe_ui 目录失败（可忽略）: {e}")


if __name__ == "__main__":
    asyncio.run(run())