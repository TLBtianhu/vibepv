"""
VibePV 组件选择器 (渐进式披露第一阶段)
让 AI 从零件目录中选择当前风格所需的零件
"""
import json
from pathlib import Path
from tool_definitions import TOOL_CATALOG, get_components_catalog
from llm_client import call_llm


def build_stage1_system_msg(analysis):
    """构建第一阶段的系统消息"""
    audio_file = analysis["audio_file"]
    bpm = analysis["bpm"]["detected_bpm"]
    duration_ms = analysis["audio_duration_ms"]
    sentences_count = len(analysis["lyrics"]["sentences"])
    total_frames = int(duration_ms / 1000 * 30)

    lyrics_preview = " ".join(
        s["text"] for s in analysis["lyrics"]["sentences"][:5]
    ) if analysis["lyrics"]["sentences"] else "无歌词"

    catalog = get_components_catalog()
    catalog_text = "\n".join(
        f"- {c['name']}: {c['description']}" for c in catalog
    )

    return f"""你是 VibePV 的 AI 视觉动效导演。
音频分析数据：
- 音频文件名: {audio_file}
- BPM: {bpm}
- 时长: {duration_ms/1000:.1f}秒 ({total_frames} 帧)
- 歌词句子数: {sentences_count}
- 歌词预览: {lyrics_preview}

可用的视觉零件目录如下：
{catalog_text}

请根据用户的风格描述，调用 request_component_details 工具，传入你认为需要的零件名称列表。
你应该包含所有必要的零件（至少包含一个背景和一个歌词显示），但不要包含不需要的零件。"""


async def select_components(analysis, user_prompt):
    """
    第一阶段：AI 根据风格描述选择需要的零件
    
    返回:
        list[str]: AI 选择的零件名称列表
    """
    system_msg = build_stage1_system_msg(analysis)

    messages = [
        {"role": "system", "content": system_msg},
        {"role": "user", "content": user_prompt},
    ]

    print("[Agent] 第一阶段：AI 选择零件...")
    response = await call_llm(messages, TOOL_CATALOG)
    choice = response["choices"][0]
    msg = choice["message"]

    if choice["finish_reason"] != "tool_calls":
        raise RuntimeError("AI 没有调用 request_component_details")

    component_names = []
    for tool_call in msg.get("tool_calls", []):
        if tool_call["function"]["name"] == "request_component_details":
            args = json.loads(tool_call["function"]["arguments"])
            component_names = args.get("component_names", [])
            break

    if not component_names:
        raise RuntimeError("AI 没有选择任何零件")

    print(f"[Agent] AI 选择了 {len(component_names)} 个零件: {component_names}")
    return component_names