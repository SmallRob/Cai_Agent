"""Gateway 生命周期 MVP（Hermes S6-01）：setup / start / status / stop。"""

from __future__ import annotations

import json
import os
import re
import secrets
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from cai_agent import __version__

CONFIG_NAME = "telegram-config.json"
PID_NAME = "telegram-webhook.pid"
CONFIG_SCHEMA = "gateway_telegram_config_v1"
PID_SCHEMA = "gateway_telegram_pid_v1"
STATUS_SCHEMA = "gateway_lifecycle_status_v1"
PROXY_ROUTE_SCHEMA = "gateway_proxy_route_v1"
FEDERATION_ROUTE_AUDIT_SCHEMA = "gateway_federation_route_audit_v1"
FEDERATION_EXECUTE_ENV = "CAI_GATEWAY_FEDERATION_ROUTE_EXECUTE"
FEDERATION_ALLOWLIST_ENV = "CAI_GATEWAY_FEDERATION_ALLOWED_WORKSPACES"
FEDERATION_EXECUTE_TOKEN_ENV = "CAI_GATEWAY_FEDERATION_ROUTE_EXECUTE_TOKEN"


def _env_truthy(raw: str | None) -> bool:
    return str(raw or "").strip().lower() in ("1", "true", "yes", "on")


def _federation_execute_enabled() -> bool:
    return _env_truthy(os.environ.get(FEDERATION_EXECUTE_ENV))


def _split_workspace_allowlist(raw: str | None) -> list[Path]:
    if not raw or not str(raw).strip():
        return []
    parts = re.split(r"[\n;|]+", str(raw))
    out: list[Path] = []
    for p in parts:
        s = str(p).strip()
        if not s:
            continue
        out.append(Path(s).expanduser().resolve())
    return out


def _path_allowed_federation_target(*, source: Path, target: Path, allowlist: list[Path]) -> bool:
    s = source.resolve()
    t = target.resolve()
    if t == s:
        return True
    if not allowlist:
        return False
    for prefix in allowlist:
        try:
            t.relative_to(prefix.resolve())
            return True
        except ValueError:
            continue
    return False


def _append_federation_route_audit(source_root: Path, record: dict[str, Any]) -> Path:
    gdir = _gateway_dir(source_root)
    path = gdir / "federation-route-audit.jsonl"
    line = json.dumps(record, ensure_ascii=False) + "\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(line)
    return path


def _gateway_dir(root: Path) -> Path:
    d = (root / ".cai" / "gateway").resolve()
    d.mkdir(parents=True, exist_ok=True)
    return d


