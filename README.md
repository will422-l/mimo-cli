# mimo-cli

Official-style Xiaomi MiMo command-line interface for the **documented** public API surface.

`mimo-cli` is a practical open-source CLI for:

- text chat
- function/tool calling inspection
- built-in web search
- image understanding
- audio understanding
- video understanding
- speech synthesis (built-in voice)
- speech synthesis (voice design)
- speech synthesis (voice clone)

It also includes **reserved namespaces** for capabilities that appear in product/news materials but are **not yet documented as stable public API endpoints**. Those commands intentionally fail with a clear message instead of pretending support.

## Install

### From GitHub

```bash
pip install git+https://github.com/will422-l/mimo-cli.git
```

If GitHub git transport is unstable in your network, install from the branch archive instead:

```bash
pip install https://github.com/will422-l/mimo-cli/archive/refs/heads/main.zip
```

### Build from source

```bash
python3 -m pip install build
python3 -m build
```

### Local editable install

```bash
git clone https://github.com/will422-l/mimo-cli.git
cd mimo-cli
python3 -m pip install -e .
```

## Quick start

```bash
mimo auth login --api-key sk-xxxxx
mimo auth status
mimo doctor
mimo chat "What can Xiaomi MiMo do?"
```

## Command overview

### Auth & config

```bash
mimo auth login --api-key sk-xxxxx
mimo auth status
mimo auth logout

mimo config show
mimo config set default_text_model mimo-v2.5-pro
mimo config set base_url https://api.xiaomimimo.com
mimo config unset api_key
```

### Diagnostics

```bash
mimo doctor
mimo doctor --live
```

### Text chat

```bash
mimo chat "Explain MiMo briefly"
mimo text chat --message "user:Hello" --message "assistant:Hi" --message "user:Summarize tool calling"
mimo text chat --messages-file messages.json --output json
mimo chat "Stream this response" --stream
```

### Function tool calling

```bash
mimo tool-call "Check Beijing weather" --tools-file tools.json
mimo text tool-call "Check Beijing weather" --tools-file tools.json --thinking
```

> `--run` is currently reserved for a future local tool execution loop. Current releases inspect model tool calls but do not execute local functions yet.

### Web search

```bash
mimo web-search "Latest Xiaomi AI news" --forced
mimo search query "MiMo release notes"
```

### Vision / multimodal understanding

```bash
mimo image-understand ./demo.png "Describe the image"
mimo audio-understand ./demo.wav "Summarize the audio"
mimo video-understand ./demo.mp4 "Describe the video"

mimo vision image ./demo.png
mimo vision audio ./demo.wav "What is being said?"
mimo vision video ./demo.mp4 "Summarize the scene"
```

### Speech synthesis

```bash
mimo tts "Hello from MiMo" -o hello.wav
mimo tts "Happy birthday to you" --sing -o song.wav

mimo speech synthesize "Welcome to MiMo" -o welcome.wav
mimo speech voice-design "Young female voice, bright, fast-paced, suitable for tech news" "Today we launched new AI features." -o design.wav
mimo speech voice-clone ./voice_sample.wav "This is a cloned-voice demo." -o clone.wav
```

## Reserved future namespaces

These commands are intentionally present as stable UX placeholders, but they currently return a clear “not yet documented” error:

```bash
mimo image generate
mimo music generate
mimo speech transcribe
mimo gui
```

Why? Because Xiaomi MiMo public docs currently do **not** provide enough stable API detail for these capabilities, and this project prefers explicit placeholders over fake support.

## Documented capability map

### Explicitly documented in current MiMo public API docs

- `mimo-v2.5-pro` / `mimo-v2-pro` / `mimo-v2.5` / `mimo-v2-omni` / `mimo-v2-flash`
  - text generation
  - function calling
  - structured output
  - web search
- `mimo-v2.5` / `mimo-v2-omni`
  - image understanding
  - audio understanding
  - video understanding
- `mimo-v2.5-tts`
  - built-in voice TTS
  - style control
  - singing style
- `mimo-v2.5-tts-voicedesign`
  - voice design
- `mimo-v2.5-tts-voiceclone`
  - voice cloning
- `mimo-v2-tts`
  - older TTS model, still useful for singing style

### Reserved, not implemented until publicly documented

- image generation / text-to-image
- music generation / text-to-music
- standalone ASR API
- GUI / computer-use API

## Notes

- Local media files are automatically converted to data URLs for documented multimodal endpoints.
- Web search may require the plugin to be enabled on the Xiaomi MiMo platform side.
- Saved credentials are stored in `~/.config/mimo-cli/config.json` unless `MIMO_CONFIG_DIR` is set.

## License

MIT
