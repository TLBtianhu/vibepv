"""
VibePV 保存 API 命令行工具
用法: python agent/server/save_api.py <project_bundle.json路径>
"""
import sys
import os
import shutil


def save_and_sync(source_path):
    if not os.path.exists(source_path):
        print(f"错误: 文件不存在: {source_path}")
        sys.exit(1)

    output_path = "output/project_bundle.json"
    os.makedirs("output", exist_ok=True)
    shutil.copy2(source_path, output_path)
    print(f"[SaveAPI] 已保存至 {output_path}")

    ui_dir = "renderers/vibe_ui/public"
    os.makedirs(ui_dir, exist_ok=True)
    ui_path = os.path.join(ui_dir, "project_bundle.json")
    shutil.copy2(output_path, ui_path)
    print(f"[SaveAPI] 已同步至 {ui_path}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("用法: python agent/server/save_api.py <project_bundle.json路径>")
        sys.exit(1)
    save_and_sync(sys.argv[1])