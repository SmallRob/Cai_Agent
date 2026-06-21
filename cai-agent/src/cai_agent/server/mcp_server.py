"""Cai Agent MCP Server 实现。

将 Cai Agent 的核心功能暴露为 MCP 工具，使其可以被 Claude、Cursor 等 MCP Client 调用。

使用方式：
    # stdio 模式（默认，用于本地集成）
    python -m cai_agent.server.mcp_server

    # SSE 模式（用于远程集成）
    python -m cai_agent.server.mcp_server --transport sse --port 8090
"""

from __future__ import annotations

import asyncio
import json
import logging
import sys
from dataclasses import replace
from typing import Any

from cai_agent.config import Settings
from cai_agent.protocol.mcp_tools import CAI_AGENT_MCP_TOOLS

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# MCP Server 实现
# ---------------------------------------------------------------------------

class CaiAgentMCPServer:
    """Cai Agent MCP Server。

    将 Cai Agent 的功能暴露为 MCP 工具，支持 stdio 和 SSE 两种传输模式。
    """

    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings
        self._tool_handlers: dict[str, Any] = {
            "cai_agent_run": self._handle_run,
            "cai_agent_plan": self._handle_plan,
            "cai_agent_workflow": self._handle_workflow,
            "cai_agent_doc_generate": self._handle_doc_generate,
            "cai_agent_doc_review": self._handle_doc_review,
            "cai_agent_doctor": self._handle_doctor,
            "cai_agent_list_workflows": self._handle_list_workflows,
        }

    def _get_settings(self, workspace: str | None = None, model: str | None = None) -> Settings:
        """获取配置，可选覆盖 workspace 和 model"""
        settings = self._settings or Settings.from_env()
        if workspace:
            settings = replace(settings, workspace=workspace)
        if model:
            settings = replace(settings, model=model)
        return settings

    async def _handle_run(self, arguments: dict[str, Any]) -> dict[str, Any]:
        """处理 cai_agent_run 工具调用"""
        from cai_agent.graph import build_app, initial_state

        goal = arguments.get("goal", "")
        if not goal:
            return {"ok": False, "error": "goal is required"}

        settings = self._get_settings(
            workspace=arguments.get("workspace"),
            model=arguments.get("model"),
        )
        max_iterations = arguments.get("max_iterations", 15)

        try:
            app = build_app(settings, max_iterations=max_iterations)
            final_state = app.invoke(initial_state(goal))

            return {
                "ok": True,
                "answer": final_state.get("answer", ""),
                "goal": final_state.get("goal", ""),
                "iteration": final_state.get("iteration", 0),
                "total_tokens": final_state.get("total_tokens", 0),
                "files": final_state.get("files", []),
            }
        except Exception as e:
            logger.exception("Error in cai_agent_run")
            return {"ok": False, "error": str(e)[:800]}

    async def _handle_plan(self, arguments: dict[str, Any]) -> dict[str, Any]:
        """处理 cai_agent_plan 工具调用"""
        from cai_agent.agents import create_agent

        goal = arguments.get("goal", "")
        if not goal:
            return {"ok": False, "error": "goal is required"}

        mode = arguments.get("mode", "full")
        settings = self._get_settings(
            workspace=arguments.get("workspace"),
            model=arguments.get("model"),
        )

        try:
            if mode == "quick":
                # 快速规划模式
                agent = create_agent(settings, role="default", max_iterations=5)
                prompt = (
                    f"快速规划任务：{goal}\n"
                    "请用 3-5 个步骤概括实施计划，每个步骤用一句话描述。"
                )
            else:
                # 完整规划模式
                agent = create_agent(settings, role="default", max_iterations=10)
                prompt = (
                    f"规划任务：{goal}\n"
                    "请生成详细的实施计划，包括：\n"
                    "1. 步骤分解\n"
                    "2. 依赖分析\n"
                    "3. 风险评估\n"
                    "4. 预估工作量"
                )

            final_state = agent.run(prompt)

            return {
                "ok": True,
                "plan": final_state.get("answer", ""),
                "mode": mode,
                "total_tokens": final_state.get("total_tokens", 0),
            }
        except Exception as e:
            logger.exception("Error in cai_agent_plan")
            return {"ok": False, "error": str(e)[:800]}

    async def _handle_workflow(self, arguments: dict[str, Any]) -> dict[str, Any]:
        """处理 cai_agent_workflow 工具调用"""
        from cai_agent.workflow import run_workflow

        goal = arguments.get("goal", "")
        if not goal:
            return {"ok": False, "error": "goal is required"}

        workflow_id = arguments.get("workflow_id")
        workflow_json = arguments.get("workflow_json")
        settings = self._get_settings(
            workspace=arguments.get("workspace"),
            model=arguments.get("model"),
        )
        timeout_sec = arguments.get("timeout_sec", 600)

        try:
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
                "elapsed_ms": result.get("elapsed_ms", 0),
            }
        except Exception as e:
            logger.exception("Error in cai_agent_workflow")
            return {"ok": False, "error": str(e)[:800]}

    async def _handle_doc_generate(self, arguments: dict[str, Any]) -> dict[str, Any]:
        """处理 cai_agent_doc_generate 工具调用"""
        from cai_agent.doc_writer import DocGenerateRequest, generate_doc

        doc_type = arguments.get("doc_type", "")
        if not doc_type:
            return {"ok": False, "error": "doc_type is required"}

        settings = self._get_settings(
            workspace=arguments.get("workspace"),
            model=arguments.get("model"),
        )

        request = DocGenerateRequest(
            doc_type=doc_type,
            output_path=arguments.get("output", ""),
            source_dirs=arguments.get("source_dirs", ["."]),
            language=arguments.get("language", "zh-CN"),
            goal_extra=arguments.get("goal_extra", ""),
        )

        try:
            result = generate_doc(settings, request)

            return {
                "ok": result.ok,
                "output_path": result.output_path,
                "doc_type": result.doc_type,
                "sections_generated": result.sections_generated,
                "word_count": result.word_count,
                "elapsed_ms": result.elapsed_ms,
                "tokens_used": result.tokens_used,
                "error": result.error,
            }
        except Exception as e:
            logger.exception("Error in cai_agent_doc_generate")
            return {"ok": False, "error": str(e)[:800]}

    async def _handle_doc_review(self, arguments: dict[str, Any]) -> dict[str, Any]:
        """处理 cai_agent_doc_review 工具调用"""
        from cai_agent.doc_writer import review_doc

        file_path = arguments.get("file_path", "")
        if not file_path:
            return {"ok": False, "error": "file_path is required"}

        settings = self._get_settings(
            workspace=arguments.get("workspace"),
            model=arguments.get("model"),
        )

        try:
            result = review_doc(settings, file_path)

            return {
                "ok": result.ok,
                "file_path": result.file_path,
                "score": result.score,
                "issues": result.issues,
                "suggestions": result.suggestions,
                "elapsed_ms": result.elapsed_ms,
                "tokens_used": result.tokens_used,
                "error": result.error,
            }
        except Exception as e:
            logger.exception("Error in cai_agent_doc_review")
            return {"ok": False, "error": str(e)[:800]}

    async def _handle_doctor(self, arguments: dict[str, Any]) -> dict[str, Any]:
        """处理 cai_agent_doctor 工具调用"""
        settings = self._get_settings(workspace=arguments.get("workspace"))

        try:
            from cai_agent.__main__ import _diagnose
            result = _diagnose(settings)
            return {"ok": True, "diagnostics": result}
        except Exception as e:
            logger.exception("Error in cai_agent_doctor")
            return {"ok": False, "error": str(e)[:800]}

    async def _handle_list_workflows(self, arguments: dict[str, Any]) -> dict[str, Any]:
        """处理 cai_agent_list_workflows 工具调用"""
        from cai_agent.workflow import load_template

        settings = self._get_settings(workspace=arguments.get("workspace"))

        try:
            # 获取内置模板
            from cai_agent.workflow import _BUILTIN_TEMPLATES
            templates = {}
            for name, template in _BUILTIN_TEMPLATES.items():
                templates[name] = {
                    "description": template.get("description", ""),
                    "steps": len(template.get("steps", [])),
                    "source": "builtin",
                }

            # 尝试加载用户自定义模板
            try:
                user_template = load_template(settings)
                if user_template:
                    templates["user-custom"] = {
                        "description": user_template.get("description", "User custom workflow"),
                        "steps": len(user_template.get("steps", [])),
                        "source": "user",
                    }
            except Exception:
                pass

            return {"ok": True, "workflows": templates}
        except Exception as e:
            logger.exception("Error in cai_agent_list_workflows")
            return {"ok": False, "error": str(e)[:800]}

    async def handle_tool_call(self, name: str, arguments: dict[str, Any]) -> list[dict[str, Any]]:
        """处理工具调用请求"""
        handler = self._tool_handlers.get(name)
        if not handler:
            return [{"type": "text", "text": json.dumps({"ok": False, "error": f"Unknown tool: {name}"})}]

        result = await handler(arguments)
        return [{"type": "text", "text": json.dumps(result, ensure_ascii=False)}]

    def get_tools(self) -> list[dict[str, Any]]:
        """获取工具列表"""
        return CAI_AGENT_MCP_TOOLS


