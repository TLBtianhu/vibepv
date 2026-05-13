"""
动态构建零件 Function Calling 工具定义
"""
from agent.perception.components.manifest_loader import load_manifests


def build_component_tool_definitions():
    """根据 manifest.json 自动生成完整的零件工具定义"""
    manifests = load_manifests()
    definitions = {}

    for component_name, meta in manifests.items():
        params_desc = meta.get("params", {})

        # 构建参数 Schema
        properties = {}
        for pname, pinfo in params_desc.items():
            prop = {
                "type": pinfo.get("type", "string"),
                "description": pinfo.get("description", ""),
            }
            if "default" in pinfo:
                prop["default"] = pinfo["default"]
            properties[pname] = prop

        tool_func_name = f"use_{component_name}"

        definitions[component_name] = {
            "type": "function",
            "function": {
                "name": tool_func_name,
                "description": f"{component_name}: {meta.get('description', '')}",
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": [],
                },
            },
        }

    return definitions