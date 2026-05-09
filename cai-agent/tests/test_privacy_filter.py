from __future__ import annotations

from typing import Any
from unittest.mock import patch

from cai_agent import llm_factory
from cai_agent.config import Settings
from cai_agent.privacy_filter import filter_outgoing_chat_messages, redact_outgoing_text


def test_redact_off_is_identity() -> None:
    s = "user@corp.example sk-proj-123456789012345678901234567890 C:\\Secret\\a.txt"
    assert redact_outgoing_text(s, "off") == s
    assert redact_outgoing_text(s, "unknown_mode") == s


def test_redact_email_and_openai_sk_light() -> None:
    s = "mail user.name@example.com and sk-proj-abcdefghijklmnopqrstuvwxyz0123456789ABCD tail"
    out = redact_outgoing_text(s, "light")
    assert "example.com" not in out
    assert "abcdefghijklmnopqrstuvwxyz" not in out
    assert "…" in out


def test_redact_bearer_and_unix_path_light() -> None:
    s = 'Authorization: Bearer supersecrettokenvaluehere path /home/alice/proj/readme.md end'
    out = redact_outgoing_text(s, "light")
    assert "supersecrettokenvaluehere" not in out
    assert "/home/alice/proj/readme.md" not in out


def test_strict_redacts_long_hex_not_matched_in_light() -> None:
    blob = "deadbeefdeadbeefdeadbeefdeadbeefdeadbeef"
    assert redact_outgoing_text(blob, "light") == blob
    strict = redact_outgoing_text(blob, "strict")
    assert "deadbeefdeadbeefdeadbeefdeadbeefdeadbeef" not in strict


def test_strict_ssn_pattern() -> None:
    # SSN-shaped runs are also matched by the coarse phone heuristic in light.
    assert "078-05-1120" not in redact_outgoing_text("ssn 078-05-1120", "light")
    assert "078-05-1120" not in redact_outgoing_text("ssn 078-05-1120", "strict")


def test_filter_messages_copies_and_preserves_off() -> None:
    raw: list[dict[str, Any]] = [{"role": "user", "content": "a@b.co"}]
    off = filter_outgoing_chat_messages("off", raw)
    assert off is raw

    lit = filter_outgoing_chat_messages("light", raw)
    assert lit is not raw
    assert raw[0]["content"] == "a@b.co"
    assert lit[0]["content"] != raw[0]["content"]


def test_multimodal_text_parts_light() -> None:
    msgs: list[dict[str, Any]] = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "reach me at dev@local.test ok"},
            ],
        },
    ]
    out = filter_outgoing_chat_messages("light", msgs)
    assert "local.test" not in str(out[0]["content"][0]["text"])


def test_llm_factory_applies_filter_before_openai_adapter() -> None:
    captured: list[list[dict[str, Any]]] = []

    def fake_openai(settings: Any, messages: list[dict[str, Any]]) -> str:
        captured.append(messages)
        return "{}"

    with patch.object(llm_factory._openai_adapter, "chat_completion", side_effect=fake_openai):
        settings = AnySettings(privacy_filter_mode="light")
        llm_factory.chat_completion(
            settings,
            [{"role": "user", "content": "x@y.zz and D:\\keys\\secret.pem"}],
        )

    assert captured
    body = captured[0][0]["content"]
    assert isinstance(body, str)
    assert "secret.pem" not in body
    assert "@y.zz" not in body


def test_settings_privacy_toml_and_env_override(tmp_path, monkeypatch) -> None:
    cfg = tmp_path / "cai-agent.toml"
    cfg.write_text(
        '[privacy]\nfilter = "light"\n'
        '[llm]\nbase_url = "http://localhost/v1"\nmodel = "m"\napi_key = "k"\n'
        '[agent]\n',
        encoding="utf-8",
    )
    s = Settings.from_env(config_path=str(cfg))
    assert s.privacy_filter_mode == "light"
    monkeypatch.setenv("CAI_PRIVACY_FILTER", "strict")
    s2 = Settings.from_env(config_path=str(cfg))
    assert s2.privacy_filter_mode == "strict"


class AnySettings:
    """Minimal settings bag for dispatch tests."""

    def __init__(self, *, privacy_filter_mode: str = "off") -> None:
        self.provider = "openai_compatible"
        self.privacy_filter_mode = privacy_filter_mode
        self.base_url = "http://localhost/v1"
        self.model = "m"
        self.api_key = "k"
        self.temperature = 0.2
        self.llm_timeout_sec = 60.0
        self.http_trust_env = False
        self.mock = False
        self.llm_max_http_retries = 50
