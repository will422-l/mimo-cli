# Errors and Troubleshooting

## `Missing API key`

Run:

```bash
mimo auth login --api-key sk-xxxxx
```

Or set:

```bash
export MIMO_API_KEY=sk-xxxxx
```

## Web search does not happen

MiMo web search is model/tool-choice dependent and may require the Web Search plugin to be enabled in the Xiaomi MiMo platform console. Try:

```bash
mimo web-search "latest news" --forced --raw
```

If the API returns a platform/plugin error, enable the plugin on the platform side.

## `Reserved: ... not yet documented`

Some namespaces are intentionally reserved:

- `mimo image generate`
- `mimo music generate`
- `mimo speech transcribe`
- `mimo gui`

They are placeholders for future integrations. The current Xiaomi MiMo public API docs do not expose stable endpoints for these capabilities.

## Multimodal model errors

Image/audio/video understanding is documented for:

- `mimo-v2.5`
- `mimo-v2-omni`

If another model fails, pass:

```bash
--model mimo-v2.5
```

## Local file size errors

The CLI converts local files to base64 data URLs. Large files may exceed API limits or context length limits. Prefer a public URL for large media.

## TTS returns no audio

Check:

- model supports audio output
- `audio.voice` is valid
- target text is placed as assistant content for normal TTS
- voice clone sample is mp3/wav and within documented size limits

## Config file location

Default:

```text
~/.config/mimo-cli/config.json
```

Override:

```bash
export MIMO_CONFIG_DIR=/path/to/config-dir
```
