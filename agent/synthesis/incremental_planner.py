"""
增量视觉计划生成器
在已有视觉计划的基础上，只修改指定零件的参数，其余保持原样。
"""
import json
from llm_client import call_llm
from tool_definitions import TOOL_CATALOG
from perception.manifest_loader import load_manifests


def build_stage2_details(component_names):
    manifests = load_manifests()
    details = []
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
        details.append(f"- {name}: {meta.get('description', '')}\n{params_str}")
    return "\n\n".join(details)


def build_system_msg(adata, component_names, target_effects, previous_plan):
    audio_file = adata.get("audio_file", "")
    duration_ms = adata.get("audio_duration_ms", 0)
    total_frames = int(duration_ms / 1000 * 30) if duration_ms else 0
    available_fields = adata.get("available_fields", [])
    available_str = ", ".join(available_fields) if available_fields else "无"

    details_text = build_stage2_details(component_names)

    previous_inner = previous_plan.get("visual_plan", previous_plan)
    previous_rules = previous_inner.get("rules", [])
    previous_rules_str = json.dumps(previous_rules, ensure_ascii=False, indent=2)

    prompt = (
        "现在你已获得所选零件的完整参数定义。\n\n"
        "音频数据：\n"
        f"- 音频文件名: {audio_file}\n"
        f"- 总帧数(30fps): {total_frames}\n"
        f"- 可用数据字段: {available_str}\n\n"
        "所选零件及参数：\n"
        f"{details_text}\n\n"
        "---\n"
        "【增量更新模式】\n"
        f"你只被要求更新以下 effectId 对应的参数：{', '.join(target_effects)}。\n"
        "对于 previous_plan 中已存在的其他效果，你必须原样保留，不要做任何修改。\n"
        "以下是先前的视觉计划，供你参考：\n"
        f"```json\n{previous_rules_str}\n```\n\n"
        "【强制格式要求】\n"
        "请只修改上述指定的 effectId 的参数，其他规则完全不变，直接复制到新的 visual_plan 中。\n"
        "JSON 结构：\n"
        "{\n"
        '  "metadata": { "style": "风格名", "description": "简短描述" },\n'
        '  "rules": [\n'
        "    {\n"
        '      "effectId": "唯一标识",\n'
        '      "type": "component",\n'
        '      "layer": 0,\n'
        '      "component": "零件名称",\n'
        '      "params": { ... },\n'
        '      "timeline": { "start": 开始帧, "end": 结束帧 }\n'
        "    }\n"
        "  ]\n"
        "}\n"
        "每个被选中的零件都必须作为 rules 数组中的一个独立元素出现，严禁使用其他结构。\n"
        f'所有需要音频文件的零件（如 CircularSpectrum）必须使用上述音频文件名 "{audio_file}"。'
    )
    return prompt


async def generate_visual_plan(adata, user_prompt, component_names, target_effects, previous_plan, model=None):
    system_msg = build_system_msg(adata, component_names, target_effects, previous_plan)
    messages = [
        {"role": "system", "content": system_msg},
        {"role": "user", "content": user_prompt or "请根据音频数据和零件描述更新视觉计划"},
    ]

    design_pv_tool = [t for t in TOOL_CATALOG if t["function"]["name"] == "design_pv"]
    active_model = model or "deepseek-v4-pro"
    print(f"[Planner] 增量生成视觉计划... (模型: {active_model})")
    response = await call_llm(messages, design_pv_tool, model=active_model)
    choice = response["choices"][0]
    msg = choice["message"]

    new_plan = None
    if choice["finish_reason"] == "tool_calls":
        for tool_call in msg["tool_calls"]:
            if tool_call["function"]["name"] == "design_pv":
                args = json.loads(tool_call["function"]["arguments"])
                visual_plan_json = args.get("visual_plan_json", "{}")
                try:
                    new_plan = json.loads(visual_plan_json)
                except json.JSONDecodeError:
                    return None
                break
        if new_plan is None:
            raise RuntimeError("AI 没有调用 design_pv 工具")
    else:
        content = msg.get("content", "")
        try:
            new_plan = json.loads(content)
        except json.JSONDecodeError:
            raise RuntimeError(f"AI 未返回有效的视觉计划: {content}")

    previous_inner = previous_plan.get("visual_plan", previous_plan)
    previous_rules = previous_inner.get("rules", [])
    new_rules = new_plan.get("rules", [])
    merged_rules = {rule["effectId"]: rule for rule in previous_rules}
    for rule in new_rules:
        merged_rules[rule["effectId"]] = rule
    new_plan["rules"] = list(merged_rules.values())
    new_plan["metadata"] = new_plan.get("metadata", previous_inner.get("metadata", {}))

    return new_plan