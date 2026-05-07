"""
VibePV Agent 主控脚本 (方案B: VisualPlan 字符串参数)
用法: python src/agent/agent.py <analysis.json路径> <输出JSON路径> --prompt "风格描述"
"""
import sys
import json
import asyncio
from llm_client import call_llm
from tool_definitions import TOOLS

async def run():
    if len(sys.argv) < 5 or "--prompt" not in sys.argv:
        print("用法: python src/agent/agent.py <analysis.json路径> <输出JSON路径> --prompt '风格描述'")
        sys.exit(1)

    analysis_path = sys.argv[1]
    output_path = sys.argv[2]
    prompt_index = sys.argv.index("--prompt")
    user_prompt = " ".join(sys.argv[prompt_index + 1:])

    # 1. 读取分析数据
    with open(analysis_path, "r", encoding="utf-8") as f:
        analysis = json.load(f)

    bpm = analysis["bpm"]["detected_bpm"]
    duration_ms = analysis["audio_duration_ms"]
    sentences_count = len(analysis["lyrics"]["sentences"])

    lyrics_preview = " ".join(
        s["text"] for s in analysis["lyrics"]["sentences"][:5]
    ) if analysis["lyrics"]["sentences"] else "无歌词"

    # 2. 构建消息（调用 design_pv 工具，并添加严格约束）
    total_frames = int(duration_ms / 1000 * 30)
    system_msg = f"""你是 VibePV 的 AI 视觉动效导演。
你会收到一首歌的音频分析数据：
- BPM: {bpm}
- 时长: {duration_ms}ms ({duration_ms/1000:.1f}秒)
- 歌词句子数: {sentences_count}
- 歌词预览: {lyrics_preview}
- 总帧数(30fps): {total_frames}

请调用 design_pv 工具，将完整的 VisualPlan 放在 visual_plan_json 字符串参数中。
确保 JSON 格式正确，timeline 的 start/end 在 0 到 {total_frames} 范围内。

⚠️ 严格约束：只使用 tool_definitions.py 中列出的组件和参数名，不要自己发明任何字段名。
- ParticleField 的颜色参数是 color（单数）和 colorSecondary（单数），不要使用 colors（复数数组）或 particleColor 等自创名称。
- 速度参数必须用 speedRange（数组 [最小速度, 最大速度]），不要使用 speed（单数）。
- 尺寸参数必须用 sizeRange（数组 [最小尺寸, 最大尺寸]），不要使用 size（单数）。
- opacity 是单个小数（0~1），不要写成数组。
- 粒子总数不超过 120（每层不超过 80）。
- LyricsDisplay 不需要额外 params，不要给它加任何参数。
- 全部参数名只能使用 tool_definitions.py 中明确列出的字段，切勿自己发明。"""

    messages = [
        {"role": "system", "content": system_msg},
        {"role": "user", "content": user_prompt},
    ]

    # 3. 调用 LLM
    print(f"[Agent] 正在向 DeepSeek 请求视觉计划...")
    response = await call_llm(messages, TOOLS)
    choice = response["choices"][0]
    finish_reason = choice["finish_reason"]
    msg = choice["message"]

    # 4. 处理返回结果
    if finish_reason == "tool_calls":
        tool_call = msg["tool_calls"][0]
        args = json.loads(tool_call["function"]["arguments"])
        visual_plan_json = args.get("visual_plan_json", "{}")
        try:
            visual_plan = json.loads(visual_plan_json)
            print(f"[Agent] AI 生成的视觉计划: {json.dumps(visual_plan, ensure_ascii=False)}")
        except json.JSONDecodeError:
            print(f"[Agent] visual_plan_json 解析失败，使用默认计划。内容: {visual_plan_json}")
            visual_plan = None
    else:
        content = msg.get("content", "")
        try:
            visual_plan = json.loads(content)
            print(f"[Agent] 模型直接返回 JSON (未通过工具调用)")
        except json.JSONDecodeError:
            print(f"[Agent] 模型未返回有效 JSON，使用默认计划。原始内容: {content}")
            visual_plan = None

    # 降级方案
    if visual_plan is None:
        visual_plan = {
            "metadata": {"style": "default", "description": "默认视觉计划"},
            "rules": [
                {
                    "effectId": "bg_default",
                    "type": "component",
                    "layer": 0,
                    "component": "AnimatedGradient",
                    "params": {"colors": ["#0a0a2a", "#ff00ff", "#00ffff"]},
                    "timeline": {"start": 0, "end": total_frames}
                },
                {
                    "effectId": "lyrics_default",
                    "type": "component",
                    "layer": 1,
                    "component": "LyricsDisplay",
                    "params": {},
                    "timeline": {"start": 0, "end": total_frames}
                }
            ]
        }

    # 5. 保存为 {"visual_plan": {...}} 格式
    result = {"visual_plan": visual_plan}
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"[Agent] 视觉计划已保存至 {output_path}")

if __name__ == "__main__":
    asyncio.run(run())