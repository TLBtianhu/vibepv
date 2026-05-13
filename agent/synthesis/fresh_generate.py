"""
全新生成视觉计划
不看已有参数，只根据零件名 + 用户 Prompt 生成全新参数。
"""
import json
from agent.infra.llm_client import call_llm
from agent.synthesis.tools.designer_tools import DESIGNER_TOOLS
from agent.perception.components.manifest_loader import load_manifests


def build_params_description(component_names):
    """根据零件名称列表，构建参数描述文本"""
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


def build_system_msg(component_names):
    details_text = build_params_description(component_names)
    return f"""现在你已获得所选零件的完整参数定义。

所选零件及参数：
{details_text}

---
【全新生成模式】
请根据用户的风格描述，为所有选中零件生成全新的参数。不参考任何已有参数值。

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


async def generate_visual_plan(user_prompt, component_names, model=None):
    system_msg = build_system_msg(component_names)
    messages = [
        {"role": "system", "content": system_msg},
        {"role": "user", "content": user_prompt},
    ]
    active_model = model or "deepseek-v4-pro"
    print(f"[FreshGenerate] 全新生成... (模型: {active_model})")
    response = await call_llm(messages, DESIGNER_TOOLS, model=active_model)
    choice = response["choices"][0]
    msg = choice["message"]

    if choice["finish_reason"] == "tool_calls":
        for tool_call in msg["tool_calls"]:
            if tool_call["function"]["name"] == "design_pv":
                args = json.loads(tool_call["function"]["arguments"])
                visual_plan_json = args.get("visual_plan_json", "{}")
                try:
                    return json.loads(visual_plan_json)
                except json.JSONDecodeError:
                    return None
        raise RuntimeError("AI 没有调用 design_pv 工具")
    else:
        content = msg.get("content", "")
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            raise RuntimeError(f"AI 未返回有效的视觉计划: {content}")