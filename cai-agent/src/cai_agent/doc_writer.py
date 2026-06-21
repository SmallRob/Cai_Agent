"""AI Agent 文档编写核心模块。

提供文档生成、更新、审查和模板管理功能，
利用 LangGraph Agent 系统实现智能化文档编写。
"""

from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal

from cai_agent.config import Settings
from cai_agent.agents import create_agent, AgentRole
from cai_agent.workflow import run_workflow


# ---------------------------------------------------------------------------
# 数据结构定义
# ---------------------------------------------------------------------------

DocType = Literal["readme", "api", "architecture", "changelog", "contributing", "custom"]


@dataclass(frozen=True)
class DocGenerateRequest:
    """文档生成请求"""
    doc_type: DocType
    output_path: str
    source_dirs: list[str] = field(default_factory=lambda: ["."])
    template: str | None = None
    style_guide: str | None = None
    language: str = "zh-CN"
    include_examples: bool = True
    max_depth: int = 3
    goal_extra: str = ""


@dataclass
class DocGenerateResult:
    """文档生成结果"""
    schema_version: str = "doc_generate_result_v1"
    ok: bool = False
    output_path: str = ""
    doc_type: str = ""
    sections_generated: list[str] = field(default_factory=list)
    word_count: int = 0
    elapsed_ms: int = 0
    tokens_used: int = 0
    warnings: list[str] = field(default_factory=list)
    error: str | None = None
    generated_at: str = ""


@dataclass
class DocReviewResult:
    """文档审查结果"""
    schema_version: str = "doc_review_result_v1"
    ok: bool = False
    file_path: str = ""
    issues: list[dict[str, Any]] = field(default_factory=list)
    score: float = 0.0
    suggestions: list[str] = field(default_factory=list)
    elapsed_ms: int = 0
    tokens_used: int = 0
    error: str | None = None
    generated_at: str = ""


@dataclass
class DocUpdateResult:
    """文档更新结果"""
    schema_version: str = "doc_update_result_v1"
    ok: bool = False
    file_path: str = ""
    changes_summary: str = ""
    sections_updated: list[str] = field(default_factory=list)
    elapsed_ms: int = 0
    tokens_used: int = 0
    warnings: list[str] = field(default_factory=list)
    error: str | None = None
    generated_at: str = ""


# ---------------------------------------------------------------------------
# 文档类型配置
# ---------------------------------------------------------------------------

DOC_TYPE_CONFIG: dict[str, dict[str, Any]] = {
    "readme": {
        "name": "README",
        "description": "项目说明文档",
        "default_output": "README.md",
        "required_sections": ["项目介绍", "安装", "使用方法", "配置"],
        "optional_sections": ["贡献指南", "许可证", "更新日志"],
        "prompt_suffix": "生成一个完整的项目 README 文档，包含项目介绍、安装说明、使用方法、配置说明等。",
    },
    "api": {
        "name": "API 文档",
        "description": "API 接口文档",
        "default_output": "docs/API.md",
        "required_sections": ["概述", "认证", "接口列表", "错误码"],
        "optional_sections": ["SDK", "示例", "FAQ"],
        "prompt_suffix": "生成详细的 API 接口文档，包含所有公开接口的路径、参数、响应格式和示例。",
    },
    "architecture": {
        "name": "架构文档",
        "description": "系统架构说明",
        "default_output": "docs/ARCHITECTURE.md",
        "required_sections": ["概述", "技术栈", "模块划分", "数据流"],
        "optional_sections": ["部署架构", "性能考虑", "安全设计"],
        "prompt_suffix": "生成系统架构文档，包含整体架构、模块划分、数据流、技术选型等。",
    },
    "changelog": {
        "name": "变更日志",
        "description": "版本变更记录",
        "default_output": "CHANGELOG.md",
        "required_sections": ["版本号", "变更日期", "变更内容"],
        "optional_sections": ["Breaking Changes", "已知问题"],
        "prompt_suffix": "生成变更日志，基于 Git 历史和代码变更记录版本更新内容。",
    },
    "contributing": {
        "name": "贡献指南",
        "description": "贡献者指南",
        "default_output": "CONTRIBUTING.md",
        "required_sections": ["如何贡献", "开发环境", "代码规范", "提交规范"],
        "optional_sections": ["Issue 规范", "PR 规范", "发布流程"],
        "prompt_suffix": "生成贡献指南，说明如何参与项目开发、代码规范和提交流程。",
    },
}


