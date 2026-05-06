"""
DeepSeek API 客户端，支持 Function Calling
"""
import os
import httpx
from pathlib import Path

def load_api_key():
    env_path = Path(__file__).resolve().parent.parent.parent / ".env"
    if not env_path.exists():
        print(f"[WARNING] .env file not found at {env_path}")
        return None
    with open(env_path, "r", encoding="utf-8-sig") as f:
        for raw_line in f:
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("DEEPSEEK_API_KEY"):
                key, _, value = line.partition("=")
                value = value.strip().strip('"').strip("'")
                return value if value else None
    return None

api_key_value = load_api_key()
if api_key_value:
    os.environ["DEEPSEEK_API_KEY"] = api_key_value
else:
    print("[WARNING] DEEPSEEK_API_KEY not found in .env file")

DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

async def call_llm(messages: list, tools: list | None = None) -> dict:
    if not DEEPSEEK_API_KEY:
        raise RuntimeError(
            "未设置 DEEPSEEK_API_KEY。请确保项目根目录下的 .env 文件存在，"
            "并且包含形如 DEEPSEEK_API_KEY=sk-xxx 的行。"
        )

    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "deepseek-chat",  # 强制使用可用模型
        "messages": messages,
        "tools": tools,
    }

    print(f"[DEBUG] 模型: {payload['model']}")
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(DEEPSEEK_API_URL, json=payload, headers=headers)
            print(f"[DEBUG] HTTP 状态码: {response.status_code}")
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        print(f"[ERROR] HTTP {e.response.status_code}: {e.response.text}")
        raise
    except httpx.ReadTimeout:
        print("[ERROR] 请求超时：60秒内未收到响应")
        raise