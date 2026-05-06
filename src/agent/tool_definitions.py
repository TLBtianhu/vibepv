"""
VibePV Agent 工具定义 (方案B: 字符串参数绕过嵌套限制)
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
                '"layer": 0, "component": "组件名(AnimatedGradient/LyricsDisplay/ParticleField)", '
                '"params": {...}, "timeline": {"start": 0, "end": 帧数}}]}\n'
                "设计原则：\n"
                "1. 至少包含一个背景组件 (AnimatedGradient) 和一个歌词组件 (LyricsDisplay)\n"
                "2. 可根据风格添加 ParticleField\n"
                "3. 根据 BPM 决定 timeline 的 start/end（30fps 计算总帧数）\n"
                "4. 颜色方案要贴合用户描述的风格"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "visual_plan_json": {
                        "type": "string",
                        "description": "JSON 字符串，包含 metadata 和 rules，格式如上所述"
                    }
                },
                "required": ["visual_plan_json"]
            }
        }
    }
]