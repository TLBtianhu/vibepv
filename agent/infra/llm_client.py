"""
DeepSeek V4 API 客户端，支持 Function Calling (带重试与精细化超时)
"""
import os
import asyncio
import httpx
from pathlib import Path

def load_api_key():
    """健壮地读取 .env 文件中的 API Key"""
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

MODEL_NAME = "deepseek-v4-pro"
MAX_TOKENS = 32768
MAX_RETRIES = 3

DEEPSEEK_TIMEOUT = httpx.Timeout(
    connect=10.0,
    read=300.0,
    write=10.0,
    pool=10.0,
)

async def call_llm(messages: list, tools: list | None = None, model: str | None = None) -> dict:
    if not DEEPSEEK_API_KEY:
        raise RuntimeError("未设置 DEEPSEEK_API_KEY。")

    active_model = model or MODEL_NAME

    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": active_model,
        "messages": messages,
        "tools": tools,
        "stream": False,
        "max_tokens": MAX_TOKENS,
        "tool_choice": "auto",
    }

    print(f"[DEBUG] 模型: {payload['model']} | max_tokens: {MAX_TOKENS} | 工具数: {len(tools) if tools else 0}")

    last_exception = None
    for attempt in range(MAX_RETRIES):
        try:
            async with httpx.AsyncClient(timeout=DEEPSEEK_TIMEOUT) as client:
                response = await client.post(DEEPSEEK_API_URL, json=payload, headers=headers)
                print(f"[DEBUG] HTTP 状态码: {response.status_code} (尝试 {attempt + 1}/{MAX_RETRIES})")
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            status_code = e.response.status_code
            print(f"[ERROR] HTTP {status_code}: {e.response.text}")
            if 400 <= status_code < 500:
                raise
            last_exception = e
        except httpx.TimeoutException:
            print(f"[WARNING] 请求超时 (尝试 {attempt + 1}/{MAX_RETRIES})")
            last_exception = httpx.TimeoutException("请求超时")
        except Exception as e:
            print(f"[WARNING] 请求出错 (尝试 {attempt + 1}/{MAX_RETRIES}): {e}")
            last_exception = e

        if attempt < MAX_RETRIES - 1:
            wait_time = 2 ** attempt
            print(f"[INFO] 等待 {wait_time} 秒后重试...")
            await asyncio.sleep(wait_time)

    raise last_exception