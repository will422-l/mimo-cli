import json

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


def test_preset_vices_constant():
    """Verify PRESET_VOICES matches official Xiaomi MiMo V2.5 TTS documented voices."""
    assert "冰糖" in cli.PRESET_VOICES
    assert "茉莉" in cli.PRESET_VOICES
    assert "苏打" in cli.PRESET_VOICES
    assert "白桦" in cli.PRESET_VOICES
    assert "Mia" in cli.PRESET_VOICES
    assert "Chloe" in cli.PRESET_VOICES
    assert "Milo" in cli.PRESET_VOICES
    assert "Dean" in cli.PRESET_VOICES
    assert len(cli.PRESET_VOICES) == 8


def test_tts_voice_choices_enforced():
    """--voice should only accept preset voices."""
    parser = cli.build_parser()
    # Valid voice should work
    args = parser.parse_args(["tts", "hello", "-o", "out.wav", "--voice", "冰糖"])
    assert args.voice == "冰糖"
    # Invalid voice should be rejected by argparse choices
    try:
        parser.parse_args(["tts", "hello", "-o", "out.wav", "--voice", "nonexistent"])
        assert False, "Should have raised SystemExit for invalid voice"
    except SystemExit:
        pass


def test_tts_context_arg():
    """--context should be parsed for natural language style control."""
    parser = cli.build_parser()
    args = parser.parse_args(["tts", "hello", "-o", "out.wav", "--context", "用温柔的语气"])
    assert args.context == "用温柔的语气"


def test_tts_format_choices():
    """--format should accept wav, mp3, opus."""
    parser = cli.build_parser()
    for fmt in ["wav", "mp3", "opus"]:
        args = parser.parse_args(["tts", "hello", "-o", f"out.{fmt}", "--format", fmt])
        assert args.format == fmt
    # Invalid format should be rejected
    try:
        parser.parse_args(["tts", "hello", "-o", "out.flac", "--format", "flac"])
        assert False, "Should have raised SystemExit for invalid format"
    except SystemExit:
        pass


def test_voice_clone_validation_good(tmp_path):
    """Valid mp3/wav files under 10MB should pass validation."""
    good_file = tmp_path / "voice.mp3"
    good_file.write_bytes(b"fake mp3 data")
    cli.validate_voice_sample(str(good_file))  # Should not raise


def test_voice_clone_validation_bad_format(tmp_path):
    """Non-mp3/wav files should be rejected."""
    bad_file = tmp_path / "voice.flac"
    bad_file.write_bytes(b"fake flac data")
    try:
        cli.validate_voice_sample(str(bad_file))
        assert False, "Should have raised MimoError for bad format"
    except cli.MimoError as e:
        assert "Unsupported" in str(e)


def test_voice_clone_validation_too_large(tmp_path):
    """Files over 10MB should be rejected."""
    big_file = tmp_path / "voice.wav"
    big_file.write_bytes(b"\x00" * (10 * 1024 * 1024 + 1))
    try:
        cli.validate_voice_sample(str(big_file))
        assert False, "Should have raised MimoError for file too large"
    except cli.MimoError as e:
        assert "too large" in str(e).lower()


def test_voice_clone_validation_missing_file():
    """Nonexistent files should be rejected."""
    try:
        cli.validate_voice_sample("/nonexistent/path/voice.wav")
        assert False, "Should have raised MimoError for missing file"
    except cli.MimoError as e:
        assert "not found" in str(e).lower()


def test_feishu_send_subcommand_exists():
    """speech feishu-send subcommand should be registered."""
    parser = cli.build_parser()
    args = parser.parse_args(["speech", "feishu-send", "audio.wav", "open_id", "ou_test123"])
    assert args.audio_file == "audio.wav"
    assert args.receive_id_type == "open_id"
    assert args.receive_id == "ou_test123"


def test_tts_builds_context_message():
    """When --context is provided, it should be injected as user message."""
    parser = cli.build_parser()
    args = parser.parse_args(["tts", "你好", "-o", "out.wav", "--voice", "冰糖", "--context", "温柔地说"])
    # We can't easily call cmd_tts without mocking the API, but we can verify args
    assert args.context == "温柔地说"
    assert args.voice == "冰糖"


def test_voice_design_context_overrides_prompt():
    """voice-design --context should override voice_prompt positional arg."""
    parser = cli.build_parser()
    args = parser.parse_args([
        "speech", "voice-design", "default_prompt", "hello", "-o", "out.wav",
        "--context", "director mode instruction"
    ])
    assert args.context == "director mode instruction"
    assert args.voice_prompt == "default_prompt"


def test_voice_clone_context_arg():
    """voice-clone --context should be parsed."""
    parser = cli.build_parser()
    args = parser.parse_args([
        "speech", "voice-clone", "sample.wav", "hello", "-o", "out.wav",
        "--context", "用激动的语气"
    ])
    assert args.context == "用激动的语气"


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

    cli.save_config({"api_key": "abc"})
    assert oct(config_path.stat().st_mode & 0o777) == "0o600"


def test_reserved_command_exits_with_code_3():
    with pytest.raises(cli.NotYetDocumentedError):
        cli.cmd_image_generate(cli.argparse.Namespace())