# ---------------------------------------------------------------------------
# 核心功能
# ---------------------------------------------------------------------------

def _build_doc_system_prompt(doc_type: str, language: str, request: DocGenerateRequest) -> str:
    """构建文档编写的系统提示词"""
    config = DOC_TYPE_CONFIG.get(doc_type, {})
    lang_hint = "中文" if language.startswith("zh") else "English"

    base_prompt = f"""你是一个专业的技术文档编写专家，擅长编写{lang_hint}技术文档。

你的职责是：
1. 深入分析代码库结构和功能
2. 生成清晰、准确、易读的技术文档
3. 保持文档与代码的一致性
4. 遵循项目已有的文档风格和规范

编写原则：
- 使用简洁明了的语言
- 提供实际的代码示例
- 保持结构清晰，使用适当的标题层级
- 包含必要的图表和流程说明（使用 Mermaid 语法）
- 确保所有链接和引用有效
- 文档语言：{lang_hint}
"""

    if doc_type != "custom":
        sections_hint = "必需章节：" + "、".join(config.get("required_sections", []))
        optional = config.get("optional_sections", [])
        if optional:
            sections_hint += "\n可选章节：" + "、".join(optional)

        base_prompt += f"""
文档类型：{config.get('name', doc_type)}
{sections_hint}

{config.get('prompt_suffix', '')}
"""

    if request.goal_extra:
        base_prompt += f"\n额外要求：{request.goal_extra}\n"

    base_prompt += """
输出要求：
1. 直接输出完整的 Markdown 文档内容
2. 不要输出 JSON 工具调用指令
3. 使用 write_file 工具将文档写入指定路径
4. 文档内容应完整、专业、可直接使用
"""

    return base_prompt


def _build_doc_goal(request: DocGenerateRequest) -> str:
    """构建文档生成的目标描述"""
    config = DOC_TYPE_CONFIG.get(request.doc_type, {})
    doc_name = config.get("name", request.doc_type)

    goal = f"生成 {doc_name} 文档"
    goal += f"\n输出路径：{request.output_path}"
    goal += f"\n源代码目录：{', '.join(request.source_dirs)}"

    if request.template:
        goal += f"\n使用模板：{request.template}"
    if request.style_guide:
        goal += f"\n风格指南：{request.style_guide}"
    if request.include_examples:
        goal += "\n请包含代码示例"

    goal += f"\n分析深度：{request.max_depth} 层"

    if request.goal_extra:
        goal += f"\n额外要求：{request.goal_extra}"

    return goal


