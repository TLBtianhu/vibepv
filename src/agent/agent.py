"""
VibePV Agent 主控脚本 (完全动态数据源，无音频路径依赖)

用法:
  阶段一 (生成零件选择文件):
    python src/agent/agent.py --prompt '风格描述'
    生成 output/component_selection.json 后停止，请审核该文件。

  阶段二 (生成视觉计划):
    python src/agent/agent.py <输出JSON路径> --components-file output/component_selection.json
    从 component_selection.json 读取用户确认的零件列表，生成视觉计划。
"""
import sys
import json
import os
import asyncio
from data_scanner import scan_data_sources
from component_selector import select_components, save_selection, load_selection
from visual_planner import generate_visual_plan
from dependency_checker import check_missing_data


def load_context(adata):
    """根据数据源清单加载具体数据，构建上下文字典"""
    context = {}
    sources = adata.get("data_sources", {})

    # 加载音频基础信息
    if "audio_file" in sources or "audio_duration_ms" in sources:
        info_path = sources.get("audio_file") or sources.get("audio_duration_ms")
        if info_path and os.path.exists(info_path):
            with open(info_path, "r", encoding="utf-8") as f:
                info = json.load(f)
            context["audio_file"] = info.get("audio_file", "")
            context["audio_duration_ms"] = info.get("audio_duration_ms", 0)

    # 加载 BPM
    if "bpm" in sources:
        bpm_path = sources["bpm"]
        if os.path.exists(bpm_path):
            with open(bpm_path, "r", encoding="utf-8") as f:
                context["bpm"] = json.load(f)

    # 加载歌词 words
    if "lyrics.words" in sources:
        words_path = sources["lyrics.words"]
        if os.path.exists(words_path):
            with open(words_path, "r", encoding="utf-8") as f:
                context["lyrics_words"] = json.load(f)

    context["available_fields"] = adata.get("available_fields", [])
    return context


async def run():
    if len(sys.argv) < 2:
        print("用法:")
        print("  阶段一: python src/agent/agent.py --prompt '风格描述'")
        print("  阶段二: python src/agent/agent.py <输出JSON路径> --components-file output/component_selection.json")
        sys.exit(1)

    # 动态扫描数据源
    adata = scan_data_sources()
    context = load_context(adata)

    # ===== 阶段一 =====
    if "--prompt" in sys.argv:
        prompt_index = sys.argv.index("--prompt")
        user_prompt = " ".join(sys.argv[prompt_index + 1:])

        selected_components = await select_components(context, user_prompt)
        save_selection(selected_components, context, user_prompt)

        # 显示可用数据清单
        available_fields = context.get("available_fields", [])
        print(f"\n📋 当前可用数据：{', '.join(available_fields) if available_fields else '无'}")

        # 检查依赖并显示不可用的零件
        missing_data = check_missing_data(selected_components, context)
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

    # ===== 阶段二 =====
    if "--components-file" in sys.argv:
        if len(sys.argv) < 3:
            print("错误: 阶段二需要指定输出文件路径")
            sys.exit(1)

        output_path = sys.argv[1]
        file_index = sys.argv.index("--components-file")
        components_file = sys.argv[file_index + 1]

        if not os.path.exists(components_file):
            print(f"错误: 零件选择文件不存在: {components_file}")
            print("请先运行阶段一生成该文件。")
            sys.exit(1)

        selected_components = load_selection(components_file)
        print(f"[Agent] 用户指定的零件列表: {selected_components}")

        visual_plan = await generate_visual_plan(context, "", selected_components)
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