"""
VibePV 视觉计划生成器 (渐进式披露第二阶段)
根据用户确认的零件列表，生成完整的 VisualPlan JSON
"""
import json
from llm_client import call_llm
from tool_definitions import TOOL_CATALOG, load_manifests


def build_stage2_details(component_names):
    manifests = load_manifests()
    component_details = []

    for name in component_names:
        if name not in manifests:
            continue
        meta = manifests[name]
        params_desc = meta.get("params", {})
        param_lines = ["   params: {"]
        for pname, pinfo in params_desc.items():
            ptype = pinfo.get("type", "string")
            default = pinfo.get("default")
            pdesc = pinfo.get("description", "")
            line = f'     "{pname}": {ptype}'
            if default is not None:
                line += f", 默认={default}"
            if pdesc:
                line += f" - {pdesc}"
            param_lines.append(line)
        param_lines.append("   }")
        params_str = "\n".join(param_lines)
        component_details.append(f"- {name}: {meta.get('description', '')}\n{params_str}")

    return "\n\n".join(component_details)


def build_system_msg(analysis, component_names):
    bpm = analysis["bpm"]["detected_bpm"] if analysis.get("bpm") else "未知"
    duration_ms = analysis["audio_duration_ms"]
    total_frames = int(duration_ms / 1000 * 30)
    audio_file = analysis["audio_file"]

    has_lyrics = analysis.get("lyrics") is not None and analysis["lyrics"].get("sentences")
    if has_lyrics:
        lyrics_preview = " ".join(
            s["text"] for s in analysis["lyrics"]["sentences"][:5]
        )
        lyrics_info = f"- 歌词句子数: {len(analysis['lyrics']['sentences'])}\n- 歌词预览: {lyrics_preview}"
    else:
        lyrics_info = "- 歌词: 无（纯音乐/音MAD）"

    details_text = build_stage2_details(component_names)

    return f"""现在你已获得所选零件的完整参数定义。

音频数据：
- 音频文件名: {audio_file}
- BPM: {bpm}
- 总帧数(30fps): {total_frames}
{lyrics_info}

所选零件及参数：
{details_text}

---
【强制格式要求】
你必须生成一个标准的 VisualPlan JSON，结构如下：
{{{{
  "metadata": {{{{ "style": "风格名", "description": "简短描述" }}}},
  "rules": [
    {{{{
      "effectId": "唯一标识",
      "type": "component",
      "layer": 0,
      "component": "零件名称",
      "params": {{{{ ... 该零件的参数 ... }}}},
      "timeline": {{{{ "start": 开始帧, "end": 结束帧 }}}}
    }}}}
  ]
}}}}
每个被选中的零件都必须作为 rules 数组中的一个独立元素出现，**严禁使用其他结构**。

⚠️ 重要：所有需要音频文件的零件（如 CircularSpectrum）必须使用上述音频文件名 "{audio_file}"，严禁自己编造文件名。"""


async def generate_visual_plan(analysis, user_prompt, component_names, model=None):
    system_msg = build_system_msg(analysis, component_names)

    messages = [
        {"role": "system", "content": system_msg},
        {"role": "user", "content": user_prompt or "请根据音频数据和零件描述生成视觉计划"},
    ]

    design_pv_tool = [t for t in TOOL_CATALOG if t["function"]["name"] == "design_pv"]
    active_model = model or "deepseek-v4-pro"
    print(f"[Planner] 生成视觉计划... (模型: {active_model})")
    response = await call_llm(messages, design_pv_tool, model=active_model)
    choice = response["choices"][0]
    msg = choice["message"]

    if choice["finish_reason"] == "tool_calls":
        for tool_call in msg["tool_calls"]:
            if tool_call["function"]["name"] == "design_pv":
                args = json.loads(tool_call["function"]["arguments"])
                visual_plan_json = args.get("visual_plan_json", "{}")
                try:
                    visual_plan = json.loads(visual_plan_json)
                    return visual_plan
                except json.JSONDecodeError:
                    return None
        raise RuntimeError("AI 没有调用 design_pv 工具")
    else:
        content = msg.get("content", "")
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            raise RuntimeError(f"AI 未返回有效的视觉计划: {content}")