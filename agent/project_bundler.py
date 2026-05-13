"""
VibePV 工程文件同步工具
将 output/project_bundle.json 拷贝到 renderers/vibe_ui/public/
"""
import os
import shutil

SOURCE = "output/project_bundle.json"
UI_PUBLIC = "renderers/vibe_ui/public"


def sync_to_ui(source_path=None, output_dir=None):
    src = source_path or SOURCE
    dest_dir = output_dir or UI_PUBLIC

    if not os.path.exists(src):
        print(f"[Bundler] 警告: {src} 不存在，跳过同步")
        return False

    os.makedirs(dest_dir, exist_ok=True)
    dest = os.path.join(dest_dir, os.path.basename(src))
    if os.path.exists(dest):
        src_mtime = os.path.getmtime(src)
        dest_mtime = os.path.getmtime(dest)
        if src_mtime <= dest_mtime:
            return False

    shutil.copy2(src, dest)
    print(f"[Bundler] 已同步 {src} -> {dest}")
    return True


if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("用法: python agent/project_bundler.py <project_bundle.json路径>")
        sys.exit(1)
    sync_to_ui(sys.argv[1])