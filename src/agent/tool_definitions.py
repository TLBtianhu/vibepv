"""
VibePV Agent 工具定义 (渐进式披露双层结构)
第一层：请求零件详情 + 设计PV
第二层：各个零件的完整参数定义（按需加载）
"""
import json
import os
from pathlib import Path

# ==================== 通用工具目录 ====================
TOOL_CATALOG = [
    {
        "type": "function",
        "function": {
            "name": "request_component_details",
            "description": "当你确定需要哪些视觉零件后，调用此工具请求它们的完整参数定义。请传入零件名称列表。",
            "parameters": {
                "type": "object",
                "properties": {
                    "component_names": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "你需要的零件名称列表，例如 ['AnimatedGradient', 'ParticleField']"
                    }
                },
                "required": ["component_names"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "design_pv",
            "description": "当所有必需的视觉零件完整定义都已获得后，使用此工具生成最终的PV视觉计划。",
            "parameters": {
                "type": "object",
                "properties": {
                    "visual_plan_json": {
                        "type": "string",
                        "description": "JSON 字符串，包含 metadata 和 rules"
                    }
                },
                "required": ["visual_plan_json"]
            }
        }
    }
]

# ==================== 零件目录加载 ====================

def load_manifests(meta_dir=None):
    if meta_dir is None:
        # 路径已更新：components 已上提到 src/renderer/components
        meta_dir = Path(__file__).resolve().parent.parent / "renderer" / "components"
    
    manifests = {}
    if not os.path.isdir(meta_dir):
        print(f"[ToolDef] 警告: 未找到组件目录 {meta_dir}")
        return manifests
    
    for folder in sorted(os.listdir(meta_dir)):
        folder_path = os.path.join(meta_dir, folder)
        if not os.path.isdir(folder_path):
            continue
        manifest_path = os.path.join(folder_path, "manifest.json")
        if os.path.isfile(manifest_path):
            try:
                with open(manifest_path, "r", encoding="utf-8") as f:
                    meta = json.load(f)
                    name = meta.get("name", folder)
                    manifests[name] = meta
            except json.JSONDecodeError:
                print(f"[ToolDef] 警告: 无法解析 manifest 文件 {manifest_path}")
    
    return manifests


def get_components_catalog():
    """返回零件目录列表，每个元素是 {name, description}，用于 AI 初步筛选"""
    manifests = load_manifests()
    catalog = []
    for name, meta in manifests.items():
        catalog.append({
            "name": name,
            "description": meta.get("description", "")
        })
    return catalog


def build_component_full_tool(name, meta):
    """根据 manifest 构建单个零件的完整 Function Calling 工具定义"""
    params_desc = meta.get("params", {})
    properties = {}
    for pname, pinfo in params_desc.items():
        prop = {
            "type": pinfo.get("type", "string"),
            "description": pinfo.get("description", "")
        }
        if "default" in pinfo:
            prop["default"] = pinfo["default"]
        properties[pname] = prop
    
    return {
        "type": "function",
        "function": {
            "name": f"use_{name}",
            "description": f"{name}: {meta.get('description', '')}. 参数: {json.dumps(params_desc, ensure_ascii=False)}",
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": []
            }
        }
    }


def get_component_full_definitions(component_names):
    """根据零件名称列表返回对应的完整工具定义列表"""
    manifests = load_manifests()
    full_tools = []
    for name in component_names:
        if name in manifests:
            full_tools.append(build_component_full_tool(name, manifests[name]))
        else:
            print(f"[ToolDef] 警告: 未知零件 {name}")
    return full_tools