# Voice: default OOS and MCP path

> Boundary RFC (Chinese canonical): [`docs/rfc/HM_07A_VOICE_BOUNDARY.zh-CN.md`](rfc/HM_07A_VOICE_BOUNDARY.zh-CN.md).  
> This repo ships **`cai-agent voice config|check`**, **`voice`** fields in **`doctor` / `api_doctor_summary`**, and a minimal **Telegram** **`gateway telegram voice-reply`** helper. Real-time duplex voice is **not** a default product commitment.

## Recommended path (MCP)

Configure STT/TTS (or combined) MCP servers in **`cai-agent.toml`** or env, same as other MCP tools. Verify with **`cai-agent doctor --json`** and **`/mcp`** in the TUI.

## Local contracts (without external MCP)

- **`cai-agent voice config --json`**: **`voice_provider_contract_v1`**
- **`cai-agent voice check --json`**: **`voice_check_v1`**, exit **0** or **2**

Sprint scheduling: [`docs/PLATFORM_SURFACES_SPRINT_PLAN.zh-CN.md`](PLATFORM_SURFACES_SPRINT_PLAN.zh-CN.md) (theme D).
