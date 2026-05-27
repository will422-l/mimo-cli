import argparse
import base64
import json
import mimetypes
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests

API_BASE = os.environ.get("MIMO_BASE_URL", "https://api.xiaomimimo.com")
OPENAI_CHAT_URL = API_BASE.rstrip("/") + "/v1/chat/completions"
DEFAULT_TIMEOUT = int(os.environ.get("MIMO_TIMEOUT", "300"))


class MimoError(RuntimeError):
    pass


def env_api_key() -> str:
    key = os.environ.get("MIMO_API_KEY") or os.environ.get("XIAOMIMIMO_API_KEY")
    if not key:
        raise MimoError("Missing API key. Set MIMO_API_KEY or XIAOMIMIMO_API_KEY.")
    return key


def auth_headers() -> Dict[str, str]:
    return {
        "Authorization": f"Bearer {env_api_key()}",
        "Content-Type": "application/json",
    }


def read_text_arg(text: Optional[str], text_file: Optional[str]) -> str:
    if text_file:
        return Path(text_file).read_text(encoding="utf-8")
    if text is None:
        raise MimoError("Text is required. Pass positional text or --text-file.")
    return text


def file_to_data_url(path: str) -> str:
    p = Path(path)
    mime, _ = mimetypes.guess_type(str(p))
    if not mime:
        mime = "application/octet-stream"
    raw = p.read_bytes()
    return f"data:{mime};base64," + base64.b64encode(raw).decode("ascii")


def maybe_media_ref(value: str, kind: str) -> Dict[str, Any]:
    if value.startswith("http://") or value.startswith("https://") or value.startswith("data:"):
        return {kind: {"url": value} if kind in {"image_url", "video_url"} else {"data": value}}
    data_url = file_to_data_url(value)
    return {kind: {"url": data_url} if kind in {"image_url", "video_url"} else {"data": data_url}}


def post_chat(payload: Dict[str, Any], stream: bool = False):
    response = requests.post(
        OPENAI_CHAT_URL,
        headers=auth_headers(),
        json=payload,
        stream=stream,
        timeout=DEFAULT_TIMEOUT,
    )
    if response.status_code >= 400:
        raise MimoError(f"HTTP {response.status_code}: {response.text[:2000]}")
    return response


def extract_message(data: Dict[str, Any]) -> Dict[str, Any]:
    choices = data.get("choices") or []
    if not choices:
        raise MimoError("No choices returned")
    return choices[0].get("message") or {}


def save_audio_from_message(message: Dict[str, Any], out_path: str) -> None:
    audio = message.get("audio")
    if not audio or not audio.get("data"):
        raise MimoError("No audio returned in response")
    Path(out_path).write_bytes(base64.b64decode(audio["data"]))


def print_json(obj: Any) -> None:
    print(json.dumps(obj, ensure_ascii=False, indent=2))


def cmd_models(_: argparse.Namespace) -> None:
    models = {
        "text_models": [
            "mimo-v2.5-pro",
            "mimo-v2-pro",
            "mimo-v2.5",
            "mimo-v2-omni",
            "mimo-v2-flash",
        ],
        "tts_models": [
            "mimo-v2.5-tts",
            "mimo-v2.5-tts-voiceclone",
            "mimo-v2.5-tts-voicedesign",
            "mimo-v2-tts",
        ],
        "documented_capabilities": {
            "function_calling": ["mimo-v2.5-pro", "mimo-v2-pro", "mimo-v2.5", "mimo-v2-omni", "mimo-v2-flash"],
            "web_search": ["mimo-v2.5-pro", "mimo-v2.5", "mimo-v2-pro", "mimo-v2-omni", "mimo-v2-flash"],
            "image_understanding": ["mimo-v2.5", "mimo-v2-omni"],
            "audio_understanding": ["mimo-v2.5", "mimo-v2-omni"],
            "video_understanding": ["mimo-v2.5", "mimo-v2-omni"],
            "tts_builtin_voice": ["mimo-v2.5-tts", "mimo-v2-tts"],
            "tts_voice_design": ["mimo-v2.5-tts-voicedesign"],
            "tts_voice_clone": ["mimo-v2.5-tts-voiceclone"],
            "singing_style": ["mimo-v2.5-tts", "mimo-v2-tts"],
        },
        "not_in_current_api_docs": [
            "image generation / text-to-image",
            "music generation / text-to-music",
            "standalone ASR HTTP API docs",
            "GUI/computer-use API details",
        ],
    }
    print_json(models)


