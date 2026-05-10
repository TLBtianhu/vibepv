"""
VibePV Agent 主控脚本 (完全动态数据源)

用法:
  阶段一 (生成零件选择文件):
    python src/agent/agent.py --prompt '风格描述'
    生成 output/component_selection.json 后停止。

  阶段二 (生成视觉计划):
    python src/agent/agent.py <输出JSON路径> --components-file output/component_selection.json
    从 component_selection.json 读取用户确认的零件列表，生成视觉计划。
"""
import sys
import json
import os
import asyncio
from services.data_scanner import scan_data_sources
from core.component_selector import select_components, save_selection, load_selection
from visual_planner import generate_visual_plan
from services.dependency_checker import check_missing_data


async def run():
    if len(sys.argv) < 2:
        print("用法:")
        print("  阶段一: python src/agent/agent.py --prompt '风格描述'")
        print("  阶段二: python src/agent/agent.py <输出JSON路径> --components-file output/component_selection.json")
        sys.exit(1)

    # ===== 阶段一：生成 component_selection.json =====
    if "--prompt" in sys.argv:
        prompt_index = sys.argv.index("--prompt")
        user_prompt = " ".join(sys.argv[prompt_index + 1:])

        selected_components = await select_components(user_prompt)
        save_selection(selected_components, user_prompt)

        # 扫描数据源，检查依赖
        adata = scan_data_sources()
        missing_data = check_missing_data(selected_components, adata.get("available_fields", []))

        print(f"\n📋 当前可用数据：{', '.join(adata.get('available_fields', [])) or '无'}")
        if missing_data:
            print("\nℹ️ 基于现有数据，以下零件不可用（缺少必要数据）：")
            for comp, fields in missing_data.items():
                print(f"  - {comp}（需要 {', '.join(fields)}）")
            print("\n💡 如需使用这些零件，请先运行对应的数据分析模块补齐数据。")
        else:
            print("\n✅ 所有选中的零件都有足够的可用数据。")

        print("\n" + "=" * 50)
        print("阶段一完成！component_selection.json 已生成。")
        print("请审核/修改该文件后运行阶段二：")
        print("  python src/agent/agent.py <输出JSON路径> --components-file output/component_selection.json")
        print("=" * 50)
        return

    # ===== 阶段二：生成 visual_params.json =====
    if "--components-file" in sys.argv:
        if len(sys.argv) < 3:
            print("错误: 阶段二需要指定输出文件路径")
            sys.exit(1)

        output_path = sys.argv[1]
        file_index = sys.argv.index("--components-file")
        components_file = sys.argv[file_index + 1]

        if not os.path.exists(components_file):
            print(f"错误: 零件选择文件不存在: {components_file}")
            sys.exit(1)

        selected_components = load_selection(components_file)
        print(f"[Agent] 用户指定的零件列表: {selected_components}")

        adata = scan_data_sources()
        visual_plan = await generate_visual_plan(adata, "", selected_components)
        if visual_plan is None:
            raise RuntimeError("未能生成有效的视觉计划")

        result = {"visual_plan": visual_plan}
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        print(f"[Agent] 视觉计划已保存至 {output_path}")
        return

    print("错误: 请提供 --prompt 或 --components-file 参数")
    sys.exit(1)


if __name__ == "__main__":
    asyncio.run(run())