def generate_doc(
    settings: Settings,
    request: DocGenerateRequest,
    *,
    progress: Any = None,
) -> DocGenerateResult:
    """生成文档

    Args:
        settings: 配置信息
        request: 文档生成请求
        progress: 进度回调

    Returns:
        文档生成结果
    """
    start_time = time.perf_counter()
    result = DocGenerateResult(
        doc_type=request.doc_type,
        output_path=request.output_path,
        generated_at=datetime.now(UTC).isoformat(),
    )

    try:
        # 构建目标描述
        goal = _build_doc_goal(request)

        # 创建 doc-writer Agent
        # 注意：当前 Agent 系统使用 role 来区分，我们用 "default" 角色
        # 通过系统提示词来指定文档编写行为
        agent = create_agent(
            settings,
            role="default",
            max_iterations=20,
            progress=progress,
        )

        # 执行 Agent
        final_state = agent.run(goal)

        # 提取结果
        answer = final_state.get("answer", "")
        elapsed_ms = int((time.perf_counter() - start_time) * 1000)

        # 检查输出文件是否存在
        output_path = Path(settings.workspace) / request.output_path
        if output_path.exists():
            content = output_path.read_text(encoding="utf-8")
            result.ok = True
            result.word_count = len(content)
            result.sections_generated = _extract_sections(content)
        else:
            # 尝试从 answer 中提取内容
            if answer and len(answer) > 100:
                # 将 answer 写入文件
                output_path.parent.mkdir(parents=True, exist_ok=True)
                output_path.write_text(answer, encoding="utf-8")
                result.ok = True
                result.word_count = len(answer)
                result.sections_generated = _extract_sections(answer)
            else:
                result.error = "文档生成失败：未产生有效内容"

        result.elapsed_ms = elapsed_ms
        result.tokens_used = int(final_state.get("total_tokens", 0) or 0)

    except Exception as e:
        result.error = str(e)[:800]
        result.elapsed_ms = int((time.perf_counter() - start_time) * 1000)

    return result


def review_doc(
    settings: Settings,
    file_path: str,
    *,
    progress: Any = None,
) -> DocReviewResult:
    """审查文档

    Args:
        settings: 配置信息
        file_path: 文档文件路径
        progress: 进度回调

    Returns:
        文档审查结果
    """
    start_time = time.perf_counter()
    result = DocReviewResult(
        file_path=file_path,
        generated_at=datetime.now(UTC).isoformat(),
    )

    try:
        # 读取文档内容
        full_path = Path(settings.workspace) / file_path
        if not full_path.exists():
            result.error = f"文件不存在：{file_path}"
            return result

        content = full_path.read_text(encoding="utf-8")

        # 构建审查目标
        goal = f"""审查文档 {file_path} 的质量，检查以下方面：

1. **完整性**：是否包含所有必要章节
2. **准确性**：内容是否与代码一致
3. **可读性**：结构是否清晰，语言是否简洁
4. **规范性**：是否遵循 Markdown 规范
5. **链接有效性**：所有链接是否有效

文档内容：
```
{content[:8000]}  # 限制长度避免 token 溢出
```

请输出 JSON 格式的审查结果：
{{
  "score": 0-100,
  "issues": [
    {{"severity": "high/medium/low", "description": "问题描述", "location": "位置"}}
  ],
  "suggestions": ["改进建议1", "改进建议2"]
}}
"""

        # 创建审查 Agent
        agent = create_agent(
            settings,
            role="reviewer",
            max_iterations=10,
            progress=progress,
        )

        # 执行审查
        final_state = agent.run(goal)
        answer = final_state.get("answer", "")

        # 解析审查结果
        try:
            # 尝试从 answer 中提取 JSON
            review_data = _extract_json_from_text(answer)
            if review_data:
                result.ok = True
                result.score = float(review_data.get("score", 0))
                result.issues = review_data.get("issues", [])
                result.suggestions = review_data.get("suggestions", [])
            else:
                result.ok = True
                result.score = 0
                result.suggestions = [answer[:500]]
        except Exception:
            result.ok = True
            result.score = 0
            result.suggestions = [answer[:500]]

        result.elapsed_ms = int((time.perf_counter() - start_time) * 1000)
        result.tokens_used = int(final_state.get("total_tokens", 0) or 0)

    except Exception as e:
        result.error = str(e)[:800]
        result.elapsed_ms = int((time.perf_counter() - start_time) * 1000)

    return result


