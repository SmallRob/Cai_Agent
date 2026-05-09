"""CTX-COMPACT-N10: offline long-session fixtures for context compaction regression.

Loads ``n10_case_*.json`` under ``fixtures/context_compaction_regression/`` and runs
``evaluate_compaction_quality`` in heuristic mode and (when present) with a fixed
``summary_payload`` that simulates the graph LLM compaction path without HTTP.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from cai_agent.context_compaction import evaluate_compaction_quality

_FIXTURE_DIR = Path(__file__).resolve().parent / "fixtures" / "context_compaction_regression"


def _case_files() -> list[Path]:
    return sorted(_FIXTURE_DIR.glob("n10_case_*.json"))


def _load_case(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(data.get("messages"), list)
    ev = data.get("evaluation")
    assert isinstance(ev, dict)
    return data


@pytest.mark.parametrize("fixture_path", _case_files(), ids=lambda p: p.stem)
def test_n10_fixture_heuristic_eval_passes(fixture_path: Path) -> None:
    case = _load_case(fixture_path)
    ev = case["evaluation"]
    result = evaluate_compaction_quality(
        case["messages"],
        keep_tail_messages=int(ev["keep_tail_messages"]),
        summary_max_chars=int(ev["summary_max_chars"]),
        required_markers=tuple(ev.get("required_markers") or ()),
        min_score=float(ev["min_score"]),
        min_token_reduction_ratio=float(ev["min_token_reduction_ratio"]),
    ).payload
    assert result.get("evaluation_variant") == "heuristic"
    assert result.get("schema_version") == "context_compaction_eval_v1"
    assert result.get("passed") is True, json.dumps(result, ensure_ascii=False, indent=2)


@pytest.mark.parametrize("fixture_path", _case_files(), ids=lambda p: p.stem)
def test_n10_fixture_llm_simulated_eval_passes(fixture_path: Path) -> None:
    case = _load_case(fixture_path)
    llm = case.get("llm_equivalent_summary")
    if not isinstance(llm, dict) or not llm:
        pytest.skip("no llm_equivalent_summary")
    ev = case["evaluation"]
    result = evaluate_compaction_quality(
        case["messages"],
        keep_tail_messages=int(ev["keep_tail_messages"]),
        summary_max_chars=int(ev["summary_max_chars"]),
        required_markers=tuple(ev.get("required_markers") or ()),
        min_score=float(ev["min_score"]),
        min_token_reduction_ratio=float(ev["min_token_reduction_ratio"]),
        summary_payload=llm,
        summary_source="llm",
    ).payload
    assert result.get("evaluation_variant") == "llm_simulated"
    assert result.get("schema_version") == "context_compaction_eval_v1"
    assert result.get("passed") is True, json.dumps(result, ensure_ascii=False, indent=2)


def test_n10_fixture_directory_non_empty() -> None:
    assert _case_files(), f"expected n10_case_*.json under {_FIXTURE_DIR}"
