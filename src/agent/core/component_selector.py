"""
VibePV 组件选择器 (渐进式披露第一阶段)
让 AI 从零件目录中选择当前风格所需的零件。
不扫描已有数据源——只负责选零件并列出所选零件依赖的数据源清单。
"""
import json
import os
from llm_client import call_llm
from services.manifest_loader import load_manifests

# 第一阶段独立的工具定义
STAGE1_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "request_component_details",
            "description": "当你确定需要哪些视觉零件后，调用此工具请求它们的完整参数定义。请传入零件名称列表。",
            "parameters": {
                "type": "object",
                "properties": {
                    "component_names": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "你需要的零件名称列表"
                    }
                },
                "required": ["component_names"]
            }
        }
    }
]


def get_components_catalog():
    """返回轻量级零件目录，包含每个零件的名称、描述和所需数据源"""
    manifests = load_manifests()
    catalog = []
    for name, meta in manifests.items():
        requires = meta.get("requires", {}).get("data", [])
        catalog.append({
            "name": name,
            "description": meta.get("description", ""),
            "requires_data": requires,
        })
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
请根据风格描述自主判断需要哪些零件，不要包含与风格无关的零件。"""


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
    """第一阶段：AI 根据风格描述选择需要的零件"""
    system_msg = build_stage1_system_msg()
    messages = [
        {"role": "system", "content": system_msg},
        {"role": "user", "content": user_prompt},
    ]

    print("[Agent] 第一阶段：AI 选择零件...")
    response = await call_llm(messages, STAGE1_TOOLS, model="deepseek-v4-pro")
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


def save_selection(component_names, user_prompt, output_path="output/component_selection.json"):
    """保存零件选择结果到中间文件，供用户审核和修改"""
    catalog = get_components_catalog()
    available = [c["name"] for c in catalog]

    selection = {
        "available_components": available,
        "selected_components": component_names,
        "style": user_prompt,
        "user_modified": False,
    }
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(selection, f, ensure_ascii=False, indent=2)

    print(f"[Selector] 零件选择结果已保存至 {output_path}")


def load_selection(filepath="output/component_selection.json"):
    """从中间文件加载用户确认的零件列表"""
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)["selected_components"]