"""
VibePV 文件监听 + WebSocket 推送服务
监听 output/project_bundle.json 的变化，自动同步到 UI public/，
并通过 WebSocket 通知前端刷新。
"""
import asyncio
import os
import shutil
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import websockets

WATCH_FILE = "output/project_bundle.json"
UI_PUBLIC_DIR = "renderers/vibe_ui/public"
WEBSOCKET_HOST = "localhost"
WEBSOCKET_PORT = 54322

connected_clients = set()


class ProjectBundleHandler(FileSystemEventHandler):
    def __init__(self):
        self.last_sync_time = 0

    def on_modified(self, event):
        if not event.is_directory and event.src_path.endswith("project_bundle.json"):
            now = time.time()
            if now - self.last_sync_time < 0.5:
                return
            self.last_sync_time = now

            print(f"[Watcher] 检测到 project_bundle.json 已修改")

            if os.path.exists(WATCH_FILE):
                os.makedirs(UI_PUBLIC_DIR, exist_ok=True)
                dest = os.path.join(UI_PUBLIC_DIR, "project_bundle.json")
                shutil.copy2(WATCH_FILE, dest)
                print(f"[Watcher] 已同步到 {dest}")

            asyncio.run_coroutine_threadsafe(broadcast_refresh(), loop)


async def broadcast_refresh():
    if not connected_clients:
        return
    message = "refresh"
    disconnected = set()
    for ws in connected_clients:
        try:
            await ws.send(message)
        except websockets.ConnectionClosed:
            disconnected.add(ws)
    connected_clients.difference_update(disconnected)


async def handle_client(websocket):
    connected_clients.add(websocket)
    print(f"[WebSocket] 客户端已连接 (当前 {len(connected_clients)} 个)")
    try:
        async for _ in websocket:
            pass
    except websockets.ConnectionClosed:
        pass
    finally:
        connected_clients.discard(websocket)
        print(f"[WebSocket] 客户端已断开 (当前 {len(connected_clients)} 个)")


async def start_websocket_server():
    print(f"[WebSocket] 正在启动 ws://{WEBSOCKET_HOST}:{WEBSOCKET_PORT}")
    async with websockets.serve(handle_client, WEBSOCKET_HOST, WEBSOCKET_PORT):
        await asyncio.Future()


def start_file_watcher():
    watch_dir = os.path.dirname(WATCH_FILE)
    os.makedirs(watch_dir, exist_ok=True)
    if not os.path.exists(WATCH_FILE):
        with open(WATCH_FILE, "w", encoding="utf-8") as f:
            json.dump({}, f)

    handler = ProjectBundleHandler()
    observer = Observer()
    observer.schedule(handler, watch_dir, recursive=False)
    observer.start()
    print(f"[Watcher] 正在监听 {WATCH_FILE}")
    return observer


async def main():
    global loop
    loop = asyncio.get_running_loop()
    observer = start_file_watcher()
    try:
        await start_websocket_server()
    finally:
        observer.stop()
        observer.join()


if __name__ == "__main__":
    import json
    asyncio.run(main())