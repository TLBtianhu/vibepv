# 本地模型目录

此目录用于存放本地 AI 模型权重文件，不提交到 Git。

## 需要的模型

### Qwen3-ASR-0.6B
- 用途：歌词识别与时间戳对齐
- 下载地址：https://huggingface.co/Qwen/Qwen3-ASR-0.6B
- 存放路径：models/Qwen3-ASR-0.6B/

### Qwen3-ForcedAligner-0.6B
- 用途：强制对齐，生成逐字时间戳
- 下载地址：https://huggingface.co/Qwen/Qwen3-ForcedAligner-0.6B
- 存放路径：models/Qwen3-ForcedAligner-0.6B/

## 注意事项
- 模型文件较大（GB 级），请确保有足够硬盘空间
- 下载后无需额外配置，udio_pipeline.py 会自动加载
