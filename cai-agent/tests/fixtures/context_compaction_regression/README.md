# Context compaction regression fixtures (CTX-COMPACT-N10)

JSON files `n10_case_*.json` are loaded by `test_context_compaction_regression_fixtures.py`.

Each file contains:

- `case_id`: stable id
- `messages`: chat history (same shape as saved sessions)
- `evaluation`: knobs for `evaluate_compaction_quality` (`keep_tail_messages`, `summary_max_chars`, `required_markers`, `min_score`, `min_token_reduction_ratio`)
- `llm_equivalent_summary` (optional): dict shaped like graph LLM compaction JSON; exercises the `summary_payload` / `llm` path **without** calling a model

To run:

```powershell
python -m pytest -q cai-agent/tests/test_context_compaction_regression_fixtures.py
```

See `docs/qa/CTX_COMPACT_N10_REGRESSION.zh-CN.md` for the full matrix and manual real-LLM notes.