def cmd_chat(args: argparse.Namespace) -> None:
    user_text = read_text_arg(args.text, args.text_file)
    payload: Dict[str, Any] = {
        "model": args.model,
        "messages": [{"role": "user", "content": user_text}],
    }
    if args.system:
        payload["messages"].insert(0, {"role": "system", "content": args.system})
    if args.temperature is not None:
        payload["temperature"] = args.temperature
    if args.max_tokens is not None:
        payload["max_tokens"] = args.max_tokens
    if args.thinking:
        payload["thinking"] = {"type": "enabled", "budget_tokens": args.budget_tokens}
    if args.json_mode:
        payload["response_format"] = {"type": "json_object"}
    data = post_chat(payload).json()
    if args.raw:
        print_json(data)
        return
    message = extract_message(data)
    if message.get("reasoning_content"):
        print("=== reasoning_content ===")
        print(message["reasoning_content"])
        print()
    print(message.get("content", ""))


def cmd_tool_call(args: argparse.Namespace) -> None:
    prompt = read_text_arg(args.text, args.text_file)
    schema = json.loads(Path(args.tools_file).read_text(encoding="utf-8"))
    payload = {
        "model": args.model,
        "messages": [{"role": "user", "content": prompt}],
        "tools": schema,
        "tool_choice": args.tool_choice,
    }
    data = post_chat(payload).json()
    print_json(data if args.raw else extract_message(data))


def cmd_web_search(args: argparse.Namespace) -> None:
    prompt = read_text_arg(args.text, args.text_file)
    payload = {
        "model": args.model,
        "messages": [{"role": "user", "content": prompt}],
        "tools": [{"type": "web_search", "forced_search": bool(args.forced)}],
        "tool_choice": "auto",
    }
    data = post_chat(payload).json()
    if args.raw:
        print_json(data)
        return
    msg = extract_message(data)
    print(msg.get("content", ""))
    annotations = msg.get("annotations") or []
    if annotations:
        print("\n=== annotations ===")
        print_json(annotations)
    usage = data.get("usage", {}).get("web_search_usage")
    if usage:
        print("\n=== web_search_usage ===")
        print_json(usage)


def multimodal_message(prompt: str, media_kind: str, media_value: str) -> List[Dict[str, Any]]:
    part = maybe_media_ref(media_value, media_kind)
    return [{"role": "user", "content": [
        {"type": list(part.keys())[0], **list(part.values())[0]},
        {"type": "text", "text": prompt},
    ]}]


def cmd_image_understand(args: argparse.Namespace) -> None:
    payload = {
        "model": args.model,
        "messages": multimodal_message(args.prompt, "image_url", args.image),
    }
    data = post_chat(payload).json()
    print_json(data if args.raw else extract_message(data))


def cmd_audio_understand(args: argparse.Namespace) -> None:
    payload = {
        "model": args.model,
        "messages": multimodal_message(args.prompt, "input_audio", args.audio),
    }
    data = post_chat(payload).json()
    print_json(data if args.raw else extract_message(data))


def cmd_video_understand(args: argparse.Namespace) -> None:
    payload = {
        "model": args.model,
        "messages": multimodal_message(args.prompt, "video_url", args.video),
    }
    data = post_chat(payload).json()
    print_json(data if args.raw else extract_message(data))


def cmd_tts(args: argparse.Namespace) -> None:
    text = read_text_arg(args.text, args.text_file)
    messages = []
    if args.instruction:
        messages.append({"role": "user", "content": args.instruction})
    messages.append({"role": "assistant", "content": text})
    payload = {
        "model": args.model,
        "messages": messages,
        "audio": {
            "voice": args.voice,
            "format": args.format,
        },
        "stream": False,
    }
    data = post_chat(payload).json()
    message = extract_message(data)
    save_audio_from_message(message, args.output)
    if args.raw:
        print_json(data)
    else:
        print(args.output)


def cmd_tts_voice_design(args: argparse.Namespace) -> None:
    target_text = read_text_arg(args.text, args.text_file)
    messages = [{"role": "user", "content": args.voice_prompt}]
    if not args.optimize_text_preview:
        messages.append({"role": "assistant", "content": target_text})
    payload = {
        "model": "mimo-v2.5-tts-voicedesign",
        "messages": messages,
        "audio": {
            "voice": "voice_design",
            "format": args.format,
            "optimize_text_preview": bool(args.optimize_text_preview),
        },
        "stream": False,
    }
    data = post_chat(payload).json()
    message = extract_message(data)
    save_audio_from_message(message, args.output)
    if args.raw:
        print_json(data)
    else:
        print(args.output)