# ---------------------------------------------------------------------------
# MCP Server 启动器
# ---------------------------------------------------------------------------

async def run_mcp_stdio(server: CaiAgentMCPServer) -> None:
    """以 stdio 模式运行 MCP Server"""
    try:
        from mcp.server import Server
        from mcp.server.stdio import stdio_server
        from mcp.types import TextContent, Tool
    except ImportError:
        logger.error("MCP SDK not installed. Install with: pip install mcp")
        sys.exit(1)

    app = Server("cai-agent-mcp")

    @app.list_tools()
    async def list_tools() -> list[Tool]:
        return [Tool(**t) for t in server.get_tools()]

    @app.call_tool()
    async def call_tool(name: str, arguments: dict) -> list[TextContent]:
        results = await server.handle_tool_call(name, arguments)
        return [TextContent(**r) for r in results]

    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream)


async def run_mcp_sse(server: CaiAgentMCPServer, host: str = "0.0.0.0", port: int = 8090) -> None:
    """以 SSE 模式运行 MCP Server"""
    try:
        from mcp.server import Server
        from mcp.server.sse import SseServerTransport
        from mcp.types import TextContent, Tool
        from starlette.applications import Starlette
        from starlette.routing import Mount, Route
    except ImportError:
        logger.error("MCP SDK or Starlette not installed. Install with: pip install mcp starlette uvicorn")
        sys.exit(1)

    app = Server("cai-agent-mcp")
    sse = SseServerTransport("/messages/")

    @app.list_tools()
    async def list_tools() -> list[Tool]:
        return [Tool(**t) for t in server.get_tools()]

    @app.call_tool()
    async def call_tool(name: str, arguments: dict) -> list[TextContent]:
        results = await server.handle_tool_call(name, arguments)
        return [TextContent(**r) for r in results]

    async def handle_sse(request):
        async with sse.connect_sse(request.scope, request.receive, request._send) as streams:
            await app.run(streams[0], streams[1], app.create_initialization_options())

    starlette_app = Starlette(
        routes=[
            Route("/sse", endpoint=handle_sse),
            Mount("/messages/", app=sse.handle_post_message),
        ],
    )

    import uvicorn
    config = uvicorn.Config(starlette_app, host=host, port=port, log_level="info")
    server_instance = uvicorn.Server(config)
    await server_instance.serve()


