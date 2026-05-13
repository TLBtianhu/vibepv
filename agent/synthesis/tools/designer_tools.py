"""
"调参数"工具定义
用于 fresh_generate 和 tune_generate 调用 LLM 生成/修改参数
"""
DESIGNER_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "design_pv",
            "description": "当所有必需的视觉零件完整定义都已获得后，使用此工具生成最终的PV视觉计划。",
            "parameters": {
                "type": "object",
                "properties": {
                    "visual_plan_json": {
                        "type": "string",
                        "description": "JSON 字符串，包含 metadata 和 rules",
                    }
                },
                "required": ["visual_plan_json"],
            },
        },
    }
]