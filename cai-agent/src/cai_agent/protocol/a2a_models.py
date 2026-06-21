"""A2A 协议数据模型定义。

定义 Agent-to-Agent Protocol 的核心数据结构，包括 AgentCard、Task、Message 等。
基于 Google A2A Protocol 规范：https://github.com/google/A2A
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any


# ---------------------------------------------------------------------------
# 枚举类型
# ---------------------------------------------------------------------------

class TaskState(str, Enum):
    """任务状态枚举"""
    SUBMITTED = "submitted"
    WORKING = "working"
    INPUT_REQUIRED = "input-required"
    COMPLETED = "completed"
    CANCELED = "canceled"
    FAILED = "failed"


class PartType(str, Enum):
    """消息片段类型"""
    TEXT = "text"
    FILE = "file"
    DATA = "data"


class Role(str, Enum):
    """消息角色"""
    USER = "user"
    AGENT = "agent"


# ---------------------------------------------------------------------------
# 消息片段
# ---------------------------------------------------------------------------

@dataclass
class TextPart:
    """文本片段"""
    type: str = "text"
    text: str = ""
    metadata: dict[str, Any] | None = None


@dataclass
class FilePart:
    """文件片段"""
    type: str = "file"
    file: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] | None = None


@dataclass
class DataPart:
    """结构化数据片段"""
    type: str = "data"
    data: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] | None = None


Part = TextPart | FilePart | DataPart


# ---------------------------------------------------------------------------
# 消息
# ---------------------------------------------------------------------------

@dataclass
class Message:
    """消息"""
    role: str  # "user" | "agent"
    parts: list[Part] = field(default_factory=list)
    metadata: dict[str, Any] | None = None


# ---------------------------------------------------------------------------
# 任务状态
# ---------------------------------------------------------------------------

@dataclass
class TaskStatus:
    """任务状态"""
    state: TaskState = TaskState.SUBMITTED
    message: Message | None = None
    timestamp: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now(UTC).isoformat()


# ---------------------------------------------------------------------------
# 工件（Artifacts）
# ---------------------------------------------------------------------------

@dataclass
class Artifact:
    """任务产出物"""
    name: str = ""
    description: str = ""
    parts: list[Part] = field(default_factory=list)
    index: int = 0
    append: bool = False
    last_chunk: bool = True
    metadata: dict[str, Any] | None = None


# ---------------------------------------------------------------------------
# 任务
# ---------------------------------------------------------------------------

@dataclass
class Task:
    """A2A 任务"""
    id: str = ""
    session_id: str = ""
    status: TaskStatus = field(default_factory=TaskStatus)
    artifacts: list[Artifact] = field(default_factory=list)
    history: list[Message] = field(default_factory=list)
    metadata: dict[str, Any] | None = None

    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())


# ---------------------------------------------------------------------------
# 请求/响应模型
# ---------------------------------------------------------------------------

@dataclass
class TaskSendRequest:
    """任务发送请求"""
    id: str = ""
    session_id: str = ""
    message: Message = field(default_factory=lambda: Message(role="user"))
    metadata: dict[str, Any] | None = None

    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())
        if not self.session_id:
            self.session_id = str(uuid.uuid4())


@dataclass
class TaskQueryRequest:
    """任务查询请求"""
    id: str = ""
    history_length: int = 10
    metadata: dict[str, Any] | None = None


@dataclass
class TaskCancelRequest:
    """任务取消请求"""
    id: str = ""
    metadata: dict[str, Any] | None = None


# ---------------------------------------------------------------------------
# AgentCard
# ---------------------------------------------------------------------------

@dataclass
class AgentSkill:
    """Agent 技能描述"""
    id: str = ""
    name: str = ""
    description: str = ""
    tags: list[str] = field(default_factory=list)
    examples: list[str] = field(default_factory=list)
    input_modes: list[str] | None = None
    output_modes: list[str] = field(default_factory=lambda: ["text/plain"])


@dataclass
class AgentCapabilities:
    """Agent 能力"""
    streaming: bool = True
    push_notifications: bool = False
    state_transition_history: bool = True


@dataclass
class AgentAuthentication:
    """Agent 认证配置"""
    schemes: list[str] = field(default_factory=lambda: ["api_key"])
    credentials: str | None = None


@dataclass
class AgentProvider:
    """Agent 提供者信息"""
    organization: str = ""
    url: str = ""


@dataclass
class AgentCard:
    """Agent 名片 - 描述 Agent 的能力和服务端点"""
    name: str = ""
    description: str = ""
    url: str = ""
    version: str = ""
    documentation_url: str | None = None
    provider: AgentProvider | None = None
    capabilities: AgentCapabilities = field(default_factory=AgentCapabilities)
    authentication: AgentAuthentication = field(default_factory=AgentAuthentication)
    default_input_modes: list[str] = field(default_factory=lambda: ["text/plain", "application/json"])
    default_output_modes: list[str] = field(default_factory=lambda: ["text/plain", "application/json"])
    skills: list[AgentSkill] = field(default_factory=list)


# ---------------------------------------------------------------------------
# JSON 序列化辅助
# ---------------------------------------------------------------------------

def _dataclass_to_dict(obj: Any) -> Any:
    """将 dataclass 转换为字典，处理嵌套和枚举"""
    if hasattr(obj, "__dataclass_fields__"):
        result = {}
        for f in obj.__dataclass_fields__:
            value = getattr(obj, f)
            if value is not None:
                key = f.replace("_", "-") if f in ("input_modes", "output_modes", "state_transition_history", "push_notifications") else f
                result[key] = _dataclass_to_dict(value)
        return result
    elif isinstance(obj, Enum):
        return obj.value
    elif isinstance(obj, list):
        return [_dataclass_to_dict(item) for item in obj]
    elif isinstance(obj, dict):
        return {k: _dataclass_to_dict(v) for k, v in obj.items()}
    return obj


def agent_card_to_dict(card: AgentCard) -> dict[str, Any]:
    """将 AgentCard 转换为 API 响应字典"""
    return {
        "name": card.name,
        "description": card.description,
        "url": card.url,
        "version": card.version,
        "documentationUrl": card.documentation_url,
        "provider": _dataclass_to_dict(card.provider) if card.provider else None,
        "capabilities": {
            "streaming": card.capabilities.streaming,
            "pushNotifications": card.capabilities.push_notifications,
            "stateTransitionHistory": card.capabilities.state_transition_history,
        },
        "authentication": {
            "schemes": card.authentication.schemes,
            "credentials": card.authentication.credentials,
        },
        "defaultInputModes": card.default_input_modes,
        "defaultOutputModes": card.default_output_modes,
        "skills": [
            {
                "id": skill.id,
                "name": skill.name,
                "description": skill.description,
                "tags": skill.tags,
                "examples": skill.examples,
                "inputModes": skill.input_modes,
                "outputModes": skill.output_modes,
            }
            for skill in card.skills
        ],
    }


def task_to_dict(task: Task) -> dict[str, Any]:
    """将 Task 转换为 API 响应字典"""
    result: dict[str, Any] = {
        "id": task.id,
        "status": {
            "state": task.status.state.value,
            "timestamp": task.status.timestamp,
        },
    }

    if task.session_id:
        result["sessionId"] = task.session_id

    if task.status.message:
        result["status"]["message"] = _message_to_dict(task.status.message)

    if task.artifacts:
        result["artifacts"] = [_artifact_to_dict(a) for a in task.artifacts]

    if task.history:
        result["history"] = [_message_to_dict(m) for m in task.history[-10:]]

    if task.metadata:
        result["metadata"] = task.metadata

    return result


def _message_to_dict(msg: Message) -> dict[str, Any]:
    """将 Message 转换为字典"""
    return {
        "role": msg.role,
        "parts": [_part_to_dict(p) for p in msg.parts],
        "metadata": msg.metadata,
    }


def _part_to_dict(part: Part) -> dict[str, Any]:
    """将 Part 转换为字典"""
    if isinstance(part, TextPart):
        result = {"type": "text", "text": part.text}
        if part.metadata:
            result["metadata"] = part.metadata
        return result
    elif isinstance(part, FilePart):
        result = {"type": "file", "file": part.file}
        if part.metadata:
            result["metadata"] = part.metadata
        return result
    elif isinstance(part, DataPart):
        result = {"type": "data", "data": part.data}
        if part.metadata:
            result["metadata"] = part.metadata
        return result
    return {"type": "text", "text": str(part)}


def _artifact_to_dict(artifact: Artifact) -> dict[str, Any]:
    """将 Artifact 转换为字典"""
    result: dict[str, Any] = {
        "parts": [_part_to_dict(p) for p in artifact.parts],
    }
    if artifact.name:
        result["name"] = artifact.name
    if artifact.description:
        result["description"] = artifact.description
    if artifact.index:
        result["index"] = artifact.index
    if artifact.metadata:
        result["metadata"] = artifact.metadata
    return result
