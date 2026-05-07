"""
DeepSeek V4 API 客户端，支持 Function Calling (带重试与优化)
"""
import os
import asyncio
import httpx
from pathlib import Path

# ====== 手动读取项目根目录的 .env 文件，设置环境变量 ======
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

# 尝试读取密钥
api_key_value = load_api_key()
if api_key_value:
    os.environ["DEEPSEEK_API_KEY"] = api_key_value
else:
    print("[WARNING] DEEPSEEK_API_KEY not found in .env file")

DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

# ====== 全局配置：可在此调整 ======
MODEL_NAME = "deepseek-v4-pro"   # 官方推荐的 V4-Pro 模型名
MAX_TOKENS = 32768               # 限制输出长度，防止模型输出过长导致超时
REQUEST_TIMEOUT = 90.0          # 单次请求超时时间（秒）
MAX_RETRIES = 3                 # 最大重试次数
# =================================

async def call_llm(messages: list, tools: list | None = None) -> dict:
    """
    调用 DeepSeek V4 API，支持自动重试与指数退避。
    """
    if not DEEPSEEK_API_KEY:
        raise RuntimeError(
            "未设置 DEEPSEEK_API_KEY。请确保项目根目录下的 .env 文件存在，"
            "并且包含形如 DEEPSEEK_API_KEY=sk-xxx 的行（等号前后不要有空格）。"
        )

    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": MODEL_NAME,
        "messages": messages,
        "tools": tools,
        "stream": False,                # 必须关闭流式
        "max_tokens": MAX_TOKENS,       # 限制输出长度，防止过长 JSON 导致超时
        "tool_choice": "auto",          # 模型自行判断是否调用工具
    }

    print(f"[DEBUG] 模型: {payload['model']} | max_tokens: {MAX_TOKENS} | 工具数: {len(tools) if tools else 0}")

    last_exception = None
    for attempt in range(MAX_RETRIES):
        try:
            async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
                response = await client.post(DEEPSEEK_API_URL, json=payload, headers=headers)
                print(f"[DEBUG] HTTP 状态码: {response.status_code} (尝试 {attempt + 1}/{MAX_RETRIES})")
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            status_code = e.response.status_code
            print(f"[ERROR] HTTP {status_code}: {e.response.text}")
            # 4xx 错误不重试，直接抛出
            if 400 <= status_code < 500:
                raise
            last_exception = e
        except httpx.ReadTimeout:
            print(f"[WARNING] 请求超时 (尝试 {attempt + 1}/{MAX_RETRIES})")
            last_exception = httpx.ReadTimeout("请求超时")

        # 如果不是最后一次尝试，则指数退避后重试
        if attempt < MAX_RETRIES - 1:
            wait_time = 2 ** attempt  # 1s, 2s, 4s ...
            print(f"[INFO] 等待 {wait_time} 秒后重试...")
            await asyncio.sleep(wait_time)

    # 所有重试均失败
    raise last_exception