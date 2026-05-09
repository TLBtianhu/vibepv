"""
VibePV Agent 主控脚本

用法:
  阶段一 (生成零件选择文件):
    python src/agent/agent.py <analysis.json路径> --prompt '风格描述'
    生成 output/component_selection.json 后停止，请审核/修改该文件。

  阶段二 (生成视觉计划):
    python src/agent/agent.py <analysis.json路径> <输出JSON路径> --components-file output/component_selection.json
    从 component_selection.json 读取用户确认的零件列表，生成 visual_params.json。
"""
import sys
import json
import os
import asyncio
from component_selector import select_components, save_selection, load_selection
from visual_planner import generate_visual_plan


async def run():
    if len(sys.argv) < 3:
        print("用法:")
        print("  阶段一 (生成零件选择文件):")
        print("    python src/agent/agent.py <analysis.json路径> --prompt '风格描述'")
        print("  阶段二 (生成视觉计划):")
        print("    python src/agent/agent.py <analysis.json路径> <输出JSON路径> --components-file output/component_selection.json")
        sys.exit(1)

    analysis_path = sys.argv[1]

    # ========== 阶段一：生成 component_selection.json ==========
    if "--prompt" in sys.argv:
        prompt_index = sys.argv.index("--prompt")
        user_prompt = " ".join(sys.argv[prompt_index + 1:])

        with open(analysis_path, "r", encoding="utf-8") as f:
            analysis = json.load(f)

        selected_components = await select_components(analysis, user_prompt)
        save_selection(selected_components, analysis, user_prompt)

        print("\n" + "=" * 50)
        print("阶段一完成！component_selection.json 已生成。")
        print("请审核/修改该文件中的 selected_components 字段，然后运行阶段二：")
        print(f"  python src/agent/agent.py {analysis_path} <输出JSON路径> --components-file output/component_selection.json")
        print("=" * 50)
        return

    # ========== 阶段二：生成 visual_params.json ==========
    if "--components-file" in sys.argv:
        if len(sys.argv) < 4:
            print("错误: 阶段二需要指定输出文件路径")
            print(f"用法: python src/agent/agent.py {analysis_path} <输出JSON路径> --components-file output/component_selection.json")
            sys.exit(1)

        output_path = sys.argv[2]
        file_index = sys.argv.index("--components-file")
        components_file = sys.argv[file_index + 1]

        if not os.path.exists(components_file):
            print(f"错误: 零件选择文件不存在: {components_file}")
            print("请先运行阶段一生成该文件：")
            print(f"  python src/agent/agent.py {analysis_path} --prompt '风格描述'")
            sys.exit(1)

        with open(analysis_path, "r", encoding="utf-8") as f:
            analysis = json.load(f)

        print("[Agent] UI 模式：从中间文件加载零件列表...")
        selected_components = load_selection(components_file)
        print(f"[Agent] 用户指定的零件列表: {selected_components}")

        visual_plan = await generate_visual_plan(analysis, "", selected_components)

        if visual_plan is None:
            raise RuntimeError("未能生成有效的视觉计划")

        result = {"visual_plan": visual_plan}
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        print(f"[Agent] 视觉计划已保存至 {output_path}")
        return

    print("错误: 请提供 --prompt 或 --components-file 参数")
    print("用法:")
    print("  阶段一: python src/agent/agent.py <analysis.json路径> --prompt '风格描述'")
    print("  阶段二: python src/agent/agent.py <analysis.json路径> <输出JSON路径> --components-file output/component_selection.json")
    sys.exit(1)


if __name__ == "__main__":
    asyncio.run(run())