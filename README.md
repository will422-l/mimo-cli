# mimo-cli

一键安装的 Xiaomi MiMo CLI 集合，按官方开放平台文档整理，覆盖当前**明确开放**的能力：

- 文本对话：`chat`
- 函数工具调用：`tool-call`
- 内置网络搜索：`web-search`
- 图像理解：`image-understand`
- 音频理解：`audio-understand`
- 视频理解：`video-understand`
- TTS（内置音色）：`tts`
- TTS（声音设计）：`tts-voice-design`
- TTS（声音克隆）：`tts-voice-clone`
- 能力清单：`models`

## 安装

```bash
cd /home/willlv/mimo-cli
python3 -m pip install -e .
```

## 环境变量

```bash
export MIMO_API_KEY="你的 key"
# 可选
export MIMO_BASE_URL="https://api.xiaomimimo.com"
export MIMO_TIMEOUT=300
```

## 快速示例

### 1) 基础聊天
```bash
mimo chat "用一句话解释 Transformer" --model mimo-v2.5-pro
```

### 2) 让模型输出 function tool call
先准备 `tools.json`：

```json
[
  {
    "type": "function",
    "function": {
      "name": "get_weather",
      "description": "Get weather by city",
      "parameters": {
        "type": "object",
        "properties": {
          "city": {"type": "string"}
        },
        "required": ["city"]
      }
    }
  }
]
```

调用：

```bash
mimo tool-call "帮我查一下北京天气" --tools-file tools.json
```

### 3) 内置网络搜索
```bash
mimo web-search "今天小米有哪些 AI 相关新闻？" --forced
```

### 4) 图像理解
```bash
mimo image-understand ./demo.png "描述图片内容并提取关键信息"
```

### 5) 音频理解
```bash
mimo audio-understand ./demo.wav "总结这段音频内容"
```

### 6) 视频理解
```bash
mimo video-understand ./demo.mp4 "描述视频主要情节"
```

### 7) 内置音色 TTS
```bash
mimo tts "你好，欢迎使用 MiMo" -o hello.wav --voice mimo_default
```

### 8) 声音设计 TTS
```bash
mimo tts-voice-design "年轻女声，明亮，语速偏快，适合播报科技新闻" "今天发布会带来了多项 AI 新能力。" -o design.wav
```

### 9) 声音克隆 TTS
```bash
mimo tts-voice-clone ./voice_sample.wav "这是克隆音色测试。" -o clone.wav
```

## 官方文档核对后的能力范围

### 已明确开放
- `mimo-v2.5-pro` / `mimo-v2-pro` / `mimo-v2.5` / `mimo-v2-omni` / `mimo-v2-flash`
  - 文本生成
  - Function Call
  - Structured Output
  - Web Search（需平台侧启用插件）
- `mimo-v2.5` / `mimo-v2-omni`
  - 图像理解
  - 音频理解
  - 视频理解
- `mimo-v2.5-tts`
  - 内置音色 TTS
  - 风格控制
  - 唱歌风格
- `mimo-v2.5-tts-voicedesign`
  - 自然语言定义新音色
- `mimo-v2.5-tts-voiceclone`
  - 上传音频样本做音色克隆
- `mimo-v2-tts`
  - 旧版 TTS，支持唱歌风格

### 文档里未看到正式 API 的能力
以下能力在这次抓取到的**官方 API 文档**里没有看到正式可调用接口，因此本 CLI 暂不伪造实现：

- 文生图 / 图像生成
- 文生音乐 / 通用音乐生成
- 独立 ASR HTTP API 文档
- GUI / computer-use / browser 操作 API 细节

如果后续你要，我可以继续做第二阶段：
1. 再深入抓 MiMo 平台控制台前端接口，确认是否有未公开到文档页的能力；
2. 把这个 CLI 扩成完整发布版（发布到 Git、本地全局安装、补流式输出、补自动保存 JSON/音频）。