# ---------------------------------------------------------------------------
# CLI 入口
# ---------------------------------------------------------------------------

def main() -> None:
    """MCP Server CLI 入口"""
    import argparse

    parser = argparse.ArgumentParser(description="Cai Agent MCP Server")
    parser.add_argument(
        "--transport",
        choices=["stdio", "sse"],
        default="stdio",
        help="传输模式：stdio（本地）或 sse（远程），默认 stdio",
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="SSE 模式的监听地址，默认 0.0.0.0",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8090,
        help="SSE 模式的监听端口，默认 8090",
    )
    parser.add_argument(
        "--config",
        default=None,
        help="配置文件路径",
    )

    args = parser.parse_args()

    # 设置日志
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        stream=sys.stderr,  # MCP stdio 模式下日志必须输出到 stderr
    )

    # 加载配置
    try:
        settings = Settings.from_env(config_path=args.config)
    except Exception as e:
        logger.error(f"Failed to load config: {e}")
        sys.exit(1)

    # 创建服务器
    server = CaiAgentMCPServer(settings)

    # 运行
    if args.transport == "stdio":
        asyncio.run(run_mcp_stdio(server))
    else:
        asyncio.run(run_mcp_sse(server, host=args.host, port=args.port))


if __name__ == "__main__":
    main()
