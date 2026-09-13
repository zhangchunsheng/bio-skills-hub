#!/usr/bin/env python3

from __future__ import annotations

import base64
import copy
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import sys
import tempfile
import threading
import time
import unittest
from unittest import mock
import wave
from io import BytesIO


SKILL_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL_DIR / "scripts"))

import generate_audio  # noqa: E402
import generate_scene_audio  # noqa: E402
import generate_bgm  # noqa: E402
import generate_images  # noqa: E402
import generate_voice_previews  # noqa: E402
import build_hyperframes  # noqa: E402
import finalize_video  # noqa: E402
from validate_story import load_story, validate_story  # noqa: E402


def silent_wav() -> bytes:
    buffer = BytesIO()
    with wave.open(buffer, "wb") as output:
        output.setnchannels(1)
        output.setsampwidth(2)
        output.setframerate(24000)
        output.writeframes(b"\0\0" * 2400)
    return buffer.getvalue()


def minimal_png(width: int = 1600, height: int = 900) -> bytes:
    signature = b"\x89PNG\r\n\x1a\n"
    ihdr_data = width.to_bytes(4, "big") + height.to_bytes(4, "big") + b"\x08\x02\x00\x00\x00"
    ihdr = len(ihdr_data).to_bytes(4, "big") + b"IHDR" + ihdr_data + b"\x00\x00\x00\x00"
    iend = b"\x00\x00\x00\x00IEND\x00\x00\x00\x00"
    return signature + ihdr + iend


class _MiMoHandler(BaseHTTPRequestHandler):
    response_status = 200
    response_body: dict = {}
    requests: list[dict] = []
    fail_first = False

    def do_POST(self) -> None:  # noqa: N802
        length = int(self.headers.get("Content-Length", "0"))
        body = json.loads(self.rfile.read(length).decode("utf-8"))
        type(self).requests.append(
            {"path": self.path, "api_key": self.headers.get("api-key"), "body": body}
        )
        if type(self).fail_first and len(type(self).requests) == 1:
            self.send_response(429)
            self.end_headers()
            self.wfile.write(b'{"error":"rate limited"}')
            return
        self.send_response(type(self).response_status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(type(self).response_body).encode("utf-8"))

    def log_message(self, format: str, *args: object) -> None:
        return


class _Server:
    def __init__(self, handler: type[_MiMoHandler]) -> None:
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)

    def __enter__(self) -> str:
        self.thread.start()
        host, port = self.server.server_address
        return f"http://{host}:{port}/v1"

    def __exit__(self, *args: object) -> None:
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=2)