def _read_map_file(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {"schema_version": "gateway_telegram_map_v1", "bindings": {}, "allowed_chat_ids": []}
    try:
        obj = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {"schema_version": "gateway_telegram_map_v1", "bindings": {}, "allowed_chat_ids": []}
    if not isinstance(obj, dict):
        return {"schema_version": "gateway_telegram_map_v1", "bindings": {}, "allowed_chat_ids": []}
    if not isinstance(obj.get("bindings"), dict):
        obj["bindings"] = {}
    if not isinstance(obj.get("allowed_chat_ids"), list):
        obj["allowed_chat_ids"] = []
    obj.setdefault("schema_version", "gateway_telegram_map_v1")
    return obj


def config_path(root: Path | str) -> Path:
    return _gateway_dir(Path(root)) / CONFIG_NAME


def pid_path(root: Path | str) -> Path:
    return _gateway_dir(Path(root)) / PID_NAME


def load_telegram_config(root: Path | str) -> dict[str, Any] | None:
    p = config_path(root)
    if not p.is_file():
        return None
    try:
        obj = json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None
    return obj if isinstance(obj, dict) else None


def save_telegram_config(root: Path | str, doc: dict[str, Any]) -> Path:
    p = config_path(root)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return p


def default_serve_block() -> dict[str, Any]:
    return {
        "host": "127.0.0.1",
        "port": 18765,
        "max_events": 0,
        "create_missing": False,
        "execute_on_update": False,
        "reply_on_execution": False,
        "reply_on_deny": False,
        "goal_template": "用户({user_id})在 chat({chat_id}) 发送消息：{text}",
        "reply_template": "执行完成 ok={ok}\n{answer}",
        "deny_message": "此 CAI Agent Bot 未授权本对话。",
    }


def build_setup_payload(
    *,
    root: Path,
    use_env_token: bool,
    bot_token: str | None,
    workspace: str | None,
    serve: dict[str, Any] | None,
    allow_chat_ids: list[str] | None,
) -> dict[str, Any]:
    """写入 ``gateway_telegram_config_v1`` 并可同步 ``allowed_chat_ids`` 到映射文件。"""
    base = root.resolve()
    ws = str(Path(workspace or ".").expanduser().resolve())
    sw = {**default_serve_block(), **(serve or {})}
    token_literal = (str(bot_token).strip() if bot_token else "") or None
    doc: dict[str, Any] = {
        "schema_version": CONFIG_SCHEMA,
        "generated_at": datetime.now(UTC).isoformat(),
        "cai_agent_version": __version__,
        "workspace": ws,
        "use_env_token": bool(use_env_token),
        "bot_token_set_in_file": bool(token_literal),
        "serve_webhook": sw,
    }
    if token_literal:
        doc["bot_token"] = token_literal
    save_telegram_config(base, doc)

    if allow_chat_ids:
        map_p = _gateway_dir(base) / "telegram-session-map.json"
        mdoc = _read_map_file(map_p)
        cur = [str(x).strip() for x in (mdoc.get("allowed_chat_ids") or []) if str(x).strip()]
        for c in allow_chat_ids:
            s = str(c).strip()
            if s and s not in cur:
                cur.append(s)
        mdoc["allowed_chat_ids"] = sorted(set(cur))
        mdoc.setdefault("schema_version", "gateway_telegram_map_v1")
        mdoc.setdefault("bindings", mdoc.get("bindings") if isinstance(mdoc.get("bindings"), dict) else {})
        map_p.parent.mkdir(parents=True, exist_ok=True)
        map_p.write_text(json.dumps(mdoc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    return {
        "schema_version": CONFIG_SCHEMA,
        "ok": True,
        "config_path": str(config_path(base)),
        "workspace": ws,
        "use_env_token": bool(use_env_token),
        "allow_chat_ids_applied": list(allow_chat_ids or []),
    }


def _pid_alive(pid: int) -> bool:
    if pid <= 0:
        return False
    if os.name == "nt":
        try:
            r = subprocess.run(
                ["tasklist", "/FI", f"PID eq {pid}"],
                capture_output=True,
                text=True,
                timeout=8,
                check=False,
            )
            return str(pid) in (r.stdout or "")
        except Exception:
            return False
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def _read_pid_doc(root: Path) -> dict[str, Any] | None:
    p = pid_path(root)
    if not p.is_file():
        return None
    try:
        o = json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None
    return o if isinstance(o, dict) else None


def build_gateway_summary_payload(root: Path | str) -> dict[str, Any]:
    """Shared read-side gateway summary for board / ops / gateway status."""
    base = Path(root).expanduser().resolve()
    cfg_path = config_path(base)
    map_path = _gateway_dir(base) / "telegram-session-map.json"
    mdoc = _read_map_file(map_path)
    binds = mdoc.get("bindings") if isinstance(mdoc.get("bindings"), dict) else {}
    allowed = [str(x) for x in (mdoc.get("allowed_chat_ids") or []) if str(x).strip()]
    pid_doc = _read_pid_doc(base)
    pid = int(pid_doc.get("pid") or 0) if isinstance(pid_doc, dict) else 0
    alive = _pid_alive(pid) if pid else False
    return {
        "schema_version": "gateway_summary_v1",
        "workspace": str(base),
        "config_path": str(cfg_path),
        "config_exists": cfg_path.is_file(),
        "map_path": str(map_path),
        "bindings_count": len(binds),
        "allowed_chat_ids_count": len(allowed),
        "allowed_chat_ids": allowed,
        "allowlist_enabled": bool(allowed),
        "webhook_pid": pid or None,
        "webhook_running": alive,
        "status": "running" if alive else ("configured" if cfg_path.is_file() else "not_configured"),
    }


def build_status_payload(root: Path | str) -> dict[str, Any]:
    base = Path(root).expanduser().resolve()
    summary = build_gateway_summary_payload(base)
    return {
        "schema_version": STATUS_SCHEMA,
        "generated_at": datetime.now(UTC).isoformat(),
        "workspace": str(base),
        "config_path": str(config_path(base)),
        "config_exists": config_path(base).is_file(),
        "pid_path": str(pid_path(base)),
        "webhook_pid": summary.get("webhook_pid"),
        "webhook_running": summary.get("webhook_running"),
        "bindings_count": summary.get("bindings_count"),
        "allowed_chat_ids": summary.get("allowed_chat_ids"),
        "allowlist_enabled": summary.get("allowlist_enabled"),
        "gateway_summary": summary,
    }


def build_gateway_proxy_route_preview(
    *,
    root: Path | str,
    platform: str,
    channel_id: str | None,
    target_workspace: str | None,
    target_profile_id: str | None,
    dry_run: bool = True,
    execute_token: str | None = None,
) -> dict[str, Any]:
    """HM-N07-D03 / GW-N02-D02: gateway proxy/routing preview; optional federation commit.

    When ``dry_run`` is false, requires ``CAI_GATEWAY_FEDERATION_ROUTE_EXECUTE`` truthy,
    optional ``CAI_GATEWAY_FEDERATION_ROUTE_EXECUTE_TOKEN`` (must match ``execute_token``),
    target workspace allowlist (same workspace always allowed; cross-root needs
    ``CAI_GATEWAY_FEDERATION_ALLOWED_WORKSPACES``), and a resolvable target profile id.
    Success appends ``gateway_federation_route_audit_v1`` JSONL under
    ``.cai/gateway/federation-route-audit.jsonl`` (no LLM or gateway process spawn).
    """
    base = Path(root).expanduser().resolve()
    src = build_gateway_summary_payload(base)
    channel = str(channel_id or "").strip() or "default"
    plat = str(platform or "").strip().lower() or "unknown"
    target_resolved = Path(str(target_workspace or base)).expanduser().resolve()
    profile_id = str(target_profile_id or "").strip() or "default"
    out: dict[str, Any] = {
        "schema_version": PROXY_ROUTE_SCHEMA,
        "generated_at": datetime.now(UTC).isoformat(),
        "dry_run": bool(dry_run),
        "source": {
            "workspace": str(base),
            "gateway_status": src.get("status"),
            "platform": plat,
            "channel_id": channel,
        },
        "route": {
            "target_workspace": str(target_resolved),
            "target_profile_id": profile_id,
            "decision": "route_preview_only",
        },
    }
    if dry_run:
        return out

    if not _federation_execute_enabled():
        out["ok"] = False
        out["error"] = "federation_execute_disabled"
        out["message"] = (
            f"Set {FEDERATION_EXECUTE_ENV}=1 to allow dry_run:false route-preview commits "
            "(GW-N02-D02)."
        )
        return out

    expected_tok = str(os.environ.get(FEDERATION_EXECUTE_TOKEN_ENV) or "").strip()
    if expected_tok:
        got = str(execute_token or "").strip()
        if not secrets.compare_digest(expected_tok, got):
            out["ok"] = False
            out["error"] = "federation_execute_token_mismatch"
            out["message"] = "CAI_GATEWAY_FEDERATION_ROUTE_EXECUTE_TOKEN is set but the execute token did not match."
            return out

    allow_roots = _split_workspace_allowlist(os.environ.get(FEDERATION_ALLOWLIST_ENV))
    if not _path_allowed_federation_target(source=base, target=target_resolved, allowlist=allow_roots):
        out["ok"] = False
        out["error"] = "target_workspace_not_allowed"
        out["message"] = (
            "Cross-workspace federation route requires the target under "
            f"{FEDERATION_ALLOWLIST_ENV}, or target must equal the source workspace."
        )
        return out

    from cai_agent.config import load_agent_settings_for_workspace

    try:
        tset = load_agent_settings_for_workspace(workspace=target_resolved)
    except Exception as e:
        out["ok"] = False
        out["error"] = "target_settings_load_failed"
        out["message"] = str(e)[:400]
        return out

    profile_ids = {p.id for p in tset.profiles}
    if profile_id not in profile_ids:
        out["ok"] = False
        out["error"] = "target_profile_not_found"
        out["message"] = f"Profile id {profile_id!r} not defined in target workspace."
        return out

    audit_record: dict[str, Any] = {
        "schema_version": FEDERATION_ROUTE_AUDIT_SCHEMA,
        "recorded_at": datetime.now(UTC).isoformat(),
        "cai_agent_version": __version__,
        "source_workspace": str(base),
        "platform": plat,
        "channel_id": channel,
        "target_workspace": str(target_resolved),
        "target_profile_id": profile_id,
    }
    audit_path = _append_federation_route_audit(base, audit_record)
    out["ok"] = True
    route_doc = out.get("route") if isinstance(out.get("route"), dict) else {}
    route_doc["decision"] = "federation_route_committed"
    out["route"] = route_doc
    out["execution"] = {
        "schema_version": "gateway_federation_route_execution_v1",
        "ok": True,
        "audit_file": str(audit_path),
        "audit_schema_version": FEDERATION_ROUTE_AUDIT_SCHEMA,
    }
    return out


def start_webhook_subprocess(root: Path | str) -> dict[str, Any]:
    """根据 ``telegram-config.json`` 启动 ``serve-webhook`` 子进程并写入 PID 文件。"""
    base = Path(root).expanduser().resolve()
    cfg = load_telegram_config(base)
    if not cfg:
        return {"schema_version": "gateway_lifecycle_start_v1", "ok": False, "error": "config_missing"}
    sw = cfg.get("serve_webhook") if isinstance(cfg.get("serve_webhook"), dict) else {}
    host = str(sw.get("host") or "127.0.0.1")
    port = int(sw.get("port") or 18765)
    max_ev = int(sw.get("max_events") or 0)
    cmd: list[str] = [
        sys.executable,
        "-m",
        "cai_agent",
        "gateway",
        "telegram",
        "serve-webhook",
        "--host",
        host,
        "--port",
        str(port),
        "--max-events",
        str(max_ev),
    ]
    if bool(sw.get("create_missing")):
        cmd.append("--create-missing")
    if bool(sw.get("execute_on_update")):
        cmd.append("--execute-on-update")
    if bool(sw.get("reply_on_execution")):
        cmd.append("--reply-on-execution")
    if bool(sw.get("reply_on_deny")):
        cmd.append("--reply-on-deny")
    gt = str(sw.get("goal_template") or "").strip()
    if gt:
        cmd.extend(["--goal-template", gt])
    rt = str(sw.get("reply_template") or "").strip()
    if rt:
        cmd.extend(["--reply-template", rt])
    dm = str(sw.get("deny_message") or "").strip()
    if dm:
        cmd.extend(["--deny-message", dm])
    tok = str(cfg.get("bot_token") or "").strip()
    if tok:
        cmd.extend(["--telegram-bot-token", tok])

    gdir = _gateway_dir(base)
    out_log = gdir / "telegram-webhook.stdout.log"
    err_log = gdir / "telegram-webhook.stderr.log"
    out_log.parent.mkdir(parents=True, exist_ok=True)
    with out_log.open("ab") as fo, err_log.open("ab") as fe:
        kwargs: dict[str, Any] = {
            "cwd": str(base),
            "stdout": fo,
            "stderr": fe,
        }
        if os.name == "nt":
            cf = getattr(subprocess, "DETACHED_PROCESS", 0)
            cf |= getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
            kwargs["creationflags"] = cf
        else:
            kwargs["start_new_session"] = True
        proc = subprocess.Popen(cmd, **kwargs)  # noqa: S603
    pid_doc = {
        "schema_version": PID_SCHEMA,
        "pid": proc.pid,
        "started_at": datetime.now(UTC).isoformat(),
        "cmd": cmd,
        "workspace": str(base),
    }
    pid_path(base).write_text(json.dumps(pid_doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {
        "schema_version": "gateway_lifecycle_start_v1",
        "ok": True,
        "pid": proc.pid,
        "pid_file": str(pid_path(base)),
        "stdout_log": str(out_log),
        "stderr_log": str(err_log),
    }


def stop_webhook_subprocess(root: Path | str) -> dict[str, Any]:
    base = Path(root).expanduser().resolve()
    doc = _read_pid_doc(base)
    pid = int(doc.get("pid") or 0) if isinstance(doc, dict) else 0
    if pid <= 0:
        return {"schema_version": "gateway_lifecycle_stop_v1", "ok": False, "error": "no_pid_file"}
    if not _pid_alive(pid):
        pid_path(base).unlink(missing_ok=True)
        return {"schema_version": "gateway_lifecycle_stop_v1", "ok": True, "stopped": False, "reason": "not_running"}
    try:
        if os.name == "nt":
            subprocess.run(
                ["taskkill", "/PID", str(pid), "/T", "/F"],
                capture_output=True,
                text=True,
                timeout=30,
                check=False,
            )
        else:
            os.kill(pid, 15)
    except Exception as e:
        return {"schema_version": "gateway_lifecycle_stop_v1", "ok": False, "error": "stop_failed", "message": str(e)}
    pid_path(base).unlink(missing_ok=True)
    return {"schema_version": "gateway_lifecycle_stop_v1", "ok": True, "stopped": True, "pid": pid}
