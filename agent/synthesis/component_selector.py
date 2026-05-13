"""
VibePV 组件选择器
AI 根据风格描述选择需要的零件。
不感知任何数据源状态——只根据风格描述选零件。
"""
import json
import os
from agent.infra.llm_client import call_llm
from agent.perception.components.manifest_loader import load_manifests
from agent.synthesis.tools.selector_tools import SELECTOR_TOOLS


def get_components_catalog():
    """返回轻量级零件目录，包含每个零件的名称、描述和所需数据源"""
    manifests = load_manifests()
    catalog = []
    for name, meta in manifests.items():
        requires = meta.get("requires", {}).get("data", [])
        catalog.append(
            {
                "name": name,
                "description": meta.get("description", ""),
                "requires_data": requires,
            }
        )
    return catalog


def build_stage1_system_msg():
    """构建第一阶段系统消息，包含零件目录及各自所需数据源"""
    catalog = get_components_catalog()
    catalog_lines = []
    for c in catalog:
        line = f"- {c['name']}: {c['description']}"
        if c["requires_data"]:
            line += f" [需要数据: {', '.join(c['requires_data'])}]"
        catalog_lines.append(line)
    catalog_text = "\n".join(catalog_lines)

    return f"""你是 VibePV 的 AI 视觉动效导演。

可用视觉零件目录（含各自所需的数据源）：
{catalog_text}

请根据用户的风格描述，调用 request_component_details 工具，传入你认为需要的零件名称列表。
请根据风格描述自主判断需要哪些零件，不要包含与风格无关的零件。
注意：如果零件需要特定数据源，请确保你选择的零件组合是合理的。"""


def get_required_data_for_components(component_names):
    """返回所选零件各自依赖的数据源清单"""
    manifests = load_manifests()
    required_map = {}
    for name in component_names:
        if name in manifests:
            requires = manifests[name].get("requires", {}).get("data", [])
            required_map[name] = requires
    return required_map


async def select_components(user_prompt):
    """AI 根据风格描述选择需要的零件"""
    system_msg = build_stage1_system_msg()
    messages = [
        {"role": "system", "content": system_msg},
        {"role": "user", "content": user_prompt},
    ]

    print("[Agent] AI 选择零件...")
    response = await call_llm(messages, SELECTOR_TOOLS, model="deepseek-v4-pro")
    choice = response["choices"][0]
    msg = choice["message"]

    if choice["finish_reason"] != "tool_calls":
        raise RuntimeError("AI 没有调用 request_component_details")

    component_names = []
    for tool_call in msg.get("tool_calls", []):
        if tool_call["function"]["name"] == "request_component_details":
            args = json.loads(tool_call["function"]["arguments"])
            component_names = args.get("component_names", [])
            break

    if not component_names:
        raise RuntimeError("AI 没有选择任何零件")

    print(f"[Agent] AI 选择了 {len(component_names)} 个零件: {component_names}")

    # 列出所选零件各自需要的数据源
    required_data_map = get_required_data_for_components(component_names)
    print("\n📋 所选零件需要的数据源：")
    for comp, deps in required_data_map.items():
        if deps:
            print(f"  - {comp}: {', '.join(deps)}")
        else:
            print(f"  - {comp}: 无特殊依赖")

    return component_names