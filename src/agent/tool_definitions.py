"""
VibePV Agent 工具定义
具体的组件列表由 services/manifest_loader.py 动态加载
"""
from services.manifest_loader import load_manifests

TOOL_CATALOG = [
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
    },
    {
        "type": "function",
        "function": {
            "name": "design_pv",
            "description": "当所有必需的视觉零件完整定义都已获得后，使用此工具生成或更新PV视觉计划。如果 target_effects 不为空，只更新指定效果的参数，其余规则保持原样。",
            "parameters": {
                "type": "object",
                "properties": {
                    "visual_plan_json": {
                        "type": "string",
                        "description": "JSON 字符串，包含 metadata 和 rules。"
                    },
                    "target_effects": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "（可选）如果提供，表示只为列表中的这些 effectId 生成或更新参数。如果为空或不提供，则按默认行为为所有选中的零件生成参数。"
                    }
                },
                "required": ["visual_plan_json"]
            }
        }
    }
]