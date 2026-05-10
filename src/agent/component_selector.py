"""
VibePV 组件选择器 (第一阶段)
"""
import json, os
from tool_definitions import TOOL_CATALOG, get_components_catalog
from llm_client import call_llm


def build_stage1_system_msg(adata):
    audio_file = adata["audio_file"]
    duration_ms = adata["audio_duration_ms"]
    total_frames = int(duration_ms / 1000 * 30)
    available_fields = adata.get("available_fields", [])

    lines = [
        f"- 音频文件名: {audio_file}",
        f"- BPM: {'有' if 'bpm' in available_fields else '无'}",
        f"- 时长: {duration_ms/1000:.1f}秒 ({total_frames} 帧)",
    ]
    if "lyrics.words" in available_fields:
        lines.append("- 歌词: 有")
    else:
        lines.append("- 歌词: 无（纯音乐/音MAD）")

    catalog = get_components_catalog()
    catalog_text = "\n".join(f"- {c['name']}: {c['description']}" for c in catalog)

    return f"""你是 VibePV 的 AI 视觉动效导演。
当前音频数据概况：
{chr(10).join(lines)}

可用视觉零件目录：
{catalog_text}

请根据用户的风格描述，调用 request_component_details 工具，传入你认为需要的零件名称列表。
你必须包含所有必要的零件（至少包含一个背景和一个歌词显示），但不要包含不需要的零件。
注意：如果歌词或 BPM 数据不可用，请不要选择任何依赖它们的零件。"""


async def select_components(adata, user_prompt):
    system_msg = build_stage1_system_msg(adata)
    messages = [
        {"role": "system", "content": system_msg},
        {"role": "user", "content": user_prompt},
    ]
    print("[Agent] 第一阶段：AI 选择零件...")
    response = await call_llm(messages, TOOL_CATALOG, model="deepseek-v4-pro")
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


def save_selection(component_names, adata, user_prompt, output_path="output/component_selection.json"):
    catalog = get_components_catalog()
    available = [c["name"] for c in catalog]
    selection = {
        "available_components": available,
        "selected_components": component_names,
        "style": user_prompt,
        "bpm": adata.get("bpm", None),
        "total_frames": int(adata["audio_duration_ms"] / 1000 * 30),
        "user_modified": False,
    }
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(selection, f, ensure_ascii=False, indent=2)
    print(f"[Selector] 零件选择结果已保存至 {output_path}")


def load_selection(filepath="output/component_selection.json"):
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)["selected_components"]