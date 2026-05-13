"""
VibePV 后端 API 服务
提供 /save 和 /generate 接口
"""
import json
import os
import shutil
import sys
import asyncio
from flask import Flask, request, jsonify

app = Flask(__name__)


@app.route('/save', methods=['POST'])
def save():
    """接收 project_bundle JSON，保存到 output 并同步 UI public"""
    data = request.get_json(force=True)
    output_path = "output/project_bundle.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    ui_dir = "renderers/vibe_ui/public"
    os.makedirs(ui_dir, exist_ok=True)
    ui_path = os.path.join(ui_dir, "project_bundle.json")
    shutil.copy2(output_path, ui_path)

    return jsonify({"status": "ok", "message": "已保存并同步"}), 200


@app.route('/generate', methods=['POST'])
def generate():
    """接收生成参数，根据请求调用 fresh 或 tune"""
    params = request.get_json(force=True) or {}
    prompt = params.get("prompt", "")
    mode = params.get("mode", "fresh")  # fresh 或 tune
    component_names = params.get("components", [])
    target_components = params.get("target_components", [])
    previous_plan = params.get("previous_plan", None)

    if mode == "tune" and target_components and previous_plan:
        from agent.synthesis.tune_generate import generate_visual_plan as gen
        asyncio.run(gen(prompt, component_names, target_components, previous_plan))
    else:
        from agent.synthesis.fresh_generate import generate_visual_plan as gen
        asyncio.run(gen(prompt, component_names))

    # 同步到 UI
    from agent.project_bundler import sync_to_ui
    sync_to_ui("output/project_bundle.json")

    return jsonify({"status": "ok", "message": "生成完成，已同步"}), 200


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=54321, debug=True)