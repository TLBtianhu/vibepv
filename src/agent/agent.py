"""
VibePV Agent 主控脚本 (渐进式披露：AI 自主选择零件)
用法: python src/agent/agent.py <analysis.json路径> <输出JSON路径> --prompt "风格描述"
"""
import sys
import json
import asyncio
from pathlib import Path
from llm_client import call_llm
from tool_definitions import (
    TOOL_CATALOG,
    get_components_catalog,
    get_component_full_definitions,
    load_manifests
)


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

    audio_file = analysis["audio_file"]
    bpm = analysis["bpm"]["detected_bpm"]
    duration_ms = analysis["audio_duration_ms"]
    sentences_count = len(analysis["lyrics"]["sentences"])
    total_frames = int(duration_ms / 1000 * 30)

    lyrics_preview = " ".join(
        s["text"] for s in analysis["lyrics"]["sentences"][:5]
    ) if analysis["lyrics"]["sentences"] else "无歌词"

    # 2. 获取零件目录
    catalog = get_components_catalog()
    catalog_text = "\n".join(
        f"- {c['name']}: {c['description']}" for c in catalog
    )

    # 3. 第一阶段：让 AI 根据目录选择需要的零件
    system_msg_stage1 = f"""你是 VibePV 的 AI 视觉动效导演。
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

    messages = [
        {"role": "system", "content": system_msg_stage1},
        {"role": "user", "content": user_prompt},
    ]

    print("[Agent] 第一阶段：AI 选择零件...")
    response = await call_llm(messages, TOOL_CATALOG)
    choice = response["choices"][0]
    msg = choice["message"]

    if choice["finish_reason"] != "tool_calls":
        raise RuntimeError("AI 没有调用 request_component_details")

    # 提取请求的零件名称
    component_names = []
    for tool_call in msg.get("tool_calls", []):
        if tool_call["function"]["name"] == "request_component_details":
            args = json.loads(tool_call["function"]["arguments"])
            component_names = args.get("component_names", [])
            break

    if not component_names:
        raise RuntimeError("AI 没有选择任何零件")

    print(f"[Agent] AI 选择了 {len(component_names)} 个零件: {component_names}")

    # 4. 第二阶段：加载所选零件的详细参数描述，作为系统消息，只给 design_pv 工具
    manifests = load_manifests()
    component_details = []
    for name in component_names:
        if name in manifests:
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

    details_text = "\n\n".join(component_details)

    system_msg_stage2 = f"""现在你已获得所选零件的完整参数定义。

音频数据：
- BPM: {bpm}
- 总帧数(30fps): {total_frames}
- 歌词预览: {lyrics_preview}

所选零件及参数：
{details_text}

---
【强制格式要求】
你必须生成一个标准的 VisualPlan JSON，结构如下：
{{
  "metadata": {{ "style": "风格名", "description": "简短描述" }},
  "rules": [
    {{
      "effectId": "唯一标识",
      "type": "component",
      "layer": 0,
      "component": "零件名称",
      "params": {{ ... 该零件的参数 ... }},
      "timeline": {{ "start": 开始帧, "end": 结束帧 }}
    }}
  ]
}}
每个被选中的零件都必须作为 rules 数组中的一个独立元素出现，**严禁使用其他结构**。"""

    messages = [
        {"role": "system", "content": system_msg_stage2},
        {"role": "user", "content": user_prompt},
    ]

    # 第二阶段只提供 design_pv 工具
    design_pv_tool = [t for t in TOOL_CATALOG if t["function"]["name"] == "design_pv"]
    print(f"[Agent] 第二阶段：生成视觉计划... (工具: design_pv)")
    response = await call_llm(messages, design_pv_tool)
    choice = response["choices"][0]
    msg = choice["message"]

    # 5. 提取 design_pv 的结果
    if choice["finish_reason"] == "tool_calls":
        for tool_call in msg["tool_calls"]:
            if tool_call["function"]["name"] == "design_pv":
                args = json.loads(tool_call["function"]["arguments"])
                visual_plan_json = args.get("visual_plan_json", "{}")
                try:
                    visual_plan = json.loads(visual_plan_json)
                    print(f"[Agent] AI 生成的视觉计划: {json.dumps(visual_plan, ensure_ascii=False)}")
                except json.JSONDecodeError:
                    print(f"[Agent] visual_plan_json 解析失败: {visual_plan_json}")
                    visual_plan = None
                break
        else:
            raise RuntimeError("AI 没有调用 design_pv 工具")
    else:
        # 降级：尝试从 content 读取
        content = msg.get("content", "")
        try:
            visual_plan = json.loads(content)
            print("[Agent] 从 content 中提取到 JSON")
        except json.JSONDecodeError:
            raise RuntimeError(f"AI 未返回有效的视觉计划: {content}")

    if visual_plan is None:
        raise RuntimeError("未能生成有效的视觉计划")

    # 6. 保存
    result = {"visual_plan": visual_plan}
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"[Agent] 视觉计划已保存至 {output_path}")


if __name__ == "__main__":
    asyncio.run(run())