def cmd_tts_voice_clone(args: argparse.Namespace) -> None:
    target_text = read_text_arg(args.text, args.text_file)
    payload = {
        "model": "mimo-v2.5-tts-voiceclone",
        "messages": [{"role": "assistant", "content": target_text}],
        "audio": {
            "voice": file_to_data_url(args.voice_sample),
            "format": args.format,
        },
        "stream": False,
    }
    data = post_chat(payload).json()
    message = extract_message(data)
    save_audio_from_message(message, args.output)
    if args.raw:
        print_json(data)
    else:
        print(args.output)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="mimo", description="Xiaomi MiMo API CLI")
    sub = p.add_subparsers(dest="command", required=True)

    s = sub.add_parser("models", help="Show documented models and capability map")
    s.set_defaults(func=cmd_models)

    s = sub.add_parser("chat", help="Basic text chat")
    s.add_argument("text", nargs="?")
    s.add_argument("--text-file")
    s.add_argument("--model", default="mimo-v2.5-pro")
    s.add_argument("--system")
    s.add_argument("--temperature", type=float)
    s.add_argument("--max-tokens", type=int)
    s.add_argument("--thinking", action="store_true")
    s.add_argument("--budget-tokens", type=int, default=4096)
    s.add_argument("--json-mode", action="store_true")
    s.add_argument("--raw", action="store_true")
    s.set_defaults(func=cmd_chat)

    s = sub.add_parser("tool-call", help="Ask model to produce function tool calls from a JSON tools schema file")
    s.add_argument("text", nargs="?")
    s.add_argument("--text-file")
    s.add_argument("--model", default="mimo-v2.5-pro")
    s.add_argument("--tools-file", required=True)
    s.add_argument("--tool-choice", default="auto")
    s.add_argument("--raw", action="store_true")
    s.set_defaults(func=cmd_tool_call)

    s = sub.add_parser("web-search", help="Use MiMo built-in web search tool")
    s.add_argument("text", nargs="?")
    s.add_argument("--text-file")
    s.add_argument("--model", default="mimo-v2.5-pro")
    s.add_argument("--forced", action="store_true")
    s.add_argument("--raw", action="store_true")
    s.set_defaults(func=cmd_web_search)

    s = sub.add_parser("image-understand", help="Image understanding via URL, data URL, or local file")
    s.add_argument("image")
    s.add_argument("prompt")
    s.add_argument("--model", default="mimo-v2.5")
    s.add_argument("--raw", action="store_true")
    s.set_defaults(func=cmd_image_understand)

    s = sub.add_parser("audio-understand", help="Audio understanding via URL, data URL, or local file")
    s.add_argument("audio")
    s.add_argument("prompt")
    s.add_argument("--model", default="mimo-v2.5")
    s.add_argument("--raw", action="store_true")
    s.set_defaults(func=cmd_audio_understand)

    s = sub.add_parser("video-understand", help="Video understanding via URL, data URL, or local file")
    s.add_argument("video")
    s.add_argument("prompt")
    s.add_argument("--model", default="mimo-v2.5")
    s.add_argument("--raw", action="store_true")
    s.set_defaults(func=cmd_video_understand)

    s = sub.add_parser("tts", help="Built-in voice TTS")
    s.add_argument("text", nargs="?")
    s.add_argument("--text-file")
    s.add_argument("-o", "--output", required=True)
    s.add_argument("--model", default="mimo-v2.5-tts")
    s.add_argument("--voice", default="mimo_default")
    s.add_argument("--format", default="wav")
    s.add_argument("--instruction", help="Optional user instruction for style/tone")
    s.add_argument("--raw", action="store_true")
    s.set_defaults(func=cmd_tts)

    s = sub.add_parser("tts-voice-design", help="Generate custom voice from natural-language voice prompt")
    s.add_argument("voice_prompt")
    s.add_argument("text", nargs="?")
    s.add_argument("--text-file")
    s.add_argument("-o", "--output", required=True)
    s.add_argument("--format", default="wav")
    s.add_argument("--optimize-text-preview", action="store_true")
    s.add_argument("--raw", action="store_true")
    s.set_defaults(func=cmd_tts_voice_design)

    s = sub.add_parser("tts-voice-clone", help="Clone a voice from local audio sample")
    s.add_argument("voice_sample")
    s.add_argument("text", nargs="?")
    s.add_argument("--text-file")
    s.add_argument("-o", "--output", required=True)
    s.add_argument("--format", default="wav")
    s.add_argument("--raw", action="store_true")
    s.set_defaults(func=cmd_tts_voice_clone)

    return p


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    try:
        args.func(args)
    except KeyboardInterrupt:
        print("Interrupted", file=sys.stderr)
        raise SystemExit(130)
    except MimoError as e:
        print(f"Error: {e}", file=sys.stderr)
        raise SystemExit(2)


if __name__ == "__main__":
    main()
