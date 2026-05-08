"""
VibePV Agent 主控脚本 (渐进式披露)
用法: python src/agent/agent.py <analysis.json路径> <输出JSON路径> --prompt "风格描述"
"""
import sys
import json
import asyncio
from llm_client import call_llm
from tool_definitions import TOOL_CATALOG, load_manifests
from component_selector import select_components


def build_stage2_details(component_names):
    """根据零件名称列表，构建详细参数描述文本"""
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


def build_stage2_system_msg(analysis, component_names):
    """构建第二阶段的系统消息"""
    bpm = analysis["bpm"]["detected_bpm"]
    duration_ms = analysis["audio_duration_ms"]
    total_frames = int(duration_ms / 1000 * 30)

    lyrics_preview = " ".join(
        s["text"] for s in analysis["lyrics"]["sentences"][:5]
    ) if analysis["lyrics"]["sentences"] else "无歌词"

    details_text = build_stage2_details(component_names)

    return f"""现在你已获得所选零件的完整参数定义。

音频数据：
- BPM: {bpm}
- 总帧数(30fps): {total_frames}
- 歌词预览: {lyrics_preview}

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
每个被选中的零件都必须作为 rules 数组中的一个独立元素出现，**严禁使用其他结构**。"""


async def generate_visual_plan(analysis, user_prompt, component_names):
    """
    第二阶段：加载所选零件的详细参数，调用 AI 生成 VisualPlan
    
    返回:
        dict: visual_plan 对象
    """
    system_msg = build_stage2_system_msg(analysis, component_names)

    messages = [
        {"role": "system", "content": system_msg},
        {"role": "user", "content": user_prompt},
    ]

    design_pv_tool = [t for t in TOOL_CATALOG if t["function"]["name"] == "design_pv"]
    print(f"[Agent] 第二阶段：生成视觉计划... (工具: design_pv)")
    response = await call_llm(messages, design_pv_tool)
    choice = response["choices"][0]
    msg = choice["message"]

    if choice["finish_reason"] == "tool_calls":
        for tool_call in msg["tool_calls"]:
            if tool_call["function"]["name"] == "design_pv":
                args = json.loads(tool_call["function"]["arguments"])
                visual_plan_json = args.get("visual_plan_json", "{}")
                try:
                    visual_plan = json.loads(visual_plan_json)
                    print(f"[Agent] AI 生成的视觉计划: {json.dumps(visual_plan, ensure_ascii=False)}")
                    return visual_plan
                except json.JSONDecodeError:
                    print(f"[Agent] visual_plan_json 解析失败: {visual_plan_json}")
                    return None
        raise RuntimeError("AI 没有调用 design_pv 工具")
    else:
        content = msg.get("content", "")
        try:
            visual_plan = json.loads(content)
            print("[Agent] 从 content 中提取到 JSON")
            return visual_plan
        except json.JSONDecodeError:
            raise RuntimeError(f"AI 未返回有效的视觉计划: {content}")


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

    # 2. 第一阶段：AI 选择零件
    component_names = await select_components(analysis, user_prompt)

    # 3. 第二阶段：生成完整视觉计划
    visual_plan = await generate_visual_plan(analysis, user_prompt, component_names)

    if visual_plan is None:
        raise RuntimeError("未能生成有效的视觉计划")

    # 4. 保存
    result = {"visual_plan": visual_plan}
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"[Agent] 视觉计划已保存至 {output_path}")


if __name__ == "__main__":
    asyncio.run(run())