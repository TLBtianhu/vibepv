"""
VibePV Agent 工具定义 (方案B: 字符串参数绕过嵌套限制)
具体的组件列表由 agent.py 运行时从 component_meta/ 动态加载
"""
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "design_pv",
            "description": (
                "设计 PV 的完整视觉计划。\n"
                "参数 visual_plan_json 是一个 JSON 字符串，结构如下：\n"
                '{"metadata": {"style": "风格名", "description": "描述"}, '
                '"rules": [{"effectId": "唯一ID", "type": "component或custom", '
                '"layer": 整数, "component": "组件名", '
                '"params": {...}, "timeline": {"start": 开始帧, "end": 结束帧}}]}\n\n'
                "可用组件列表已在 system prompt 中提供，请严格按照其中定义的组件名和参数名填写。"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "visual_plan_json": {
                        "type": "string",
                        "description": "JSON 字符串，包含 metadata 和 rules"
                    }
                },
                "required": ["visual_plan_json"]
            }
        }
    }
]