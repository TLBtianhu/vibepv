"""
增量视觉计划生成器
只修改用户指定零件的参数，其余零件完全保持原样。
"""
import json
from llm_client import call_llm
from tool_definitions import TOOL_CATALOG
from services.manifest_loader import load_manifests


def build_stage2_details(component_names):
    """根据零件名称列表，构建详细参数描述文本"""
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


def build_system_msg(adata, target_components, previous_plan):
    """构建增量生成的系统消息"""
    audio_file = adata.get("audio_file", "")
    duration_ms = adata.get("audio_duration_ms", 0)
    total_frames = int(duration_ms / 1000 * 30) if duration_ms else 0
    available_fields = adata.get("available_fields", [])
    available_str = ", ".join(available_fields) if available_fields else "无"

    # 只展示目标零件的详细参数
    details_text = build_stage2_details(target_components)

    # 提取之前的规则，用于展示完整上下文
    previous_inner = previous_plan.get("visual_plan", previous_plan)
    previous_rules = previous_inner.get("rules", [])
    previous_rules_str = json.dumps(previous_rules, ensure_ascii=False, indent=2)

    prompt = (
        "现在你已获得需要调整的零件的完整参数定义。\n\n"
        "音频数据：\n"
        f"- 音频文件名: {audio_file}\n"
        f"- 总帧数(30fps): {total_frames}\n"
        f"- 可用数据字段: {available_str}\n\n"
        "需要调整的零件及参数：\n"
        f"{details_text}\n\n"
        "---\n"
        "【增量更新模式】\n"
        f"用户要求你只为以下零件生成新的参数：{', '.join(target_components)}。\n"
        "对于 previous_plan 中的其他零件，必须原样保留，不要做任何修改。\n"
        "以下是先前的完整视觉计划，供你参考上下文：\n"
        f"```json\n{previous_rules_str}\n```\n\n"
        "【强制格式要求】\n"
        "你的输出必须是一个完整的 VisualPlan JSON，其中 rules 数组包含 previous_plan 中的所有规则。\n"
        "你只需要修改上述指定零件的参数，其他规则直接复制，不得有任何改动。\n"
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


async def generate_visual_plan(adata, user_prompt, target_components, previous_plan, model=None):
    """调用 LLM 增量更新视觉计划"""
    system_msg = build_system_msg(adata, target_components, previous_plan)
    messages = [
        {"role": "system", "content": system_msg},
        {"role": "user", "content": user_prompt},
    ]

    design_pv_tool = [t for t in TOOL_CATALOG if t["function"]["name"] == "design_pv"]
    active_model = model or "deepseek-v4-pro"
    print(f"[Planner] 增量生成视觉计划... 模型: {active_model}")
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

    # 将新生成的规则合并到 previous_plan 中（只有用户指定的零件会被新规则替换）
    previous_inner = previous_plan.get("visual_plan", previous_plan)
    previous_rules = previous_inner.get("rules", [])
    new_rules = new_plan.get("rules", [])
    
    # 构建新规则的映射：component -> rule
    new_rule_by_component = {rule["component"]: rule for rule in new_rules}
    
    # 替换 previous_rules 中属于 target_components 的规则
    merged_rules = []
    for rule in previous_rules:
        if rule["component"] in target_components:
            # 如果新规则中有这个 component，使用新规则；否则保留原规则
            if rule["component"] in new_rule_by_component:
                merged_rules.append(new_rule_by_component[rule["component"]])
            else:
                merged_rules.append(rule)
        else:
            merged_rules.append(rule)
    
    # 如果 target_components 中有 previous_rules 里不存在的（新增零件），也加入
    for component_name in target_components:
        if component_name in new_rule_by_component:
            already_exists = any(r["component"] == component_name for r in previous_rules)
            if not already_exists:
                merged_rules.append(new_rule_by_component[component_name])

    new_plan["rules"] = merged_rules
    new_plan["metadata"] = new_plan.get("metadata", previous_inner.get("metadata", {}))

    return new_plan