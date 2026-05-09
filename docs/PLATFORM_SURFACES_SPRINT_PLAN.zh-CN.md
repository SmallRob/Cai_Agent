# 平台外表面 Sprint 计划（Ops / Gateway / Runtime / Voice）

> 与 [`PRODUCT_PLAN.zh-CN.md`](PRODUCT_PLAN.zh-CN.md) 〇.2、[`PRODUCT_GAP_ANALYSIS.zh-CN.md`](PRODUCT_GAP_ANALYSIS.zh-CN.md) 对齐。  
> **执行 backlog 登记**：[`ROADMAP_EXECUTION.zh-CN.md`](ROADMAP_EXECUTION.zh-CN.md) §10；**当前开发队列**：[`DEVELOPER_TODOS.zh-CN.md`](DEVELOPER_TODOS.zh-CN.md)。

## 目标（四线并行、分阶段）

| 主题 | 当前基线 | Sprint 目标 | 边界 |
|------|----------|-------------|------|
| **A. 运营 Web UI / Operator** | `ops serve`：dashboard JSON/HTML、SSE/poll、`interactions` 受控写、RBAC、多 workspace 枚举 | **更完整的 operator 控制面**：跨 workspace 操作路由一致、租户/角色审计可查询、侧车可观测（health）与部署 runbook | 不引入第二套状态源；写路径保持可审计 |
| **B. Gateway 全量** | Discord/Slack/Teams MVP；`slash-catalog`、`federation-summary`、`route-preview`（dry-run） | **Slash 在真实平台上的注册与部署检查**（清单 + CLI/CI 可选）；**联邦从预览到可选执行路径**（须显式开关与安全评审） | 不默认铺 15+ 平台；一次收敛 1～2 个平台 |
| **C. 运行后端（云）** | local / docker / SSH 已产品化；[`CLOUD_RUNTIME_OOS.zh-CN.md`](CLOUD_RUNTIME_OOS.zh-CN.md) 条件立项 | **Modal / Daytona 等**：仅当门槛满足后做 **Design → POC → 可选后端**；接口对齐 `runtime_backend_interface_v1` | 未过门槛不实现真实云执行 |
| **D. Voice** | 默认 **OOS**；[`HM_07A_VOICE_BOUNDARY.zh-CN.md`](rfc/HM_07A_VOICE_BOUNDARY.zh-CN.md)；`voice config/check`；Telegram `voice-reply` 最小闭环 | **默认交付走 MCP**；维护 **MCP 接入 runbook** 与 README/doctor 指针；不承诺实时双向语音产品线 | 不重实现云端 STT/TTS |

## 建议迭代顺序（2～3 周为一轮）

1. **A1**：侧车 `GET /v1/ops/healthz`（无 Bearer，便于探活）+ README/Web 文档同步（本轮已启动）。
2. **A2**：`OPS-N02-D01`  operator 路由与跨 workspace 写路径契约（OpenAPI 片段 + pytest）。
3. **B1**：`GW-N02-D01`  选定平台（建议 Slack 或 Discord）Slash **部署检查清单** + `gateway prod-status` / doctor 扩展字段。
4. **B2**：`GW-N02-D02`  `route-preview` 与真实执行链路的 **feature flag** 对齐（设计评审后实现）。
5. **C1**：`HM-N12-D01`  复核 `CLOUD_RUNTIME_OOS` 门槛；通过后再做 Modal/Daytona **stub + 配置键草案**。
6. **D1**：`HM-N08-M01`  Voice MCP runbook 与配置示例（无默认实时语音）。

## 验证（每合并一项）

- `python -m pytest -q cai-agent/tests`（相关子集 + 全量视改动面）
- `python scripts/smoke_new_features.py`
- 涉及 HTTP：补 `test_ops_http_server.py` / `test_api_http_server.py` 或 gateway 套件

## 文档回写

每项合并后至少更新：`CHANGELOG.md` / `CHANGELOG.zh-CN.md`；触及产品边界时更新 `PRODUCT_PLAN`、`PRODUCT_GAP_ANALYSIS`、`PARITY_MATRIX` 对应行。
