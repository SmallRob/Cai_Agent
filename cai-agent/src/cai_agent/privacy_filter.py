"""Heuristic redaction for text sent to LLM providers (CTX-COMPACT-N09).

Not NLP-based: regex-only, no disk reads, no extra network. Modes ``off`` /
``light`` / ``strict`` trim how much surrounding text stays visible after a
match."""

from __future__ import annotations

import copy
import re
from typing import Any

_MODE_LIGHT = "light"
_MODE_STRICT = "strict"

# Order: high-specific secrets first, then PII-ish, then paths.
_RE_BEARER = re.compile(r"(?i)Bearer\s+\S+")
_RE_SK_OPENAI = re.compile(r"\bsk-(?:proj|live|test)-[A-Za-z0-9]{20,}\b")
_RE_GOOGLE_API = re.compile(r"\bAIza[0-9A-Za-z\-_]{20,}\b")
_RE_AWS_KEY = re.compile(r"\bAKIA[0-9A-Z]{16}\b")
_RE_GITHUB_PAT = re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}\b")
_RE_GH_OAUTH = re.compile(r"\bgh[psuor]_[A-Za-z0-9]{20,}\b")
_RE_JWT = re.compile(r"\beyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\b")
_RE_EMAIL = re.compile(
    r"(?<![A-Za-z0-9._%+-])[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
)
_RE_PHONE = re.compile(
    r"(?<!\d)(?:\+?\d{1,3}[-.\s]?)?(?:\(?\d{2,4}\)?[-.\s]?)\d{2,4}[-.\s]?\d{2,4}[-.\s]?\d{2,6}(?!\d)",
)
_RE_WIN_PATH = re.compile(
    r"(?<![A-Za-z0-9])[A-Za-z]:\\(?:[^\\/:*?\"<>|\x00-\x1f\r\n]+\\)*[^\\/:*?\"<>|\x00-\x1f\r\n]+",
)
_RE_UNIX_ABS = re.compile(
    r"(?<![A-Za-z0-9/])(?:/(?:usr|home|Users|var|opt|mnt|tmp|etc|root)(?:/[^ \t\r\n\"'|<>]+)+)",
)
_RE_HEX_STRICT = re.compile(r"\b[0-9a-fA-F]{40,64}\b")
_RE_SSN_STRICT = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")


def _edge_keep(original: str, keep_pre: int, keep_suf: int) -> str:
    s = original
    if len(s) <= keep_pre + keep_suf + 4:
        return "⟨redacted⟩"
    return f"{s[:keep_pre]}…{s[-keep_suf:]}"


def _apply_pattern(pattern: re.Pattern[str], text: str, keep_pre: int, keep_suf: int) -> str:
    def _repl(m: re.Match[str]) -> str:
        return _edge_keep(m.group(0), keep_pre, keep_suf)

    return pattern.sub(_repl, text)


def redact_outgoing_text(text: str, mode: str) -> str:
    """Return ``text`` with heuristic redactions applied (or unchanged if ``off``)."""
    m = (mode or "off").strip().lower()
    if m == "off" or not m:
        return text
    if m not in (_MODE_LIGHT, _MODE_STRICT):
        return text

    pre, suf = (4, 4) if m == _MODE_LIGHT else (2, 2)
    out = text

    # Secrets / credentials
    for pat in (
        _RE_JWT,
        _RE_BEARER,
        _RE_SK_OPENAI,
        _RE_GOOGLE_API,
        _RE_AWS_KEY,
        _RE_GITHUB_PAT,
        _RE_GH_OAUTH,
    ):
        out = _apply_pattern(pat, out, pre, suf)

    out = _apply_pattern(_RE_EMAIL, out, pre, suf)
    out = _apply_pattern(_RE_PHONE, out, pre, suf)

    out = _apply_pattern(_RE_WIN_PATH, out, pre, suf)
    out = _apply_pattern(_RE_UNIX_ABS, out, pre, suf)

    if m == _MODE_STRICT:
        out = _apply_pattern(_RE_HEX_STRICT, out, pre, suf)
        out = _apply_pattern(_RE_SSN_STRICT, out, pre, suf)

    return out


def _filter_content_value(content: Any, mode: str) -> Any:
    if isinstance(content, str):
        return redact_outgoing_text(content, mode)
    if isinstance(content, list):
        out: list[Any] = []
        for it in content:
            if isinstance(it, dict):
                d = dict(it)
                if str(it.get("type") or "") == "text" and isinstance(it.get("text"), str):
                    d["text"] = redact_outgoing_text(it["text"], mode)
                elif isinstance(it.get("content"), str):
                    d["content"] = redact_outgoing_text(it["content"], mode)
                out.append(d)
            elif isinstance(it, str):
                out.append(redact_outgoing_text(it, mode))
            else:
                out.append(copy.deepcopy(it))
        return out
    return content


def filter_outgoing_chat_messages(
    mode: str,
    messages: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Return a shallow-deep copy of ``messages`` with string ``content`` redacted."""
    m = (mode or "off").strip().lower()
    if m == "off" or not m or m not in (_MODE_LIGHT, _MODE_STRICT):
        return messages

    out: list[dict[str, Any]] = []
    for msg in messages:
        if not isinstance(msg, dict):
            out.append(msg)
            continue
        nm = dict(msg)
        if "content" in nm:
            nm["content"] = _filter_content_value(nm.get("content"), m)
        out.append(nm)
    return out


__all__ = ["filter_outgoing_chat_messages", "redact_outgoing_text"]
