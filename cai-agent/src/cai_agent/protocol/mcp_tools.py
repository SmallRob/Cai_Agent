"""MCP 工具定义模块。

定义 Cai Agent 暴露给 MCP Client 的工具列表和参数规范。
"""

from __future__ import annotations

from typing import Any

# ---------------------------------------------------------------------------
# MCP 工具定义
# ---------------------------------------------------------------------------

CAI_AGENT_MCP_TOOLS: list[dict[str, Any]] = [
    {
        "name": "cai_agent_run",
        "description": "执行 Cai Agent 任务。接受自然语言目标描述，Agent 会自动分析代码库、制定计划并执行。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "goal": {
                    "type": "string",
                    "description": "任务目标的自然语言描述，例如：'修复登录页面的样式问题' 或 '为 UserService 添加单元测试'",
                },
                "workspace": {
                    "type": "string",
                    "description": "工作区根目录路径。如果不指定，使用环境变量 CAI_WORKSPACE 或当前目录。",
                },
                "model": {
                    "type": "string",
                    "description": "使用的 LLM 模型名称，例如 'gpt-4o'、'claude-3-opus'。如果不指定，使用默认配置。",
                },
                "max_iterations": {
                    "type": "integer",
                    "description": "最大迭代次数，默认为 15。增大此值可以让 Agent 尝试更多方案。",
                    "minimum": 1,
                    "maximum": 50,
                    "default": 15,
                },
            },
            "required": ["goal"],
        },
    },
    {
        "name": "cai_agent_plan",
        "description": "生成实施计划。分析目标并生成详细的、可执行的实施计划，包括步骤、依赖和风险评估。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "goal": {
                    "type": "string",
                    "description": "规划目标的自然语言描述，例如：'设计一个用户认证系统'",
                },
                "workspace": {
                    "type": "string",
                    "description": "工作区根目录路径。",
                },
                "mode": {
                    "type": "string",
                    "enum": ["quick", "full"],
                    "description": "规划模式：'quick' 快速生成大纲，'full' 生成详细计划（默认）。",
                    "default": "full",
                },
                "model": {
                    "type": "string",
                    "description": "使用的 LLM 模型名称。",
                },
            },
            "required": ["goal"],
        },
    },
    {
        "name": "cai_agent_workflow",
        "description": "运行预定义工作流或自定义工作流。支持多步骤、多角色的复杂任务编排。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "goal": {
                    "type": "string",
                    "description": "工作流目标描述。",
                },
                "workflow_id": {
                    "type": "string",
                    "description": "预定义工作流 ID 或模板名，例如 'explore-implement-review'、'doc-generate'。",
                },
                "workflow_json": {
                    "type": "string",
                    "description": "自定义工作流 JSON 定义。如果不指定 workflow_id，则使用此自定义工作流。",
                },
                "workspace": {
                    "type": "string",
                    "description": "工作区根目录路径。",
                },
                "model": {
                    "type": "string",
                    "description": "使用的 LLM 模型名称。",
                },
                "timeout_sec": {
                    "type": "number",
                    "description": "超时时间（秒），默认 600。",
                    "minimum": 30,
                    "maximum": 3600,
                    "default": 600,
                },
            },
            "required": ["goal"],
        },
    },
    {
        "name": "cai_agent_doc_generate",
        "description": "生成项目文档。支持生成 README、API 文档、架构文档、变更日志等多种类型。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "doc_type": {
                    "type": "string",
                    "enum": ["readme", "api", "architecture", "changelog", "contributing"],
                    "description": "文档类型：readme(项目说明)、api(API文档)、architecture(架构文档)、changelog(变更日志)、contributing(贡献指南)",
                },
                "output": {
                    "type": "string",
                    "description": "输出文件路径。如果不指定，根据文档类型使用默认路径。",
                },
                "source_dirs": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "源代码目录列表，默认为当前目录。",
                },
                "language": {
                    "type": "string",
                    "enum": ["zh-CN", "en"],
                    "description": "文档语言，默认 zh-CN。",
                    "default": "zh-CN",
                },
                "goal_extra": {
                    "type": "string",
                    "description": "额外的生成要求，例如 '重点说明部署流程'。",
                },
                "workspace": {
                    "type": "string",
                    "description": "工作区根目录路径。",
                },
                "model": {
                    "type": "string",
                    "description": "使用的 LLM 模型名称。",
                },
            },
            "required": ["doc_type"],
        },
    },
    {
        "name": "cai_agent_doc_review",
        "description": "审查文档质量。检查文档的完整性、准确性、可读性和规范性，并给出评分和改进建议。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "要审查的文档文件路径，相对于工作区根目录。",
                },
                "workspace": {
                    "type": "string",
                    "description": "工作区根目录路径。",
                },
                "model": {
                    "type": "string",
                    "description": "使用的 LLM 模型名称。",
                },
            },
            "required": ["file_path"],
        },
    },
    {
        "name": "cai_agent_doctor",
        "description": "诊断 Cai Agent 配置和环境。检查 LLM 密钥、工具可用性、工作区状态等。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "workspace": {
                    "type": "string",
                    "description": "工作区根目录路径。",
                },
            },
        },
    },
    {
        "name": "cai_agent_list_workflows",
        "description": "列出所有可用的工作流模板，包括内置模板和用户自定义模板。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "workspace": {
                    "type": "string",
                    "description": "工作区根目录路径。",
                },
            },
        },
    },
]


def get_tool_by_name(name: str) -> dict[str, Any] | None:
    """根据名称获取工具定义。"""
    for tool in CAI_AGENT_MCP_TOOLS:
        if tool["name"] == name:
            return tool
    return None


def list_tool_names() -> list[str]:
    """列出所有工具名称。"""
    return [t["name"] for t in CAI_AGENT_MCP_TOOLS]
