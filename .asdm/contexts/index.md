# 项目顶层索引

> **重要**：本文件是 AI 启动时必读的第一个文件，用于建立对项目的全局认知。
> **大小限制**：< 2KB（必须保持精简）

## 1. 项目概览

**项目名称**：CAI Agent
**一句话描述**：基于 LangGraph 的终端编码代理，通过自然语言与工作区交互，支持 OpenAI 兼容的 API 端点
**技术栈定位**：Python + LangGraph + Textual TUI

## 2. 技术栈

| 类别 | 技术 |
|------|------|
| 主要语言 | Python 3.11+ |
| 核心框架 | LangGraph, httpx, Textual |
| 数据库 | SQLite (FTS5) |
| 缓存 | 内存缓存 |
| 构建工具 | setuptools, pip |
| 测试框架 | pytest |

## 3. 领域划分

| 领域 | 职责 | 入口 |
|------|------|------|
| 核心代理 | 代理执行、工作流、技能管理 | [domains/core-agent.md] |
| 工具与模型 | 工具提供、模型管理、LLM集成 | [domains/tools-models.md] |
| 配置与上下文 | 配置管理、上下文处理、会话 | [domains/config-context.md] |
| 网关与集成 | Slack、Teams、Discord等网关 | [domains/gateways.md] |
| 运行时与执行 | 运行时环境、沙盒、调度 | [domains/runtime.md] |
| 观察与运维 | 指标、监控、运维仪表板 | [domains/observe-ops.md] |
| 安全与质量 | 权限、安全扫描、质量门 | [domains/security-quality.md] |
| 用户界面 | TUI、导出、看板 | [domains/user-interface.md] |

## 4. 构建指南

```bash
# 安装
cd cai-agent && pip install -e .

# 测试
pytest

# 启动TUI
python -m cai-agent ui -w "$PWD"

# 运行命令
cai-agent run "Summarize this repository layout"
```

## 5. 导航指引

- **理解项目**：阅读本文件（L1）
- **修改某领域**：阅读对应领域索引（L2）
- **执行具体任务**：按需阅读详细内容（L3）

---

*本文件由 Context Builder v0.3 生成，保持精简以确保 AI 高效加载*