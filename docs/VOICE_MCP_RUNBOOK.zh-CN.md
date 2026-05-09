# Voice：默认 OOS 与 MCP 接入说明

> 边界 RFC：**[`docs/rfc/HM_07A_VOICE_BOUNDARY.zh-CN.md`](rfc/HM_07A_VOICE_BOUNDARY.zh-CN.md)**。  
> 本仓提供 **`cai-agent voice config|check`**、**`doctor`/`api_doctor_summary` 中的 `voice`** 字段，以及 **Telegram** 侧最小 **`gateway telegram voice-reply`**（需 Bot Token / `voice_file_id` 等），**不**将实时双向语音作为默认产品线。

## 推荐路径（MCP）

1. 在 **`cai-agent.toml`** 或环境变量中配置 MCP 服务器（STT/TTS 任选其一或组合），与现有 **`/mcp`**、**`mcp-check`** 流程一致。
2. 运行 **`cai-agent doctor --json`**，确认 **`voice`** 或 MCP 相关节无阻塞性错误。
3. 在 TUI 用 **`/mcp`** 或项目文档中的 **`WEBSEARCH_NOTEBOOK_MCP`** 同类方式核对 MCP 工具是否已暴露给 Agent。

具体 MCP 服务器名称与配置因供应商而异；以各 STT/TTS 官方 MCP 或自建桥接为准。

## 本机契约（无 MCP 时）

- **`cai-agent voice config --json`**：输出 **`voice_provider_contract_v1`**（配置态摘要）。
- **`cai-agent voice check --json`**：输出 **`voice_check_v1`**，按配置完整性返回退出码 **0** 或 **2**。

## 相关文档

- Sprint 排期：**[`PLATFORM_SURFACES_SPRINT_PLAN.zh-CN.md`](PLATFORM_SURFACES_SPRINT_PLAN.zh-CN.md)**（主题 D · Voice）
