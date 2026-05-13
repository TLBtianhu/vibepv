"""
"选零件"工具定义
用于 component_selector 调用 LLM 选择零件
"""
SELECTOR_TOOLS = [
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
                        "description": "你需要的零件名称列表，例如 ['AnimatedGradient', 'ParticleField']",
                    }
                },
                "required": ["component_names"],
            },
        },
    }
]