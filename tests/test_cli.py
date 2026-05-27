import json
from pathlib import Path

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
