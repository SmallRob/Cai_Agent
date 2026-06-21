"""Cai Agent 的 AgentCard 定义。

定义 Cai Agent 作为 A2A 服务端的名片信息，包括能力、技能和端点。
"""

from __future__ import annotations

from cai_agent.protocol.a2a_models import (
    AgentAuthentication,
    AgentCapabilities,
    AgentCard,
    AgentProvider,
    AgentSkill,
)


def create_cai_agent_card(
    *,
    url: str = "http://localhost:8080",
    version: str = "0.21.0",
    api_key: str | None = None,
) -> AgentCard:
    """创建 Cai Agent 的 AgentCard。

    Args:
        url: 服务端点 URL
        version: 版本号
        api_key: API 密钥（可选）

    Returns:
        AgentCard 实例
    """
    return AgentCard(
        name="Cai Agent",
        description=(
            "AI 驱动的代码开发助手，基于 LangGraph 状态机和多角色 Agent 系统。"
            "支持代码生成、文档编写、工作流编排、代码审查等多种开发任务。"
            "具备探索-实现-评审的自动化开发能力。"
        ),
        url=url,
        version=version,
        documentation_url="https://github.com/cai-agent/cai-agent",
        provider=AgentProvider(
            organization="Cai Agent",
            url="https://github.com/cai-agent",
        ),
        capabilities=AgentCapabilities(
            streaming=True,
            push_notifications=False,
            state_transition_history=True,
        ),
        authentication=AgentAuthentication(
            schemes=["api_key"] if api_key else [],
            credentials=api_key,
        ),
        default_input_modes=["text/plain", "application/json"],
        default_output_modes=["text/plain", "application/json"],
        skills=[
            AgentSkill(
                id="code_generation",
                name="代码生成",
                description="根据自然语言描述生成代码，支持多种编程语言和框架。可自动分析现有代码库风格并保持一致。",
                tags=["code", "programming", "generation", "development"],
                examples=[
                    "用 Python 实现一个 REST API 服务器",
                    "创建一个 React 表单组件，包含验证逻辑",
                    "为 UserService 类添加单元测试",
                    "实现一个支持并发的文件下载器",
                ],
            ),
            AgentSkill(
                id="code_review",
                name="代码审查",
                description="审查代码质量，检查潜在的 bug、安全漏洞、性能问题和代码风格问题。",
                tags=["code", "review", "quality", "security"],
                examples=[
                    "审查 src/auth.py 的安全性",
                    "检查这个 PR 的代码质量",
                    "找出这段代码的性能瓶颈",
                ],
            ),
            AgentSkill(
                id="documentation",
                name="文档编写",
                description="自动生成和更新项目文档，支持 README、API 文档、架构文档等多种类型。",
                tags=["docs", "documentation", "readme", "api"],
                examples=[
                    "生成项目的 README 文档",
                    "为 REST API 生成接口文档",
                    "更新 CHANGELOG",
                ],
            ),
            AgentSkill(
                id="bug_fix",
                name="Bug 修复",
                description="分析错误信息和堆栈跟踪，定位问题根因并提供修复方案。",
                tags=["bug", "fix", "debug", "error"],
                examples=[
                    "修复登录接口返回 500 错误",
                    "解决内存泄漏问题",
                    "修复样式在移动端的显示问题",
                ],
            ),
            AgentSkill(
                id="refactoring",
                name="代码重构",
                description="重构代码以提高可读性、可维护性和性能，同时保持功能不变。",
                tags=["refactor", "code", "improvement", "cleanup"],
                examples=[
                    "重构 UserService，提取公共方法",
                    "将这个单体函数拆分为多个小函数",
                    "优化数据库查询性能",
                ],
            ),
            AgentSkill(
                id="workflow",
                name="工作流编排",
                description="执行多步骤、多角色的复杂开发工作流，支持探索-实现-评审等模式。",
                tags=["workflow", "pipeline", "automation", "orchestration"],
                examples=[
                    "运行探索-实现-评审流程来完成这个功能",
                    "执行代码质量检查工作流",
                    "运行自动化测试和部署流程",
                ],
            ),
            AgentSkill(
                id="planning",
                name="任务规划",
                description="分析复杂任务并生成详细的实施计划，包括步骤分解、依赖分析和风险评估。",
                tags=["plan", "planning", "architecture", "design"],
                examples=[
                    "规划用户认证系统的实现方案",
                    "设计微服务架构",
                    "制定数据库迁移计划",
                ],
            ),
        ],
    )
