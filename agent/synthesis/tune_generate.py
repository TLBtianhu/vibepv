"""
增量视觉计划生成器
看已有参数 + 用户 Prompt，在当前基础上修改指定零件的参数。
"""
import json
from agent.infra.llm_client import call_llm
from agent.synthesis.tools.designer_tools import DESIGNER_TOOLS
from agent.perception.components.manifest_loader import load_manifests


def build_params_description(component_names):
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


def build_system_msg(component_names, target_effects, previous_plan):
    details_text = build_params_description(component_names)
    previous_rules = previous_plan.get("rules", [])
    previous_rules_str = json.dumps(previous_rules, ensure_ascii=False, indent=2)

    prompt = (
        "现在你已获得所选零件的完整参数定义。\n\n"
        "所选零件及当前参数：\n"
        f"{details_text}\n\n"
        "---\n"
        "【修改现有模式】\n"
        f"你只被要求更新以下组件对应的参数：{', '.join(target_effects)}。\n"
        "以下是这些组件当前的参数值，请在此基础上根据用户的调整描述进行修改。\n"
        "对于其他未指定的零件，你必须原样保留，不要做任何修改。\n"
        f"```json\n{previous_rules_str}\n```\n\n"
        "【强制格式要求】\n"
        "请生成完整的 visual_plan，只修改用户指定的零件参数，其余零件原样保留。\n"
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
    )
    return prompt


async def generate_visual_plan(user_prompt, component_names, target_effects, previous_plan, model=None):
    system_msg = build_system_msg(component_names, target_effects, previous_plan)
    messages = [
        {"role": "system", "content": system_msg},
        {"role": "user", "content": user_prompt},
    ]
    active_model = model or "deepseek-v4-pro"
    print(f"[TuneGenerate] 修改现有... (模型: {active_model})")
    response = await call_llm(messages, DESIGNER_TOOLS, model=active_model)
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

    previous_rules = previous_plan.get("rules", [])
    new_rules = new_plan.get("rules", [])
    merged_rules = {rule["effectId"]: rule for rule in previous_rules}
    for rule in new_rules:
        merged_rules[rule["effectId"]] = rule
    new_plan["rules"] = list(merged_rules.values())
    new_plan["metadata"] = new_plan.get("metadata", previous_plan.get("metadata", {}))
    return new_plan