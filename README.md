# VibePV

AI 驱动的歌词可视化 PV 创作工具。输入一首歌 + 一句风格描述，AI 自动完成从音频分析到视觉动效设计的全流程，输出完整 MV。

## 核心理念

- **离线优先，云端增强**：核心音频分析本地运行，AI Agent 通过 API 调用云端大模型
- **数据驱动规则引擎**：AI 生成可执行的 VisualPlan JSON，宿主引擎逐帧渲染
- **工程文件开放**：project_bundle.json 为人可读、可分享、可二次开发
- **数据飞轮**：用户创作 → 数据沉淀 → 微调蒸馏模型 → 反哺社区

## 快速开始

```bash
# 1. 安装 Python 依赖
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 2. 下载本地 AI 模型
huggingface-cli download Qwen/Qwen3-ASR-0.6B --local-dir models/Qwen3-ASR-0.6B
huggingface-cli download Qwen/Qwen3-ForcedAligner-0.6B --local-dir models/Qwen3-ForcedAligner-0.6B

# 3. 安装渲染器依赖
cd renderers/host && npm install
cd ../vibe_ui && npm install && cd ../..

# 4. 配置 API Key
cp .env.example .env  # 编辑 .env 填入 DEEPSEEK_API_KEY

# 5. 分析音频 + AI 生成
python workspace/analyzers/audio_info/run.py test_audio/song.wav output/audio_info.json
python workspace/analyzers/bpm_detector/run.py test_audio/song.wav output/bpm.json
python agent/synthesis/select_components.py --prompt "温暖治愈风"

# 6. 启动 UI
cd renderers/vibe_ui && npm run dev