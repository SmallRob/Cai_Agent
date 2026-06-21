"""Cai Agent A2A Server 实现。

实现 Agent-to-Agent Protocol 服务端，使 Cai Agent 可以被其他 A2A Agent 发现和调用。

使用方式：
    # 启动 A2A 服务
    python -m cai_agent.server.a2a_server --port 8080

    # 指定工作区
    python -m cai_agent.server.a2a_server --workspace /path/to/project
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
# A2A Server 实现
# ---------------------------------------------------------------------------

class CaiAgentA2AServer:
    """Cai Agent A2A Server。

    实现 A2A 协议的服务端，支持任务创建、查询、取消等操作。
    """

    def __init__(
        self,
        settings: Any = None,
        *,
        host: str = "0.0.0.0",
        port: int = 8080,
        api_key: str | None = None,
    ) -> None:
        self._settings = settings
        self._host = host
        self._port = port
        self._api_key = api_key
        self._tasks: dict[str, Any] = {}  # task_id -> Task
        self._running_tasks: dict[str, asyncio.Task] = {}  # task_id -> asyncio.Task

    def _get_settings(self, workspace: str | None = None, model: str | None = None) -> Any:
        """获取配置"""
        from cai_agent.config import Settings

        settings = self._settings or Settings.from_env()
        if workspace:
            settings = replace(settings, workspace=workspace)
        if model:
            settings = replace(settings, model=model)
        return settings

    def _create_app(self) -> Any:
        """创建 FastAPI 应用"""
        try:
            from fastapi import FastAPI, HTTPException, Request
            from fastapi.middleware.cors import CORSMiddleware
            from fastapi.responses import JSONResponse
        except ImportError:
            logger.error("FastAPI not installed. Install with: pip install fastapi uvicorn")
            sys.exit(1)

        from cai_agent.protocol.a2a_card import create_cai_agent_card
        from cai_agent.protocol.a2a_models import (
            Artifact,
            Message,
            Task,
            TaskCancelRequest,
            TaskQueryRequest,
            TaskSendRequest,
            TaskState,
            TaskStatus,
            TextPart,
            agent_card_to_dict,
            task_to_dict,
        )

        app = FastAPI(
            title="Cai Agent A2A Server",
            description="Agent-to-Agent Protocol server for Cai Agent",
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

        # 认证中间件
        if self._api_key:
            @app.middleware("http")
            async def auth_middleware(request: Request, call_next):
                # AgentCard 端点不需要认证
                if request.url.path == "/.well-known/agent.json":
                    return await call_next(request)

                auth_header = request.headers.get("Authorization", "")
                if auth_header.startswith("Bearer "):
                    token = auth_header[7:]
                    if token == self._api_key:
                        return await call_next(request)

                return JSONResponse(
                    status_code=401,
                    content={"error": "Unauthorized", "message": "Invalid or missing API key"},
                )

        # AgentCard 端点
        @app.get("/.well-known/agent.json")
        async def get_agent_card() -> dict:
            url = f"http://{self._host}:{self._port}"
            card = create_cai_agent_card(
                url=url,
                api_key=self._api_key,
            )
            return agent_card_to_dict(card)

        # 发送任务
        @app.post("/a2a/tasks/send")
        async def send_task(request: dict) -> dict:
            # 解析请求
            task_id = request.get("id", str(uuid.uuid4()))
            session_id = request.get("sessionId", str(uuid.uuid4()))
            message_data = request.get("message", {})

            # 提取消息内容
            parts = message_data.get("parts", [])
            goal = ""
            for part in parts:
                if part.get("type") == "text":
                    goal += part.get("text", "")

            if not goal:
                raise HTTPException(status_code=400, detail="Message must contain text part with goal")

            # 创建任务
            task = Task(
                id=task_id,
                session_id=session_id,
                status=TaskStatus(state=TaskState.SUBMITTED),
                history=[Message(role="user", parts=[TextPart(text=goal)])],
            )
            self._tasks[task_id] = task

            # 异步执行任务
            asyncio_task = asyncio.create_task(self._execute_task(task, goal))
            self._running_tasks[task_id] = asyncio_task

            return task_to_dict(task)

        # 同步发送任务（等待完成）
        @app.post("/a2a/tasks/sendSubscribe")
        async def send_task_subscribe(request: dict) -> dict:
            # 解析请求
            task_id = request.get("id", str(uuid.uuid4()))
            session_id = request.get("sessionId", str(uuid.uuid4()))
            message_data = request.get("message", {})

            # 提取消息内容
            parts = message_data.get("parts", [])
            goal = ""
            for part in parts:
                if part.get("type") == "text":
                    goal += part.get("text", "")

            if not goal:
                raise HTTPException(status_code=400, detail="Message must contain text part with goal")

            # 创建任务
            task = Task(
                id=task_id,
                session_id=session_id,
                status=TaskStatus(state=TaskState.SUBMITTED),
                history=[Message(role="user", parts=[TextPart(text=goal)])],
            )
            self._tasks[task_id] = task

            # 同步执行任务
            await self._execute_task(task, goal)

            return task_to_dict(task)

        # 查询任务
        @app.post("/a2a/tasks/get")
        async def get_task(request: dict) -> dict:
            task_id = request.get("id", "")
            if not task_id:
                raise HTTPException(status_code=400, detail="Task id is required")

            task = self._tasks.get(task_id)
            if not task:
                raise HTTPException(status_code=404, detail=f"Task not found: {task_id}")

            return task_to_dict(task)

        # 取消任务
        @app.post("/a2a/tasks/cancel")
        async def cancel_task(request: dict) -> dict:
            task_id = request.get("id", "")
            if not task_id:
                raise HTTPException(status_code=400, detail="Task id is required")

            task = self._tasks.get(task_id)
            if not task:
                raise HTTPException(status_code=404, detail=f"Task not found: {task_id}")

            # 取消正在运行的任务
            asyncio_task = self._running_tasks.get(task_id)
            if asyncio_task and not asyncio_task.done():
                asyncio_task.cancel()
                try:
                    await asyncio_task
                except asyncio.CancelledError:
                    pass

            task.status = TaskStatus(state=TaskState.CANCELED)
            return task_to_dict(task)

        # SSE 流式任务
        @app.post("/a2a/tasks/sendStream")
        async def send_task_stream(request: dict):
            from fastapi.responses import StreamingResponse

            # 解析请求
            task_id = request.get("id", str(uuid.uuid4()))
            session_id = request.get("sessionId", str(uuid.uuid4()))
            message_data = request.get("message", {})

            # 提取消息内容
            parts = message_data.get("parts", [])
            goal = ""
            for part in parts:
                if part.get("type") == "text":
                    goal += part.get("text", "")

            if not goal:
                raise HTTPException(status_code=400, detail="Message must contain text part with goal")

            # 创建任务
            task = Task(
                id=task_id,
                session_id=session_id,
                status=TaskStatus(state=TaskState.SUBMITTED),
                history=[Message(role="user", parts=[TextPart(text=goal)])],
            )
            self._tasks[task_id] = task

            async def event_stream():
                # 发送初始状态
                yield f"data: {json.dumps(task_to_dict(task))}\n\n"

                # 执行任务并发送更新
                task.status = TaskStatus(state=TaskState.WORKING)
                yield f"data: {json.dumps(task_to_dict(task))}\n\n"

                try:
                    await self._execute_task(task, goal)
                    yield f"data: {json.dumps(task_to_dict(task))}\n\n"
                except Exception as e:
                    task.status = TaskStatus(state=TaskState.FAILED)
                    yield f"data: {json.dumps(task_to_dict(task))}\n\n"

            return StreamingResponse(
                event_stream(),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                },
            )

        # 健康检查
        @app.get("/health")
        async def health() -> dict:
            return {
                "status": "healthy",
                "service": "cai-agent-a2a",
                "version": "0.21.0",
                "active_tasks": len([t for t in self._tasks.values() if t.status.state == TaskState.WORKING]),
                "total_tasks": len(self._tasks),
            }

        return app

    async def _execute_task(self, task: Any, goal: str) -> None:
        """执行任务"""
        from cai_agent.protocol.a2a_models import (
            Artifact,
            TaskState,
            TaskStatus,
            TextPart,
        )

        try:
            task.status = TaskStatus(state=TaskState.WORKING)

            # 获取配置
            settings = self._get_settings()

            # 执行 Agent
            from cai_agent.graph import build_app, initial_state
            app_graph = build_app(settings)
            final_state = app_graph.invoke(initial_state(goal))

            # 提取结果
            answer = final_state.get("answer", "")
            files = final_state.get("files", [])
            total_tokens = final_state.get("total_tokens", 0)

            # 构建响应
            task.status = TaskStatus(state=TaskState.COMPLETED)
            task.artifacts = [
                Artifact(
                    name="answer",
                    description="Agent 的回答",
                    parts=[TextPart(text=answer)],
                ),
            ]

            # 如果有文件变更，添加文件列表
            if files:
                task.artifacts.append(
                    Artifact(
                        name="files",
                        description="变更的文件列表",
                        parts=[TextPart(text=json.dumps(files, ensure_ascii=False))],
                    )
                )

            task.metadata = {
                "total_tokens": total_tokens,
                "iteration": final_state.get("iteration", 0),
            }

        except asyncio.CancelledError:
            task.status = TaskStatus(state=TaskState.CANCELED)
            raise
        except Exception as e:
            logger.exception("Error executing task")
            task.status = TaskStatus(
                state=TaskState.FAILED,
                message=TextPart(text=str(e)[:800]),
            )
        finally:
            # 清理
            self._running_tasks.pop(task.id, None)

    def run(self) -> None:
        """启动服务器"""
        try:
            import uvicorn
        except ImportError:
            logger.error("uvicorn not installed. Install with: pip install uvicorn")
            sys.exit(1)

        app = self._create_app()
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
    """A2A Server CLI 入口"""
    import argparse

    parser = argparse.ArgumentParser(description="Cai Agent A2A Server")
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="监听地址，默认 0.0.0.0",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8080,
        help="监听端口，默认 8080",
    )
    parser.add_argument(
        "--config",
        default=None,
        help="配置文件路径",
    )
    parser.add_argument(
        "--api-key",
        default=None,
        help="API 密钥（可选，用于认证）",
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
    server = CaiAgentA2AServer(
        settings,
        host=args.host,
        port=args.port,
        api_key=args.api_key,
    )

    # 启动
    logger.info(f"Starting Cai Agent A2A Server on {args.host}:{args.port}")
    server.run()


if __name__ == "__main__":
    main()
