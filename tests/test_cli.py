import json
from pathlib import Path

import pytest

from mimo_tools import cli


def test_multimodal_image_payload_shape(tmp_path):
    img = tmp_path / "a.png"
    img.write_bytes(b"fake")
    messages = cli.multimodal_message("describe", "image_url", str(img))
    part = messages[0]["content"][0]
    assert part["type"] == "image_url"
    assert "image_url" in part
    assert part["image_url"]["url"].startswith("data:image/png;base64,")


def test_multimodal_audio_payload_shape(tmp_path):
    audio = tmp_path / "a.wav"
    audio.write_bytes(b"fake")
    messages = cli.multimodal_message("describe", "input_audio", str(audio))
    part = messages[0]["content"][0]
    assert part["type"] == "input_audio"
    assert "input_audio" in part
    assert part["input_audio"]["data"].startswith("data:audio/x-wav;base64,") or part["input_audio"]["data"].startswith("data:audio/wav;base64,")


def test_capability_map_has_reserved_items():
    data = cli.capability_map()
    assert "image generation / text-to-image" in data["reserved_not_yet_documented"]
    assert "mimo-v2.5" in data["documented_capabilities"]["image_understanding"]


def test_parser_version_and_reserved_commands_exist():
    parser = cli.build_parser()
    help_text = parser.format_help()
    assert "auth" in help_text
    assert "config" in help_text
    assert "doctor" in help_text
    assert "image" in help_text
    assert "music" in help_text


def test_chat_url_does_not_duplicate_v1(monkeypatch):
    monkeypatch.setattr(cli, "get_config_value", lambda key: "https://api.example.com/v1" if key == "base_url" else None)
    assert cli.chat_url() == "https://api.example.com/v1/chat/completions"


def test_chat_url_appends_v1_when_absent(monkeypatch):
    monkeypatch.setattr(cli, "get_config_value", lambda key: "https://api.example.com" if key == "base_url" else None)
    assert cli.chat_url() == "https://api.example.com/v1/chat/completions"


def test_web_search_payload_uses_force_search(monkeypatch):
    captured = {}

    class Response:
        def json(self):
            return {"choices": [{"message": {"content": "ok"}}]}

    def fake_post_chat(payload, args=None, stream=False):
        captured["payload"] = payload
        return Response()

    monkeypatch.setattr(cli, "post_chat", fake_post_chat)
    args = cli.build_parser().parse_args(["search", "query", "hello", "--forced"])
    args.func(args)

    tool = captured["payload"]["tools"][0]
    assert tool == {"type": "web_search", "force_search": True}
    assert "forced_search" not in tool


def test_config_show_masks_short_api_key(tmp_path, monkeypatch, capsys):
    config_dir = tmp_path / "config"
    config_path = config_dir / "config.json"
    monkeypatch.setattr(cli, "CONFIG_DIR", config_dir)
    monkeypatch.setattr(cli, "CONFIG_PATH", config_path)

    cli.save_config({"api_key": "abc"})
    cli.cmd_config_show(cli.argparse.Namespace())
    output = capsys.readouterr().out
    data = json.loads(output)
    assert data["config"]["api_key"] == "***"
    assert "abc" not in output


def test_auth_status_masks_short_api_key(tmp_path, monkeypatch, capsys):
    config_dir = tmp_path / "config"
    config_path = config_dir / "config.json"
    monkeypatch.setattr(cli, "CONFIG_DIR", config_dir)
    monkeypatch.setattr(cli, "CONFIG_PATH", config_path)
    monkeypatch.delenv("MIMO_API_KEY", raising=False)
    monkeypatch.delenv("XIAOMIMIMO_API_KEY", raising=False)

    cli.save_config({"api_key": "abc"})
    cli.cmd_auth_status(cli.argparse.Namespace(api_key=None))
    output = capsys.readouterr().out
    data = json.loads(output)
    assert data["key"] == "***"
    assert "abc" not in output


def test_save_config_uses_private_permissions(tmp_path, monkeypatch):
    config_dir = tmp_path / "config"
    config_path = config_dir / "config.json"
    monkeypatch.setattr(cli, "CONFIG_DIR", config_dir)
    monkeypatch.setattr(cli, "CONFIG_PATH", config_path)

    cli.save_config({"api_key": "secret"})
    assert oct(config_path.stat().st_mode & 0o777) == "0o600"


def test_reserved_command_exits_with_code_3():
    with pytest.raises(cli.NotYetDocumentedError):
        cli.cmd_image_generate(cli.argparse.Namespace())
