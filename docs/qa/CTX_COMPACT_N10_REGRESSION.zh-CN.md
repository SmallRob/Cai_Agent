# CTX-COMPACT-N10：上下文压缩离线回归样本（fixtures）

## 目的

在 **不调用真实 LLM** 的前提下，用固定长会话 JSON 对以下两条路径做回归：

1. **启发式**：`evaluate_compaction_quality(messages, ...)` 默认路径（与 `sessions --compact-eval` 一致）。
2. **LLM 形摘要（模拟）**：同一批 `messages`，但向 `compact_messages` 注入 `llm_equivalent_summary`（与 graph 在 `compact_mode=llm` 时传入的 JSON 同形），用于验证 **retention + token 压缩** 在「模型返回理想摘要」时仍稳定。

`context_compaction_eval_v1` 增加可选字段 **`evaluation_variant`**：`heuristic` | `llm_simulated`（见 `context_compaction_eval_v1.schema.json`）。

## Fixture 位置

- 目录：`cai-agent/tests/fixtures/context_compaction_regression/`
- 文件：`n10_case_*.json`（每条用例一个文件）
- 说明：`README.md`

单条 fixture 结构：

- `case_id` / `notes`
- `messages`：与保存会话一致的消息列表（含 `{"tool":...,"result":...}` 的 JSON 字符串 user 消息）
- `evaluation`：`keep_tail_messages`、`summary_max_chars`、`required_markers`、`min_score`、`min_token_reduction_ratio`
- `llm_equivalent_summary`（可选）：graph LLM 摘要 JSON，用于 `llm_simulated` 路径

## 自动化命令

```powershell
$env:PYTHONPATH = "cai-agent/src"
python -m pytest -q cai-agent/tests/test_context_compaction_regression_fixtures.py
```

与既有压缩测例一并跑（推荐）：

```powershell
python -m pytest -q cai-agent/tests/test_context_compaction.py cai-agent/tests/test_graph_context_compaction.py cai-agent/tests/test_sessions_compact_eval_cli.py cai-agent/tests/test_context_compaction_regression_fixtures.py
```

全量：

```powershell
python -m pytest -q cai-agent/tests
python scripts/smoke_new_features.py
```

## 真模型（可选，人工 / CI 外）

本任务 **不要求** CI 拉真实模型。若要在发布前对比线上 profile：

1. 将某条 fixture 的 `messages` 复制到临时会话文件，或用 TUI 手工重放关键轮次。
2. 配置 `[context].compact_mode = "llm"` 与足够小的 `compact_trigger_ratio`，在 **测试 workspace** 跑一轮长对话。
3. 用 `sessions --compact-eval --json` 对 **启发式离线** 做 gate；真模型路径以 graph 的 `phase=compact` / `compact_fallback` 日志与导出会话为准。

## 维护说明

- 调整启发式或 retention 规则时，若 fixture 失败：先确认是否 **有意行为变更**，再更新 `messages` / 阈值 / `llm_equivalent_summary`，并在本文件或 PR 说明中记录原因。
- 新增用例：复制 `n10_case_*.json`，改 `case_id`，保证 `evaluation` 阈值不过松（避免回归失效）。
