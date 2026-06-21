"""ACP 协议数据模型定义。

基于 AgentUnion ACP 规范，定义 AgentProfile、会话、消息等核心数据结构。
简化实现，支持本地部署和基本的 Agent 通信。

参考规范：https://acp.agentunion.cn/introduction/
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

class SessionState(str, Enum):
    """会话状态"""
    PENDING = "pending"          # 等待加入
    ACTIVE = "active"            # 活跃中
    COMPLETED = "completed"      # 已完成
    FAILED = "failed"            # 失败
    CANCELED = "canceled"        # 已取消


class MessageContentType(int, Enum):
    """消息内容类型"""
    TEXT = 0          # 普通文本
    JSON = 1          # JSON 文本
    AUDIO = 2         # 音频数据
    VIDEO = 3         # 视频数据
    IMAGE = 4         # 图片数据


class MessageType(int, Enum):
    """消息类型"""
    REQUEST = 0x0001             # 请求消息
    RESPONSE = 0x0002            # 响应消息
    HEARTBEAT = 0x0003           # 心跳消息
    SESSION_INVITE = 0x0010      # 会话邀请
    SESSION_JOIN = 0x0011        # 加入会话
    SESSION_LEAVE = 0x0012       # 离开会话
    SESSION_CLOSE = 0x0013       # 关闭会话
    SESSION_MEMBERS = 0x0014     # 成员列表
    DATA = 0x0020                # 数据消息
    STREAM_START = 0x0030        # 流式开始
    STREAM_DATA = 0x0031         # 流式数据
    STREAM_END = 0x0032          # 流式结束
    ERROR = 0x00FF               # 错误消息


# ---------------------------------------------------------------------------
# AgentProfile 数据模型
# ---------------------------------------------------------------------------

@dataclass
class PublisherInfo:
    """发布者信息"""
    publisher_aid: str = ""
    organization: str = ""
    certification_signature: str = ""


@dataclass
class AgentCapabilities:
    """Agent 能力"""
    core: list[str] = field(default_factory=list)
    extended: list[str] = field(default_factory=list)


@dataclass
class LLMInfo:
    """LLM 信息"""
    model: str = ""
    num_parameters: str = ""
    quantization_bits: str = ""
    context_length: str = ""


@dataclass
class AgentIO:
    """Agent 输入输出规范"""
    types: list[str] = field(default_factory=list)
    formats: list[str] = field(default_factory=list)
    examples: dict[str, Any] = field(default_factory=dict)
    semantics: list[str] = field(default_factory=list)
    compatible_aids: list[str] = field(default_factory=list)


@dataclass
class AuthorizationInfo:
    """授权信息"""
    modes: list[str] = field(default_factory=lambda: ["free"])
    fee: dict[str, Any] = field(default_factory=dict)
    description: str = ""
    sla: dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentProfile:
    """Agent 能力描述文件

    遵循 ACP agentprofile.json 规范，用于：
    - 搜索引擎收录
    - Agent 发现
    - 授权与协作
    """
    name: str = ""
    description: str = ""
    version: str = "1.0.0"
    last_updated: str = ""
    publisher_info: PublisherInfo = field(default_factory=PublisherInfo)
    avatar_url: str = ""
    capabilities: AgentCapabilities = field(default_factory=AgentCapabilities)
    llm: LLMInfo = field(default_factory=LLMInfo)
    authorization: AuthorizationInfo = field(default_factory=AuthorizationInfo)
    input: AgentIO = field(default_factory=AgentIO)
    output: AgentIO = field(default_factory=AgentIO)
    support_stream: bool = True
    support_async: bool = True
    permissions: list[str] = field(default_factory=lambda: ["*"])

    def __post_init__(self):
        if not self.last_updated:
            self.last_updated = datetime.now(UTC).isoformat()


# ---------------------------------------------------------------------------
# 消息头（简化版）
# ---------------------------------------------------------------------------

@dataclass
class MessageHeader:
    """消息头

    简化版消息头，包含基本的路由和元数据信息。
    """
    magic: str = "MU"                    # 魔数标识
    version: int = 1                     # 版本号
    msg_type: int = MessageType.REQUEST  # 消息类型
    msg_seq: int = 0                     # 消息序列号
    content_type: int = MessageContentType.JSON  # 内容类型
    timestamp: str = ""                  # 时间戳

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now(UTC).isoformat()


# ---------------------------------------------------------------------------
# 消息体
# ---------------------------------------------------------------------------

@dataclass
class Message:
    """ACP 消息

    Agent 之间通信的基本单位。
    """
    header: MessageHeader = field(default_factory=MessageHeader)
    sender_aid: str = ""                 # 发送方 AID
    receiver_aid: str = ""               # 接收方 AID
    session_id: str = ""                 # 会话 ID
    payload: dict[str, Any] = field(default_factory=dict)  # 消息负载
    signature: str = ""                  # 签名（可选）

    def to_dict(self) -> dict[str, Any]:
        """转换为字典"""
        return {
            "header": {
                "magic": self.header.magic,
                "version": self.header.version,
                "msg_type": self.header.msg_type,
                "msg_seq": self.header.msg_seq,
                "content_type": self.header.content_type,
                "timestamp": self.header.timestamp,
            },
            "sender_aid": self.sender_aid,
            "receiver_aid": self.receiver_aid,
            "session_id": self.session_id,
            "payload": self.payload,
            "signature": self.signature,
        }


# ---------------------------------------------------------------------------
# 会话
# ---------------------------------------------------------------------------

@dataclass
class SessionMember:
    """会话成员"""
    aid: str = ""
    role: str = "participant"  # "creator" | "participant"
    joined_at: str = ""
    status: str = "active"

    def __post_init__(self):
        if not self.joined_at:
            self.joined_at = datetime.now(UTC).isoformat()


@dataclass
class Session:
    """ACP 会话

    管理 Agent 之间的通信会话。
    """
    session_id: str = ""
    creator_aid: str = ""
    state: SessionState = SessionState.PENDING
    members: list[SessionMember] = field(default_factory=list)
    messages: list[Message] = field(default_factory=list)
    created_at: str = ""
    updated_at: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.session_id:
            self.session_id = str(uuid.uuid4())
        if not self.created_at:
            self.created_at = datetime.now(UTC).isoformat()
        self.updated_at = self.created_at

    def add_member(self, aid: str, role: str = "participant") -> SessionMember:
        """添加成员"""
        member = SessionMember(aid=aid, role=role)
        self.members.append(member)
        self.updated_at = datetime.now(UTC).isoformat()
        return member

    def remove_member(self, aid: str) -> bool:
        """移除成员"""
        for i, member in enumerate(self.members):
            if member.aid == aid:
                self.members.pop(i)
                self.updated_at = datetime.now(UTC).isoformat()
                return True
        return False

    def add_message(self, message: Message) -> None:
        """添加消息"""
        self.messages.append(message)
        self.updated_at = datetime.now(UTC).isoformat()

    def get_member_aids(self) -> list[str]:
        """获取所有成员 AID"""
        return [m.aid for m in self.members]


# ---------------------------------------------------------------------------
# 请求/响应模型
# ---------------------------------------------------------------------------

@dataclass
class SendMessageRequest:
    """发送消息请求"""
    sender_aid: str = ""
    receiver_aid: str = ""
    session_id: str = ""
    content: dict[str, Any] = field(default_factory=dict)
    content_type: int = MessageContentType.JSON


@dataclass
class CreateSessionRequest:
    """创建会话请求"""
    creator_aid: str = ""
    participants: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class JoinSessionRequest:
    """加入会话请求"""
    aid: str = ""
    session_id: str = ""


@dataclass
class ACPResponse:
    """ACP 响应"""
    code: int = 200
    message: str = "OK"
    data: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """转换为字典"""
        result = {
            "code": self.code,
            "message": self.message,
        }
        if self.data:
            result["data"] = self.data
        return result


# ---------------------------------------------------------------------------
# 序列化辅助函数
# ---------------------------------------------------------------------------

def agent_profile_to_dict(profile: AgentProfile) -> dict[str, Any]:
    """将 AgentProfile 转换为字典"""
    return {
        "publisherInfo": {
            "publisherAid": profile.publisher_info.publisher_aid,
            "organization": profile.publisher_info.organization,
            "certificationSignature": profile.publisher_info.certification_signature,
        },
        "avaUrl": profile.avatar_url,
        "version": profile.version,
        "lastUpdated": profile.last_updated,
        "name": profile.name,
        "description": profile.description,
        "capabilities": {
            "core": profile.capabilities.core,
            "extended": profile.capabilities.extended,
        },
        "llm": {
            "model": profile.llm.model,
            "num_parameters": profile.llm.num_parameters,
            "quantization_bits": profile.llm.quantization_bits,
            "context_length": profile.llm.context_length,
        },
        "authorization": {
            "modes": profile.authorization.modes,
            "fee": profile.authorization.fee,
            "description": profile.authorization.description,
            "sla": profile.authorization.sla,
        },
        "input": {
            "types": profile.input.types,
            "formats": profile.input.formats,
            "examples": profile.input.examples,
            "semantics": profile.input.semantics,
            "compatibleAids": profile.input.compatible_aids,
        },
        "output": {
            "types": profile.output.types,
            "formats": profile.output.formats,
            "examples": profile.output.examples,
            "semantics": profile.output.semantics,
            "compatibleAids": profile.output.compatible_aids,
        },
        "supportStream": profile.support_stream,
        "supportAsync": profile.support_async,
        "permission": profile.permissions,
    }


def session_to_dict(session: Session) -> dict[str, Any]:
    """将 Session 转换为字典"""
    return {
        "session_id": session.session_id,
        "creator_aid": session.creator_aid,
        "state": session.state.value,
        "members": [
            {
                "aid": m.aid,
                "role": m.role,
                "joined_at": m.joined_at,
                "status": m.status,
            }
            for m in session.members
        ],
        "message_count": len(session.messages),
        "created_at": session.created_at,
        "updated_at": session.updated_at,
        "metadata": session.metadata,
    }
