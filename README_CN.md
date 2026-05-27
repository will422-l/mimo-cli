# mimo-cli 中文文档

面向 Xiaomi MiMo 公开平台**已文档化能力**的命令行工具，但不伪造官方未开放接口。

当前支持：

- 文本对话
- 函数 / 工具调用结果查看
- 内置 Web Search
- 图像理解
- 音频理解
- 视频理解
- TTS 内置音色
- TTS 声音设计
- TTS 声音克隆

同时预留了未来扩展命名空间：图像生成、音乐生成、独立 ASR、GUI/computer-use。当前这些命令会返回明确的“尚未公开文档化”提示。

## 安装

```bash
pip install git+https://github.com/will422-l/mimo-cli.git
```

如果当前网络下 GitHub git 传输不稳定，也可以从分支压缩包安装：

```bash
pip install https://github.com/will422-l/mimo-cli/archive/refs/heads/main.zip
```

从源码构建：

```bash
python3 -m pip install build
python3 -m build
```

本地开发安装：

```bash
git clone https://github.com/will422-l/mimo-cli.git
cd mimo-cli
python3 -m pip install -e .
```

## 快速开始

```bash
mimo auth login --api-key sk-xxxxx
mimo auth status
mimo doctor
mimo chat "简单介绍一下 MiMo"
```

## 认证与配置

```bash
mimo auth login --api-key sk-xxxxx
mimo auth status
mimo auth logout

mimo config show
mimo config set default_text_model mimo-v2.5-pro
mimo config set base_url https://api.xiaomimimo.com
```

配置默认保存到：

```text
~/.config/mimo-cli/config.json
```

也可以通过环境变量覆盖：

```bash
export MIMO_API_KEY=sk-xxxxx
export MIMO_BASE_URL=https://api.xiaomimimo.com
export MIMO_CONFIG_DIR=/custom/config/dir
```

## 文本对话

```bash
mimo chat "解释一下工具调用"
mimo chat "流式输出这个回答" --stream
mimo text chat --message "user:你好" --message "assistant:你好" --message "user:继续解释"
mimo text chat --messages-file messages.json --output json
```

## 函数工具调用

```bash
mimo tool-call "帮我查一下北京天气" --tools-file tools.json
mimo text tool-call "帮我查一下北京天气" --tools-file tools.json --thinking
```

当前版本只查看模型返回的 `tool_calls`，不执行本地函数。`--run` 是预留给后续本地工具执行循环的接口。

## Web Search

```bash
mimo web-search "今天小米 AI 新闻" --forced
mimo search query "MiMo 最新更新"
```

注意：Web Search 可能需要在小米 MiMo 平台侧先开启插件。

## 多模态理解

```bash
mimo image-understand ./demo.png "描述图片内容"
mimo audio-understand ./demo.wav "总结音频内容"
mimo video-understand ./demo.mp4 "描述视频情节"

mimo vision image ./demo.png
mimo vision audio ./demo.wav "听到了什么？"
mimo vision video ./demo.mp4 "总结视频"
```

本地媒体文件会自动转为 data URL。

## 语音合成

```bash
mimo tts "你好，欢迎使用 MiMo" -o hello.wav
mimo tts "祝你生日快乐" --sing -o song.wav

mimo speech synthesize "欢迎使用 MiMo" -o welcome.wav
mimo speech voice-design "年轻女声，明亮，语速偏快，适合科技新闻播报" "今天发布了新的 AI 功能。" -o design.wav
mimo speech voice-clone ./voice_sample.wav "这是声音克隆测试。" -o clone.wav
```

## 预留命令

这些命令当前不会真正调用 API，而是返回清晰提示：

```bash
mimo image generate
mimo music generate
mimo speech transcribe
mimo gui
```

原因：目前公开 API 文档里还没有稳定接口说明。等官方文档或可验证接口出现后，可以直接在这些命名空间下补实现。

## 诊断

```bash
mimo doctor
mimo doctor --live
```

## License

MIT
