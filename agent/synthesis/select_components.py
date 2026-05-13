"""
VibePV 自动选零件
用法: python agent/synthesis/select_components.py --prompt "风格描述"
AI 选择零件后，直接写入 project_bundle.json，参数自动填入默认值。
"""
import sys
import json
import os
import asyncio
from agent.synthesis.component_selector import select_components
from agent.perception.analyzers.data_scanner import scan_data_sources
from agent.perception.analyzers.dependency_checker import check_missing_data
from agent.perception.components.manifest_loader import load_manifests

PROJECT_BUNDLE_PATH = "output/project_bundle.json"


def default_params_for(component_name):
    """根据 manifest.json 返回该零件的默认参数"""
    manifests = load_manifests()
    if component_name not in manifests:
        return {}
    meta = manifests[component_name]
    defaults = {}
    for key, info in meta.get("params", {}).items():
        if "default" in info:
            defaults[key] = info["default"]
    return defaults


def load_or_create_bundle():
    if os.path.exists(PROJECT_BUNDLE_PATH):
        with open(PROJECT_BUNDLE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "visual_plan": {"metadata": {"style": "", "description": ""}, "rules": []},
        "data_sources": {},
        "available_fields": [],
        "selected_components": [],
    }


def save_bundle(bundle):
    with open(PROJECT_BUNDLE_PATH, "w", encoding="utf-8") as f:
        json.dump(bundle, f, ensure_ascii=False, indent=2)
    print(f"[SelectComponents] 已保存至 {PROJECT_BUNDLE_PATH}")


async def run():
    if "--prompt" not in sys.argv:
        print("用法: python agent/synthesis/select_components.py --prompt '风格描述'")
        sys.exit(1)

    prompt_index = sys.argv.index("--prompt")
    user_prompt = " ".join(sys.argv[prompt_index + 1:])

    selected_components = await select_components(user_prompt)
    print(f"[SelectComponents] AI 选择了 {len(selected_components)} 个零件: {selected_components}")

    bundle = load_or_create_bundle()
    bundle["selected_components"] = selected_components
    bundle["visual_plan"]["metadata"]["style"] = user_prompt[:50]
    bundle["visual_plan"]["metadata"]["description"] = f"自动选择: {', '.join(selected_components)}"

    # 扫描当前可用数据源（仅用于打印提醒）
    adata = scan_data_sources()
    bundle["data_sources"] = adata.get("data_sources", {})
    bundle["available_fields"] = adata.get("available_fields", [])
    missing_data = check_missing_data(selected_components)

    print(f"\n📋 当前可用数据：{', '.join(adata.get('available_fields', [])) or '无'}")
    if missing_data:
        print("\nℹ️ 基于现有数据，以下零件不可用（缺少必要数据）：")
        for comp, fields in missing_data.items():
            print(f"  - {comp}（需要 {', '.join(fields)}）")
        print("\n💡 如需使用这些零件，请先运行对应的数据分析模块补齐数据。")
    else:
        print("\n✅ 所有选中的零件都有足够的可用数据。")

    # 为每个选中的零件创建默认参数规则
    existing_rules = bundle["visual_plan"].get("rules", [])
    existing_components = {r["component"] for r in existing_rules}
    for comp in selected_components:
        if comp not in existing_components:
            defaults = default_params_for(comp)
            existing_rules.append(
                {
                    "effectId": f"{comp.lower()}-default",
                    "type": "component",
                    "layer": 1,
                    "component": comp,
                    "params": defaults,
                    "timeline": {"start": 0, "end": 300},
                }
            )

    bundle["visual_plan"]["rules"] = existing_rules
    save_bundle(bundle)

    print("\n" + "=" * 50)
    print("自动选零件完成！project_bundle.json 已更新，所有参数使用默认值。")
    print("现在可以使用 fresh_generate 或 tune_generate 来调整参数。")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(run())