class RuntimeIntegrationTests(unittest.TestCase):
    def setUp(self) -> None:
        _MiMoHandler.requests = []
        _MiMoHandler.fail_first = False
        _MiMoHandler.response_status = 200
        _MiMoHandler.response_body = {
            "choices": [
                {
                    "message": {
                        "audio": {"data": base64.b64encode(silent_wav()).decode("ascii")}
                    }
                }
            ]
        }

    def test_openai_base_url_normalization(self) -> None:
        self.assertEqual(
            generate_images.normalize_openai_base_url("https://api.example.com"),
            "https://api.example.com/v1",
        )
        self.assertEqual(
            generate_images.normalize_openai_base_url("https://api.example.com/v1/"),
            "https://api.example.com/v1",
        )
        with self.assertRaises(ValueError):
            generate_images.normalize_openai_base_url("https://user:pass@example.com")

    def test_image_proxy_environment_is_removed(self) -> None:
        env = {
            "HTTPS_PROXY": "http://127.0.0.1:7897",
            "all_proxy": "socks5://127.0.0.1:7897",
            "OPENAI_API_KEY": "kept",
        }
        generate_images.clear_proxy_environment(env)
        self.assertEqual(env, {"OPENAI_API_KEY": "kept"})

    def test_image_cli_finishes_when_complete_png_is_ready(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "result.png"
            payload = minimal_png()
            code = (
                "from pathlib import Path; import time; "
                f"Path({str(output)!r}).write_bytes(bytes.fromhex({payload.hex()!r})); "
                "time.sleep(30)"
            )
            statuses: list[str] = []
            started = time.monotonic()
            ok, _ = generate_images.run_cli(
                [sys.executable, "-c", code],
                dict(generate_images.os.environ),
                attempts=1,
                dry_run=False,
                output_path=output,
                requested_size="1600x900",
                status_callback=lambda status, attempt, elapsed: statuses.append(status),
            )
            self.assertTrue(ok)
            self.assertLess(time.monotonic() - started, 6)
            self.assertIn("file_ready", statuses)

    def test_incomplete_png_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "incomplete.png"
            output.write_bytes(minimal_png()[:-12])
            with self.assertRaises(ValueError):
                generate_images.inspect_png_output(output, "1600x900")

    def test_image_cli_times_out_without_local_file(self) -> None:
        statuses: list[str] = []
        started = time.monotonic()
        ok, detail = generate_images.run_cli(
            [sys.executable, "-c", "import time; time.sleep(30)"],
            dict(generate_images.os.environ),
            attempts=1,
            dry_run=False,
            output_path=None,
            requested_size=None,
            status_callback=lambda status, attempt, elapsed: statuses.append(status),
            request_timeout_seconds=0.5,
        )
        self.assertFalse(ok)
        self.assertLess(time.monotonic() - started, 4)
        self.assertIn("timed_out", statuses)
        self.assertIn("without a complete local PNG", detail)

    def test_image_cli_accepts_provider_aspect_ratio(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "result.png"
            payload = minimal_png(1942, 809)
            code = (
                "from pathlib import Path; "
                f"Path({str(output)!r}).write_bytes(bytes.fromhex({payload.hex()!r}))"
            )
            ok, _ = generate_images.run_cli(
                [sys.executable, "-c", code],
                dict(generate_images.os.environ),
                attempts=2,
                dry_run=False,
                output_path=output,
                requested_size="1600x900",
            )
            self.assertTrue(ok)
            actual_size, warning = generate_images.inspect_png_output(output, "1600x900")
            self.assertEqual(actual_size, "1942x809")
            self.assertIn("cover-cropped", warning)

    def test_image_cli_retries_incomplete_png(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "result.png"
            counter = Path(directory) / "attempt.txt"
            incomplete = minimal_png()[:-12]
            valid = minimal_png()
            code = (
                "from pathlib import Path; "
                f"counter=Path({str(counter)!r}); "
                "attempt=int(counter.read_text())+1 if counter.exists() else 1; "
                "counter.write_text(str(attempt)); "
                f"Path({str(output)!r}).write_bytes(bytes.fromhex(({incomplete.hex()!r} if attempt == 1 else {valid.hex()!r})))"
            )
            with mock.patch.object(generate_images.time, "sleep"):
                ok, _ = generate_images.run_cli(
                    [sys.executable, "-c", code],
                    dict(generate_images.os.environ),
                    attempts=2,
                    dry_run=False,
                    output_path=output,
                    requested_size="1600x900",
                )
            self.assertTrue(ok)
            self.assertEqual(counter.read_text(), "2")

    def test_music_proxy_environment_is_removed(self) -> None:
        with mock.patch.dict(
            generate_bgm.os.environ,
            {"https_proxy": "http://127.0.0.1:7897", "MUSICGEN_MODEL": "kept"},
            clear=True,
        ):
            generate_bgm.clear_proxy_environment()
            self.assertEqual(dict(generate_bgm.os.environ), {"MUSICGEN_MODEL": "kept"})

    def test_composition_allows_disabled_bgm(self) -> None:
        story = {"audio": {"bgm": {"enabled": False}}}
        self.assertIsNone(build_hyperframes.resolve_bgm(story, {}, Path("/unused")))

    def test_composition_bundles_local_gsap(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = build_hyperframes.copy_runtime_assets(Path(directory))
            self.assertTrue(target.exists())
            self.assertGreater(target.stat().st_size, 50_000)

    def test_composition_mixes_narration_to_one_track(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            source = project / "line.wav"
            source.write_bytes(silent_wav())
            manifest = {
                "scenes": [
                    {
                        "lines": [
                            {"file": "line.wav", "start": 0.05},
                            {"file": "line.wav", "start": 0.2},
                        ]
                    }
                ]
            }
            output = build_hyperframes.mix_narration_track(manifest, project, 0.5)
            with wave.open(str(output), "rb") as mixed:
                self.assertEqual(mixed.getnchannels(), 1)
                self.assertEqual(mixed.getframerate(), 24000)
                self.assertEqual(mixed.getnframes(), 12000)

    def test_composition_preserves_scene_level_master_audio(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            source = project / "master.wav"
            source.write_bytes(silent_wav())
            output = build_hyperframes.resolve_narration_track(
                {"master_audio": "master.wav"}, project, 0.1
            )
            self.assertEqual(output.read_bytes(), source.read_bytes())

    def test_mimo_base_url_normalization(self) -> None:
        self.assertEqual(
            generate_audio.normalize_api_base_url("https://api.xiaomimimo.com"),
            "https://api.xiaomimimo.com/v1",
        )
        with self.assertRaises(ValueError):
            generate_audio.normalize_api_base_url("https://example.com?key=secret")

    def test_mimo_payload_uses_required_message_roles(self) -> None:
        narrator = {
            "provider": "xiaomi_mimo",
            "model": "mimo-v2.5-tts",
            "voice": "苏打",
            "tone": "克制、轻松",
            "speed": 1.3,
            "language": "zh-CN",
        }
        narration = {"text": "今天先把日子过好。", "emotion": "平静"}
        runtime = {"model": "mimo-v2.5-tts"}
        payload = generate_audio.build_mimo_payload(narrator, runtime, narration)
        self.assertEqual([item["role"] for item in payload["messages"]], ["user", "assistant"])
        self.assertEqual(payload["messages"][1]["content"], narration["text"])
        self.assertEqual(payload["audio"], {"format": "wav", "voice": "苏打"})

    def test_mimo_voice_design_payload_omits_preset_voice(self) -> None:
        narrator = {
            "provider": "xiaomi_mimo",
            "model": "mimo-v2.5-tts-voicedesign",
            "voice": "magnetic-relaxed",
            "voice_design": "四十岁左右的中文男性，磁性、温暖、松弛。",
            "tone": "纪实、克制",
            "speed": 1.5,
            "language": "zh-CN",
        }
        narration = {"text": "二十五岁那年，你没有再续租。", "emotion": "平静"}
        runtime = {"model": "mimo-v2.5-tts-voicedesign"}
        payload = generate_audio.build_mimo_payload(narrator, runtime, narration)
        self.assertEqual(payload["model"], "mimo-v2.5-tts-voicedesign")
        self.assertEqual(payload["messages"][0]["content"], narrator["voice_design"])
        self.assertEqual(
            payload["audio"], {"format": "wav", "optimize_text_preview": False}
        )

    def test_scene_mimo_payload_joins_captions_and_locks_delivery(self) -> None:
        narrator = {
            "provider": "xiaomi_mimo",
            "model": "mimo-v2.5-tts-voicedesign",
            "voice": "magnetic-relaxed",
            "voice_design": "四十岁左右的中文男性，磁性、温暖、松弛。",
            "tone": "纪实、克制",
            "speed": 1.5,
            "language": "zh-CN",
        }
        scene = {
            "narrations": [
                {"text": "二十五岁那年，你没有再续租。"},
                {"text": "房租又涨了五百。"},
            ]
        }
        text = generate_scene_audio.build_scene_text(scene)
        payload = generate_scene_audio.build_scene_mimo_payload(
            narrator, {"model": narrator["model"]}, text
        )
        self.assertEqual(
            payload["messages"][1]["content"],
            "二十五岁那年，你没有再续租。房租又涨了五百。",
        )
        self.assertIn("句首直接进入", payload["messages"][0]["content"])
        self.assertIn(narrator["tone"], payload["messages"][0]["content"])
        self.assertEqual(
            payload["audio"], {"format": "wav", "optimize_text_preview": False}
        )

    def test_scene_raw_audio_cache_does_not_depend_on_global_speed(self) -> None:
        narrator = {
            "voice": "magnetic-relaxed",
            "voice_design": "磁性、温暖、松弛。",
            "tone": "纪实、克制",
            "speed": 1.0,
            "language": "zh-CN",
        }
        runtime = {"provider": "xiaomi_mimo", "model": "mimo-v2.5-tts-voicedesign"}
        first = generate_scene_audio.scene_fingerprint(
            narrator, runtime, "scene_001", "同一段文本。"
        )
        narrator["speed"] = 1.5
        second = generate_scene_audio.scene_fingerprint(
            narrator, runtime, "scene_001", "同一段文本。"
        )
        self.assertEqual(first, second)

    def test_scene_boundary_alignment_prefers_real_silence(self) -> None:
        silences = [
            {"start": 1.8, "end": 2.2, "duration": 0.4, "mid": 2.0},
            {"start": 3.0, "end": 3.1, "duration": 0.1, "mid": 3.05},
            {"start": 4.7, "end": 5.3, "duration": 0.6, "mid": 5.0},
        ]
        selected, expected, chosen = generate_scene_audio.select_boundaries(
            ["第一句话。", "第二句话。", "第三句话。"], 7.5, silences
        )
        self.assertEqual(selected, [2.0, 5.0])
        self.assertEqual(len(expected), 2)
        self.assertTrue(all(item["duration"] > 0 for item in chosen))

    def test_scene_wav_join_adds_only_inter_scene_gap(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            first = root / "first.wav"
            second = root / "second.wav"
            output = root / "joined.wav"
            first.write_bytes(silent_wav())
            second.write_bytes(silent_wav())
            frames = generate_scene_audio.join_wav_files(
                [first, second], output, 0.35
            )
            self.assertEqual(frames, round(0.55 * 24000))

    def test_voice_preview_enables_preview_text_optimization(self) -> None:
        profile = {
            "id": "custom",
            "name": "Custom",
            "kind": "voice_design",
            "model": "mimo-v2.5-tts-voicedesign",
            "direction": "磁性松弛的中文男声。",
        }
        payload = generate_voice_previews.preview_payload(profile, "测试文案。")
        self.assertEqual(
            payload["audio"], {"format": "wav", "optimize_text_preview": True}
        )

    def test_final_media_validation_requires_video_and_audio(self) -> None:
        valid_media = {
            "streams": [
                {
                    "codec_type": "video",
                    "width": 1920,
                    "height": 1080,
                    "r_frame_rate": "30/1",
                },
                {"codec_type": "audio", "channels": 1, "sample_rate": "24000"},
            ],
            "format": {"duration": "12.000"},
        }
        self.assertEqual(finalize_video.validate_final_media(valid_media, 12.0), [])
        self.assertTrue(
            finalize_video.validate_final_media(
                {"streams": valid_media["streams"][:1], "format": {"duration": "12"}},
                12.0,
            )
        )

    def test_mimo_request_decodes_wav_and_retries_429(self) -> None:
        _MiMoHandler.fail_first = True
        payload = {
            "model": "mimo-v2.5-tts",
            "messages": [{"role": "assistant", "content": "测试。"}],
            "audio": {"format": "wav", "voice": "苏打"},
        }
        with _Server(_MiMoHandler) as base_url, mock.patch.object(generate_audio.time, "sleep"):
            result = generate_audio.request_mimo_wav(payload, base_url, "test-key", 2)
        self.assertTrue(result.startswith(b"RIFF"))
        self.assertEqual(len(_MiMoHandler.requests), 2)
        self.assertEqual(_MiMoHandler.requests[-1]["path"], "/v1/chat/completions")
        self.assertEqual(_MiMoHandler.requests[-1]["api_key"], "test-key")

    def test_mimo_error_redacts_key(self) -> None:
        secret = "secret-value"
        _MiMoHandler.response_status = 400
        _MiMoHandler.response_body = {"error": secret}
        with _Server(_MiMoHandler) as base_url:
            with self.assertRaises(RuntimeError) as caught:
                generate_audio.request_mimo_wav({}, base_url, secret, 1)
        self.assertNotIn(secret, str(caught.exception))

    def test_narration_fingerprint_changes_with_emotion(self) -> None:
        narrator = {
            "voice": "苏打",
            "tone": "克制、轻松",
            "speed": 1.3,
            "language": "zh-CN",
        }
        runtime = {"provider": "xiaomi_mimo", "model": "mimo-v2.5-tts"}
        first = generate_audio.narration_fingerprint(
            narrator, runtime, {"text": "同一句。", "emotion": "平静"}
        )
        second = generate_audio.narration_fingerprint(
            narrator, runtime, {"text": "同一句。", "emotion": "紧张"}
        )
        self.assertNotEqual(first, second)

    def test_audio_manifest_prunes_removed_sentences(self) -> None:
        manifest = {
            "jobs": {
                "scene_001:001": {"status": "complete"},
                "scene_001:002": {"status": "complete"},
                "scene_001:003": {"status": "complete"},
            }
        }
        scenes = [{"id": "scene_001", "narrations": [{}, {}]}]
        generate_audio.prune_narration_jobs(manifest, scenes)
        self.assertEqual(
            set(manifest["jobs"]), {"scene_001:001", "scene_001:002"}
        )

    def test_validator_supports_legacy_and_mimo(self) -> None:
        example = load_story(SKILL_DIR / "assets/example-story.json")
        self.assertTrue(validate_story(example)["valid"])
        mimo = copy.deepcopy(example)
        mimo["narrator"].update(
            {
                "provider": "xiaomi_mimo",
                "model": "mimo-v2.5-tts",
                "voice": "苏打",
                "speed": 1.5,
                "language": "zh-CN",
            }
        )
        self.assertTrue(validate_story(mimo)["valid"])
        mimo["narrator"]["voice"] = "unsupported"
        self.assertFalse(validate_story(mimo)["valid"])

        voice_design = copy.deepcopy(example)
        voice_design["narrator"].update(
            {
                "provider": "xiaomi_mimo",
                "model": "mimo-v2.5-tts-voicedesign",
                "voice": "magnetic-relaxed",
                "voice_design": "四十岁左右的中文男性，磁性、温暖、松弛。",
                "speed": 1.5,
                "language": "zh-CN",
            }
        )
        self.assertTrue(validate_story(voice_design)["valid"])
        del voice_design["narrator"]["voice_design"]
        self.assertFalse(validate_story(voice_design)["valid"])

    def test_validator_supports_combined_visual_review(self) -> None:
        story = load_story(SKILL_DIR / "assets/example-story.json")
        story["stage"] = "visual_review"
        story["approvals"]["story"] = "approved"
        self.assertTrue(validate_story(story)["valid"])

    def test_validator_allows_disabled_bgm(self) -> None:
        story = load_story(SKILL_DIR / "assets/example-story.json")
        story["audio"]["bgm"] = {"enabled": False}
        self.assertTrue(validate_story(story)["valid"])

    def test_validator_accepts_optional_scene_gap(self) -> None:
        story = load_story(SKILL_DIR / "assets/example-story.json")
        story["audio"]["scene_gap_seconds"] = 0.35
        self.assertTrue(validate_story(story)["valid"])
        story["audio"]["scene_gap_seconds"] = 3
        self.assertFalse(validate_story(story)["valid"])

    def test_validator_enforces_project_caption_limit(self) -> None:
        story = load_story(SKILL_DIR / "assets/example-story.json")
        story["project"]["caption_max_characters"] = 12
        story["scenes"][0]["narrations"][0]["text"] = "这是一条明显超过十二个字符限制的字幕。"
        report = validate_story(story)
        self.assertFalse(report["valid"])
        self.assertTrue(
            any("caption_max_characters=12" in error for error in report["errors"])
        )


if __name__ == "__main__":
    unittest.main()
