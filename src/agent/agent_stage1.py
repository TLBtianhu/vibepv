"""
VibePV Agent 阶段一：零件选择
用法: python src/agent/agent_stage1.py --prompt '风格描述'
生成 output/component_selection.json 后停止，请审核该文件。
"""
import sys
import asyncio
from services.data_scanner import scan_data_sources
from core.component_selector import select_components, save_selection
from services.dependency_checker import check_missing_data


async def run():
    if "--prompt" not in sys.argv:
        print("用法: python src/agent/agent_stage1.py --prompt '风格描述'")
        sys.exit(1)

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
    print("  python src/agent/agent_stage2.py <输出JSON路径> --components-file output/component_selection.json")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(run())