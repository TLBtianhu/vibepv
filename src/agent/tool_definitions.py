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
                '"layer": 整数, "component": "组件名", '
                '"params": {...}, "timeline": {"start": 开始帧, "end": 结束帧}}]}\n\n'
                "可用组件及其 params 字段（严格使用以下字段名，不要自己发明）：\n\n"
                "1. AnimatedGradient（渐变背景）\n"
                '   params: {"colors": ["#色1", "#色2", ...]}\n\n'
                "2. LyricsDisplay（歌词显示）\n"
                '   params: {}（无需额外参数）\n\n'
                "3. ParticleField（粒子场）\n"
                '   params: {\n'
                '     "particleCount": 整数(最大100),\n'
                '     "color": "#色值",\n'
                '     "colorSecondary": "#色值(可选)",\n'
                '     "sizeRange": [最小尺寸, 最大尺寸],\n'
                '     "speedRange": [最小速度, 最大速度],\n'
                '     "opacity": 0~1的小数\n'
                '   }\n'
                '   注意：color 和 colorSecondary 是单数形式，不要用复数 colors\n'
                '   注意：速度参数用 speedRange（数组），不要用 speed（单数）\n'
                '   注意：尺寸参数用 sizeRange（数组），不要用 size（单数）\n'
                '   注意：opacity 是单个数值，不是数组\n\n'
                "设计原则：\n"
                "1. 至少包含一个 AnimatedGradient 和一个 LyricsDisplay\n"
                "2. 可以根据风格添加 ParticleField\n"
                "3. 只使用上述列出的 params 字段名，严禁自己发明新字段名\n"
                "4. 粒子总数不超过 120（可以分多层，每层不超过 80）\n"
                "5. 根据 BPM 决定 timeline 的 start/end（30fps 计算总帧数）"
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