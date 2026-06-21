"""Cai Agent ACP Server 实现。

实现 Agent Communication Protocol 服务端，使 Cai Agent 可以被其他 ACP Agent 发现和调用。

基于 AgentUnion ACP 规范的简化实现，支持：
- AgentProfile 发布和发现
- 会话管理
- 消息传递
- Agent 任务执行

使用方式：
    # 启动 ACP 服务
    python -m cai_agent.server.acp_server --port 8070

    # 指定工作区
    python -m cai_agent.server.acp_server --workspace /path/to/project

参考规范：https://acp.agentunion.cn/introduction/
"""

from __future__ import annotations

import asyncio
import json
import logging
import sys
import uuid
from dataclasses import replace
from typing import Any

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# ACP Server 实现
# ---------------------------------------------------------------------------

class CaiAgentACPServer:
    """Cai Agent ACP Server。

    实现 ACP 协议的服务端，支持 AgentProfile、会话管理和消息传递。
    """

    def __init__(
        self,
        settings: Any = None,
        *,
        host: str = "0.0.0.0",
        port: int = 8070,
        agent_id: str = "",
    ) -> None:
        self._settings = settings
        self._host = host
        self._port = port
        self._agent_id = agent_id or f"cai-agent.{uuid.uuid4().hex[:8]}"
        self._sessions: dict[str, Any] = {}  # session_id -> Session
        self._message_queue: dict[str, list] = {}  # aid -> [messages]
        self._msg_seq = 0

    def _get_settings(self, workspace: str | None = None, model: str | None = None) -> Any:
        """获取配置"""
        from cai_agent.config import Settings

        settings = self._settings or Settings.from_env()
        if workspace:
            settings = replace(settings, workspace=workspace)
        if model:
            settings = replace(settings, model=model)
        return settings

    def _next_seq(self) -> int:
        """获取下一个消息序列号"""
        self._msg_seq += 1
        return self._msg_seq

    def _create_agent_profile(self) -> dict[str, Any]:
        """创建 AgentProfile"""
        from cai_agent.protocol.acp_models import (
            AgentCapabilities,
            AgentIO,
            AgentProfile,
            AuthorizationInfo,
            LLMInfo,
            PublisherInfo,
            agent_profile_to_dict,
        )

        profile = AgentProfile(
            name="Cai Agent",
            description=(
                "AI 驱动的代码开发助手，基于 LangGraph 状态机和多角色 Agent 系统。"
                "支持代码生成、文档编写、工作流编排、代码审查等多种开发任务。"
            ),
            version="0.21.0",
            publisher_info=PublisherInfo(
                publisher_aid=self._agent_id,
                organization="Cai Agent",
                certification_signature="",
            ),
            avatar_url="",
            capabilities=AgentCapabilities(
                core=["code_generation", "code_review", "documentation", "workflow"],
                extended=["bug_fix", "refactoring", "planning", "testing"],
            ),
            llm=LLMInfo(
                model="gpt-4o",
                context_length="128000",
            ),
            authorization=AuthorizationInfo(
                modes=["free"],
                description="免费使用，无费用",
            ),
            input=AgentIO(
                types=["content"],
                formats=["json", "text"],
                examples={
                    "type": "content",
                    "format": "text",
                    "content": "帮我分析 src/auth.py 的安全性",
                },
                semantics=["natural-language", "code"],
                compatible_aids=["*"],
            ),
            output=AgentIO(
                types=["content"],
                formats=["markdown", "json", "text"],
                examples={
                    "type": "content",
                    "format": "markdown",
                    "content": "# 分析结果\n\n...",
                },
                semantics=["analysis", "code", "documentation"],
                compatible_aids=["*"],
            ),
            support_stream=True,
            support_async=True,
            permissions=["*"],
        )

        return agent_profile_to_dict(profile)

    def _create_app(self) -> Any:
        """创建 FastAPI 应用"""
        try:
            from fastapi import FastAPI, HTTPException, Request
            from fastapi.middleware.cors import CORSMiddleware
            from fastapi.responses import JSONResponse, StreamingResponse
        except ImportError:
            logger.error("FastAPI not installed. Install with: pip install fastapi uvicorn")
            sys.exit(1)

        from cai_agent.protocol.acp_models import (
            ACPResponse,
            CreateSessionRequest,
            JoinSessionRequest,
            Message,
            MessageContentType,
            MessageHeader,
            MessageType,
            SendMessageRequest,
            Session,
            SessionState,
            session_to_dict,
        )

        app = FastAPI(
            title="Cai Agent ACP Server",
            description="Agent Communication Protocol server for Cai Agent",
            version="0.21.0",
        )

        # CORS 中间件
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        # -----------------------------------------------------------------------
        # AgentProfile 端点
        # -----------------------------------------------------------------------

        @app.get("/acp/agent/profile")
        async def get_agent_profile() -> dict:
            """获取 AgentProfile"""
            return self._create_agent_profile()

        @app.get("/.well-known/agentprofile.json")
        async def get_agent_profile_well_known() -> dict:
            """获取 AgentProfile（Well-Known 路径）"""
            return self._create_agent_profile()

        # -----------------------------------------------------------------------
        # 会话管理端点
        # -----------------------------------------------------------------------

        @app.post("/acp/sessions/create")
        async def create_session(request: dict) -> dict:
            """创建会话"""
            creator_aid = request.get("creator_aid", "")
            participants = request.get("participants", [])
            metadata = request.get("metadata", {})

            session = Session(
                creator_aid=creator_aid,
                state=SessionState.ACTIVE,
                metadata=metadata,
            )
            session.add_member(creator_aid, role="creator")

            for aid in participants:
                if aid != creator_aid:
                    session.add_member(aid, role="participant")

            self._sessions[session.session_id] = session

            logger.info(f"Session created: {session.session_id} by {creator_aid}")

            return ACPResponse(
                code=200,
                message="Session created",
                data=session_to_dict(session),
            ).to_dict()

        @app.post("/acp/sessions/join")
        async def join_session(request: dict) -> dict:
            """加入会话"""
            aid = request.get("aid", "")
            session_id = request.get("session_id", "")

            session = self._sessions.get(session_id)
            if not session:
                raise HTTPException(status_code=404, detail=f"Session not found: {session_id}")

            if session.state != SessionState.ACTIVE:
                raise HTTPException(status_code=400, detail="Session is not active")

            session.add_member(aid, role="participant")

            logger.info(f"Agent {aid} joined session {session_id}")

            return ACPResponse(
                code=200,
                message="Joined session",
                data=session_to_dict(session),
            ).to_dict()

        @app.post("/acp/sessions/leave")
        async def leave_session(request: dict) -> dict:
            """离开会话"""
            aid = request.get("aid", "")
            session_id = request.get("session_id", "")

            session = self._sessions.get(session_id)
            if not session:
                raise HTTPException(status_code=404, detail=f"Session not found: {session_id}")

            session.remove_member(aid)

            logger.info(f"Agent {aid} left session {session_id}")

            return ACPResponse(
                code=200,
                message="Left session",
                data=session_to_dict(session),
            ).to_dict()

        @app.post("/acp/sessions/close")
        async def close_session(request: dict) -> dict:
            """关闭会话"""
            session_id = request.get("session_id", "")
            creator_aid = request.get("creator_aid", "")

            session = self._sessions.get(session_id)
            if not session:
                raise HTTPException(status_code=404, detail=f"Session not found: {session_id}")

            if session.creator_aid != creator_aid:
                raise HTTPException(status_code=403, detail="Only creator can close session")

            session.state = SessionState.COMPLETED

            logger.info(f"Session {session_id} closed by {creator_aid}")

            return ACPResponse(
                code=200,
                message="Session closed",
                data=session_to_dict(session),
            ).to_dict()

        @app.post("/acp/sessions/get")
        async def get_session(request: dict) -> dict:
            """获取会话信息"""
            session_id = request.get("session_id", "")

            session = self._sessions.get(session_id)
            if not session:
                raise HTTPException(status_code=404, detail=f"Session not found: {session_id}")

            return ACPResponse(
                code=200,
                message="OK",
                data=session_to_dict(session),
            ).to_dict()

        @app.get("/acp/sessions/list")
        async def list_sessions() -> dict:
            """列出所有会话"""
            sessions = [session_to_dict(s) for s in self._sessions.values()]
            return ACPResponse(
                code=200,
                message="OK",
                data={"sessions": sessions, "count": len(sessions)},
            ).to_dict()

        # -----------------------------------------------------------------------
        # 消息传递端点
        # -----------------------------------------------------------------------

        @app.post("/acp/messages/send")
        async def send_message(request: dict) -> dict:
            """发送消息"""
            sender_aid = request.get("sender_aid", "")
            receiver_aid = request.get("receiver_aid", "")
            session_id = request.get("session_id", "")
            content = request.get("content", {})
            content_type = request.get("content_type", 1)

            # 创建消息
            message = Message(
                header=MessageHeader(
                    msg_type=MessageType.DATA,
                    msg_seq=self._next_seq(),
                    content_type=content_type,
                ),
                sender_aid=sender_aid,
                receiver_aid=receiver_aid,
                session_id=session_id,
                payload=content,
            )

            # 添加到会话
            session = self._sessions.get(session_id)
            if session:
                session.add_message(message)

            # 如果接收方是本 Agent，处理消息
            if receiver_aid == self._agent_id:
                response_content = await self._process_message(content)
                response_msg = Message(
                    header=MessageHeader(
                        msg_type=MessageType.RESPONSE,
                        msg_seq=self._next_seq(),
                        content_type=MessageContentType.JSON,
                    ),
                    sender_aid=self._agent_id,
                    receiver_aid=sender_aid,
                    session_id=session_id,
                    payload=response_content,
                )
                if session:
                    session.add_message(response_msg)

                return ACPResponse(
                    code=200,
                    message="Message sent and processed",
                    data={
                        "message_id": message.header.msg_seq,
                        "response": response_content,
                    },
                ).to_dict()

            # 否则加入消息队列
            if receiver_aid not in self._message_queue:
                self._message_queue[receiver_aid] = []
            self._message_queue[receiver_aid].append(message.to_dict())

            return ACPResponse(
                code=200,
                message="Message sent",
                data={"message_id": message.header.msg_seq},
            ).to_dict()

        @app.post("/acp/messages/receive")
        async def receive_messages(request: dict) -> dict:
            """接收消息"""
            aid = request.get("aid", "")
            wait = request.get("wait", False)
            timeout = request.get("timeout", 30)

            # 检查消息队列
            if aid in self._message_queue and self._message_queue[aid]:
                messages = self._message_queue[aid]
                self._message_queue[aid] = []
                return ACPResponse(
                    code=200,
                    message="Messages received",
                    data={"messages": messages, "count": len(messages)},
                ).to_dict()

            # 如果不等待，直接返回空
            if not wait:
                return ACPResponse(
                    code=200,
                    message="No messages",
                    data={"messages": [], "count": 0},
                ).to_dict()

            # 等待消息（简化实现，实际应使用 WebSocket 或 SSE）
            await asyncio.sleep(min(timeout, 5))

            if aid in self._message_queue and self._message_queue[aid]:
                messages = self._message_queue[aid]
                self._message_queue[aid] = []
                return ACPResponse(
                    code=200,
                    message="Messages received",
                    data={"messages": messages, "count": len(messages)},
                ).to_dict()

            return ACPResponse(
                code=200,
                message="No messages",
                data={"messages": [], "count": 0},
            ).to_dict()

        @app.post("/acp/messages/stream")
        async def stream_messages(request: dict):
            """流式接收消息（SSE）"""
            aid = request.get("aid", "")
            timeout = request.get("timeout", 300)

            async def event_stream():
                start_time = asyncio.get_event_loop().time()
                while True:
                    # 检查超时
                    if asyncio.get_event_loop().time() - start_time > timeout:
                        break

                    # 检查消息
                    if aid in self._message_queue and self._message_queue[aid]:
                        messages = self._message_queue[aid]
                        self._message_queue[aid] = []
                        for msg in messages:
                            yield f"data: {json.dumps(msg, ensure_ascii=False)}\n\n"

                    await asyncio.sleep(0.5)

            return StreamingResponse(
                event_stream(),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                },
            )

        # -----------------------------------------------------------------------
        # 任务执行端点
        # -----------------------------------------------------------------------

        @app.post("/acp/tasks/execute")
        async def execute_task(request: dict) -> dict:
            """执行任务

            接收任务请求，调用 Cai Agent 执行并返回结果。
            """
            sender_aid = request.get("sender_aid", "")
            session_id = request.get("session_id", "")
            goal = request.get("goal", "")
            task_type = request.get("task_type", "run")
            params = request.get("params", {})

            if not goal:
                raise HTTPException(status_code=400, detail="Goal is required")

            try:
                settings = self._get_settings(
                    workspace=params.get("workspace"),
                    model=params.get("model"),
                )

                if task_type == "run":
                    result = await self._execute_run(settings, goal, params)
                elif task_type == "plan":
                    result = await self._execute_plan(settings, goal, params)
                elif task_type == "workflow":
                    result = await self._execute_workflow(settings, goal, params)
                elif task_type == "doc":
                    result = await self._execute_doc(settings, goal, params)
                else:
                    raise HTTPException(status_code=400, detail=f"Unknown task type: {task_type}")

                # 创建响应消息
                message = Message(
                    header=MessageHeader(
                        msg_type=MessageType.RESPONSE,
                        msg_seq=self._next_seq(),
                    ),
                    sender_aid=self._agent_id,
                    receiver_aid=sender_aid,
                    session_id=session_id,
                    payload=result,
                )

                # 添加到会话
                session = self._sessions.get(session_id)
                if session:
                    session.add_message(message)

                return ACPResponse(
                    code=200,
                    message="Task executed",
                    data=result,
                ).to_dict()

            except Exception as e:
                logger.exception("Error executing task")
                return ACPResponse(
                    code=500,
                    message="Task execution failed",
                    data={"error": str(e)[:800]},
                ).to_dict()

        @app.post("/acp/tasks/execute/stream")
        async def execute_task_stream(request: dict):
            """流式执行任务（SSE）"""
            sender_aid = request.get("sender_aid", "")
            session_id = request.get("session_id", "")
            goal = request.get("goal", "")
            task_type = request.get("task_type", "run")
            params = request.get("params", {})

            if not goal:
                raise HTTPException(status_code=400, detail="Goal is required")

            async def event_stream():
                try:
                    # 发送开始事件
                    yield f"data: {json.dumps({'type': 'start', 'goal': goal})}\n\n"

                    settings = self._get_settings(
                        workspace=params.get("workspace"),
                        model=params.get("model"),
                    )

                    # 执行任务
                    if task_type == "run":
                        result = await self._execute_run(settings, goal, params)
                    elif task_type == "plan":
                        result = await self._execute_plan(settings, goal, params)
                    else:
                        result = {"error": f"Unsupported stream task type: {task_type}"}

                    # 发送结果
                    yield f"data: {json.dumps({'type': 'result', 'data': result}, ensure_ascii=False)}\n\n"

                    # 发送完成事件
                    yield f"data: {json.dumps({'type': 'complete'})}\n\n"

                except Exception as e:
                    yield f"data: {json.dumps({'type': 'error', 'message': str(e)[:800]})}\n\n"

            return StreamingResponse(
                event_stream(),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                },
            )

        # -----------------------------------------------------------------------
        # 健康检查端点
        # -----------------------------------------------------------------------

        @app.get("/health")
        async def health() -> dict:
            """健康检查"""
            return {
                "status": "healthy",
                "service": "cai-agent-acp",
                "agent_id": self._agent_id,
                "version": "0.21.0",
                "active_sessions": len([s for s in self._sessions.values() if s.state == "active"]),
                "total_sessions": len(self._sessions),
            }

        @app.get("/acp/health")
        async def acp_health() -> dict:
            """ACP 健康检查"""
            return await health()

        return app

    async def _process_message(self, content: dict[str, Any]) -> dict[str, Any]:
        """处理接收到的消息"""
        # 提取消息内容
        message_type = content.get("type", "text")
        message_content = content.get("content", "")

        if message_type == "task":
            # 任务类型消息
            goal = content.get("goal", message_content)
            settings = self._get_settings()
            return await self._execute_run(settings, goal, {})
        else:
            # 普通文本消息
            return {
                "type": "response",
                "content": f"收到消息：{message_content[:200]}",
                "agent_id": self._agent_id,
            }

    async def _execute_run(self, settings: Any, goal: str, params: dict) -> dict[str, Any]:
        """执行 run 任务"""
        from cai_agent.graph import build_app, initial_state

        max_iterations = params.get("max_iterations", 15)
        app_graph = build_app(settings, max_iterations=max_iterations)
        final_state = app_graph.invoke(initial_state(goal))

        return {
            "ok": True,
            "answer": final_state.get("answer", ""),
            "goal": final_state.get("goal", ""),
            "iteration": final_state.get("iteration", 0),
            "total_tokens": final_state.get("total_tokens", 0),
            "files": final_state.get("files", []),
        }

    async def _execute_plan(self, settings: Any, goal: str, params: dict) -> dict[str, Any]:
        """执行 plan 任务"""
        from cai_agent.agents import create_agent

        mode = params.get("mode", "full")
        agent = create_agent(settings, role="default", max_iterations=10)

        if mode == "quick":
            prompt = f"快速规划任务：{goal}\n请用 3-5 个步骤概括实施计划。"
        else:
            prompt = f"规划任务：{goal}\n请生成详细的实施计划。"

        final_state = agent.run(prompt)

        return {
            "ok": True,
            "plan": final_state.get("answer", ""),
            "mode": mode,
            "total_tokens": final_state.get("total_tokens", 0),
        }

    async def _execute_workflow(self, settings: Any, goal: str, params: dict) -> dict[str, Any]:
        """执行 workflow 任务"""
        from cai_agent.workflow import run_workflow

        workflow_id = params.get("workflow_id")
        workflow_json = params.get("workflow_json")
        timeout_sec = params.get("timeout_sec", 600)

        result = run_workflow(
            settings,
            goal=goal,
            template_name=workflow_id,
            workflow_json=workflow_json,
            timeout_sec=timeout_sec,
        )

        return {
            "ok": result.get("ok", False),
            "answer": result.get("answer", ""),
            "steps_completed": result.get("steps_completed", 0),
            "total_steps": result.get("total_steps", 0),
            "total_tokens": result.get("total_tokens", 0),
        }

    async def _execute_doc(self, settings: Any, goal: str, params: dict) -> dict[str, Any]:
        """执行 doc 任务"""
        from cai_agent.doc_writer import DocGenerateRequest, generate_doc

        doc_type = params.get("doc_type", "readme")
        output_path = params.get("output", "")

        request = DocGenerateRequest(
            doc_type=doc_type,
            output_path=output_path,
            source_dirs=params.get("source_dirs", ["."]),
            language=params.get("language", "zh-CN"),
            goal_extra=goal,
        )

        result = generate_doc(settings, request)

        return {
            "ok": result.ok,
            "output_path": result.output_path,
            "doc_type": result.doc_type,
            "word_count": result.word_count,
            "elapsed_ms": result.elapsed_ms,
            "tokens_used": result.tokens_used,
        }

    def run(self) -> None:
        """启动服务器"""
        try:
            import uvicorn
        except ImportError:
            logger.error("uvicorn not installed. Install with: pip install uvicorn")
            sys.exit(1)

        app = self._create_app()
        logger.info(f"Starting Cai Agent ACP Server on {self._host}:{self._port}")
        logger.info(f"Agent ID: {self._agent_id}")

        config = uvicorn.Config(
            app,
            host=self._host,
            port=self._port,
            log_level="info",
        )
        server = uvicorn.Server(config)
        asyncio.run(server.serve())


# ---------------------------------------------------------------------------
# CLI 入口
# ---------------------------------------------------------------------------

def main() -> None:
    """ACP Server CLI 入口"""
    import argparse

    parser = argparse.ArgumentParser(description="Cai Agent ACP Server")
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="监听地址，默认 0.0.0.0",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8070,
        help="监听端口，默认 8070",
    )
    parser.add_argument(
        "--config",
        default=None,
        help="配置文件路径",
    )
    parser.add_argument(
        "--agent-id",
        default=None,
        help="Agent ID（默认自动生成）",
    )

    args = parser.parse_args()

    # 设置日志
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # 加载配置
    try:
        from cai_agent.config import Settings
        settings = Settings.from_env(config_path=args.config)
    except Exception as e:
        logger.error(f"Failed to load config: {e}")
        sys.exit(1)

    # 创建服务器
    server = CaiAgentACPServer(
        settings,
        host=args.host,
        port=args.port,
        agent_id=args.agent_id or "",
    )

    # 启动
    server.run()


if __name__ == "__main__":
    main()
