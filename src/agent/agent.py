"""
VibePV Agent 主控脚本 (方案B: VisualPlan 字符串参数)
用法: python src/agent/agent.py <analysis.json路径> <输出JSON路径> --prompt "风格描述"
"""
import sys
import json
import os
import asyncio
from pathlib import Path
from llm_client import call_llm
from tool_definitions import TOOLS


def load_component_meta(meta_dir=None):
    """扫描 component_meta/ 目录，返回所有零件元数据列表"""
    if meta_dir is None:
        # agent.py 在 src/agent/ 下，往上两层到项目根目录
        meta_dir = Path(__file__).resolve().parent.parent.parent / "component_meta"

    metas = []
    if not os.path.isdir(meta_dir):
        print(f"[Agent] 警告: 未找到组件元数据目录 {meta_dir}")
        return metas

    for fname in sorted(os.listdir(meta_dir)):
        if fname.endswith(".meta.json"):
            filepath = os.path.join(meta_dir, fname)
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    meta = json.load(f)
                    metas.append(meta)
            except json.JSONDecodeError:
                print(f"[Agent] 警告: 无法解析元数据文件 {filepath}")

    return metas


def build_component_description(metas):
    """根据元数据列表，生成 Agent 工具描述中的组件说明段落"""
    if not metas:
        return "（无可用组件）\n"

    lines = []
    for i, meta in enumerate(metas, 1):
        name = meta.get("name", "Unknown")
        desc = meta.get("description", "")
        params = meta.get("params", {})

        lines.append(f"{i}. {name} — {desc}")
        if params:
            lines.append("   params: {")
            for pname, pinfo in params.items():
                ptype = pinfo.get("type", "string")
                default = pinfo.get("default")
                pdesc = pinfo.get("description", "")

                param_str = f'     "{pname}": {ptype}'
                if default is not None:
                    param_str += f", 默认={default}"
                if pdesc:
                    param_str += f" — {pdesc}"
                lines.append(param_str)
            lines.append("   }")
        else:
            lines.append("   params: {}（无需额外参数）")
        lines.append("")

    return "\n".join(lines)


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

    # 2. 构建消息（调用 design_pv 工具，并动态加载组件描述）
    total_frames = int(duration_ms / 1000 * 30)

    # 动态加载组件元数据
    component_metas = load_component_meta()
    component_desc = build_component_description(component_metas)
    print(f"[Agent] 已加载 {len(component_metas)} 个组件的元数据")

    system_msg = f"""你是 VibePV 的 AI 视觉动效导演。
你会收到一首歌的音频分析数据：
- BPM: {bpm}
- 时长: {duration_ms}ms ({duration_ms/1000:.1f}秒)
- 歌词句子数: {sentences_count}
- 歌词预览: {lyrics_preview}
- 总帧数(30fps): {total_frames}

请调用 design_pv 工具，将完整的 VisualPlan 放在 visual_plan_json 字符串参数中。
确保 JSON 格式正确，timeline 的 start/end 在 0 到 {total_frames} 范围内。

可用组件（只使用以下列出的组件和参数名，严禁发明新字段）：

{component_desc}

设计原则：
1. 至少包含一个 AnimatedGradient 和一个 LyricsDisplay
2. 可以根据风格添加其他组件
3. 只使用上面列出的 params 字段名，严禁自己发明新字段名
4. 粒子总数不超过 120（可以分多层，每层不超过 80）
5. 根据 BPM 决定 timeline 的 start/end（30fps 计算总帧数）"""

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

    if visual_plan is None:
        raise RuntimeError("Agent 未能生成有效的视觉计划，请检查 API 连接或稍后重试")

    # 5. 保存为 {"visual_plan": {...}} 格式
    result = {"visual_plan": visual_plan}
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"[Agent] 视觉计划已保存至 {output_path}")

if __name__ == "__main__":
    asyncio.run(run())