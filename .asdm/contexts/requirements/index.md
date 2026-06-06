# CAI Agent - 系统能力概览

> 基于 LangGraph 的本地 LLM Agent，集成 CLI/TUI 界面、多模型网关、工具调度与会话管理。

## 功能模块

| 模块 | 核心文件 | 职责 |
|------|----------|------|
| [核心 Agent](domains/core-agent.md) | graph.py, agents.py, workflow.py | LangGraph 状态图、Agent 循环、任务调度 |
| [LLM 集成](domains/llm-integration.md) | llm.py, llm_factory.py, model_gateway.py | 多模型接入、路由策略、API 适配 |
| [工具系统](domains/tools.md) | tools.py, tool_provider.py, sandbox.py | 工具注册、调度、沙箱执行 |
| [TUI 界面](domains/tui.md) | tui.py, tui_*.py | 终端 UI、面板、补全、任务看板 |
| [配置管理](domains/config.md) | config.py, profiles.py, models.py | TOML/环境变量分层配置、模型 Profile |
| [会话管理](domains/session.md) | session.py, context.py, context_compaction.py | 会话生命周期、上下文压缩 |
| [记忆系统](domains/memory.md) | memory.py, recall_fts5.py | 长期记忆、FTS5 检索、TTL 策略 |
| [网关集成](domains/gateway.md) | gateway_*.py | Discord/Slack/Teams/Email 等平台接入 |
| [MCP 支持](domains/mcp.md) | mcp_serve.py, mcp_presets.py | MCP 协议桥接、工具预设 |
| [安全权限](domains/security.md) | permissions.py, security_scan.py, sandbox.py | 权限控制、安全扫描、沙箱隔离 |
| [可观测性](domains/observability.md) | metrics.py, ops_*.py, observe_*.py | 指标采集、Ops 面板、报告导出 |
| [插件生态](domains/plugins.md) | plugin_registry.py, skill_registry.py | 插件注册、Skill 进化、跨平台导出 |

## 技术栈

- **语言**: Python 3.11+
- **核心框架**: LangGraph (StateGraph)
- **HTTP**: httpx
- **TUI**: textual
- **配置**: TOML + 环境变量
- **存储**: SQLite (FTS5)

## 导航

- 项目根目录: `cai-agent/`
- 源码: `cai-agent/src/cai_agent/`
- 测试: `cai-agent/tests/`
- 文档: `docs/`