def update_doc(
    settings: Settings,
    file_path: str,
    *,
    diff_range: str | None = None,
    based_on: str = "recent",
    progress: Any = None,
) -> DocUpdateResult:
    """更新文档

    Args:
        settings: 配置信息
        file_path: 文档文件路径
        diff_range: Git diff 范围（如 HEAD~3）
        based_on: 更新依据
        progress: 进度回调

    Returns:
        文档更新结果
    """
    start_time = time.perf_counter()
    result = DocUpdateResult(
        file_path=file_path,
        generated_at=datetime.now(UTC).isoformat(),
    )

    try:
        # 读取现有文档
        full_path = Path(settings.workspace) / file_path
        if not full_path.exists():
            result.error = f"文件不存在：{file_path}"
            return result

        existing_content = full_path.read_text(encoding="utf-8")

        # 构建更新目标
        diff_hint = ""
        if diff_range:
            diff_hint = f"\n基于 Git diff {diff_range} 的变更更新文档"

        goal = f"""更新文档 {file_path}，使其与最新代码保持一致。

现有文档内容：
```
{existing_content[:6000]}
```

更新依据：{based_on}
{diff_hint}

请：
1. 分析现有文档结构
2. 识别需要更新的部分
3. 保留文档的整体结构和风格
4. 更新过时的内容
5. 添加新功能的说明
6. 使用 write_file 工具写入更新后的文档
"""

        # 创建更新 Agent
        agent = create_agent(
            settings,
            role="default",
            max_iterations=15,
            progress=progress,
        )

        # 执行更新
        final_state = agent.run(goal)
        answer = final_state.get("answer", "")

        # 检查更新结果
        if full_path.exists():
            new_content = full_path.read_text(encoding="utf-8")
            if new_content != existing_content:
                result.ok = True
                result.changes_summary = answer[:500] if answer else "文档已更新"
                result.sections_updated = _diff_sections(existing_content, new_content)
            else:
                result.ok = True
                result.changes_summary = "文档无需更新"
        else:
            result.error = "更新失败：文件丢失"

        result.elapsed_ms = int((time.perf_counter() - start_time) * 1000)
        result.tokens_used = int(final_state.get("total_tokens", 0) or 0)

    except Exception as e:
        result.error = str(e)[:800]
        result.elapsed_ms = int((time.perf_counter() - start_time) * 1000)

    return result


# ---------------------------------------------------------------------------
# 辅助函数
# ---------------------------------------------------------------------------

def _extract_sections(content: str) -> list[str]:
    """从 Markdown 内容中提取章节标题"""
    sections = []
    for line in content.split("\n"):
        line = line.strip()
        if line.startswith("#"):
            # 移除 # 前缀
            title = line.lstrip("#").strip()
            if title:
                sections.append(title)
    return sections


def _diff_sections(old_content: str, new_content: str) -> list[str]:
    """比较两个文档的章节差异"""
    old_sections = set(_extract_sections(old_content))
    new_sections = set(_extract_sections(new_content))

    updated = []
    # 新增的章节
    for s in new_sections - old_sections:
        updated.append(f"+ {s}")
    # 删除的章节
    for s in old_sections - new_sections:
        updated.append(f"- {s}")
    # 保留的章节（可能内容有变化）
    for s in old_sections & new_sections:
        updated.append(f"~ {s}")

    return updated


def _extract_json_from_text(text: str) -> dict[str, Any] | None:
    """从文本中提取 JSON 对象"""
    import re

    # 尝试找到 JSON 块
    json_patterns = [
        r'```json\s*([\s\S]*?)\s*```',
        r'\{[\s\S]*\}',
    ]

    for pattern in json_patterns:
        matches = re.findall(pattern, text)
        for match in matches:
            try:
                return json.loads(match)
            except json.JSONDecodeError:
                continue

    return None


def list_doc_types() -> list[dict[str, Any]]:
    """列出所有支持的文档类型"""
    return [
        {
            "type": doc_type,
            "name": config["name"],
            "description": config["description"],
            "default_output": config["default_output"],
            "required_sections": config["required_sections"],
        }
        for doc_type, config in DOC_TYPE_CONFIG.items()
    ]


def get_doc_type_config(doc_type: str) -> dict[str, Any] | None:
    """获取指定文档类型的配置"""
    return DOC_TYPE_CONFIG.get(doc_type)
