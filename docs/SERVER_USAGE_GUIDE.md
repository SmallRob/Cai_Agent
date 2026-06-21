# Cai Agent 服务端使用指南

本指南介绍如何启动 Cai Agent 的 MCP Server、A2A Server 和 ACP Server，使其可以被其他 Agent 发现和调用。

---

## 1. 安装依赖

### 1.1 安装 MCP Server 依赖

```bash
pip install cai-agent[mcp]
```

### 1.2 安装 A2A Server 依赖

```bash
pip install cai-agent[a2a]
```

### 1.3 安装 ACP Server 依赖

```bash
pip install cai-agent[acp]
```

### 1.4 安装所有服务端依赖

```bash
pip install cai-agent[server]
```

---

## 2. MCP Server 使用

MCP（Model Context Protocol）Server 允许 Claude、Cursor、ChatGPT 等 LLM 直接调用 Cai Agent 的功能。

### 2.1 启动模式

#### stdio 模式（本地集成）

适用于本地 IDE 集成，如 Cursor、VS Code Copilot 等。

```bash
# 直接启动
cai-agent serve mcp

# 或指定工作区
cai-agent serve mcp -w /path/to/project
```

#### SSE 模式（远程集成）

适用于远程调用，如 Claude Desktop、Web 应用等。

```bash
# 启动 SSE 服务
cai-agent serve mcp --transport sse --port 8090

# 指定监听地址
cai-agent serve mcp --transport sse --host 0.0.0.0 --port 8090
```

### 2.2 Claude Desktop 配置

在 Claude Desktop 的配置文件中添加：

```json
{
  "mcpServers": {
    "cai-agent": {
      "command": "python",
      "args": ["-m", "cai_agent.server.mcp_server"],
      "env": {
        "CAI_WORKSPACE": "/path/to/your/project"
      }
    }
  }
}
```

或使用 SSE 模式：

```json
{
  "mcpServers": {
    "cai-agent": {
      "url": "http://localhost:8090/sse"
    }
  }
}
```

### 2.3 Cursor 配置

在 Cursor 的设置中，找到 MCP Server 配置，添加：

```json
{
  "cai-agent": {
    "command": "cai-agent",
    "args": ["serve", "mcp"],
    "env": {
      "CAI_WORKSPACE": "/path/to/your/project"
    }
  }
}
```

### 2.4 可用工具

MCP Server 暴露以下工具：

| 工具名 | 描述 |
|--------|------|
| `cai_agent_run` | 执行 Agent 任务 |
| `cai_agent_plan` | 生成实施计划 |
| `cai_agent_workflow` | 运行工作流 |
| `cai_agent_doc_generate` | 生成文档 |
| `cai_agent_doc_review` | 审查文档 |
| `cai_agent_doctor` | 诊断环境 |
| `cai_agent_list_workflows` | 列出工作流 |

### 2.5 使用示例

在 Claude 中使用：

```
请使用 cai_agent_run 工具，帮我修复 src/auth.py 中的登录验证 bug。
```

```
请使用 cai_agent_doc_generate 工具，生成项目的 API 文档。
```

---

## 3. A2A Server 使用

A2A（Agent-to-Agent）Server 允许其他 Agent 通过标准协议发现和调用 Cai Agent。

### 3.1 启动服务

```bash
# 基本启动
cai-agent serve a2a

# 指定端口
cai-agent serve a2a --port 8080

# 启用 API Key 认证
cai-agent serve a2a --port 8080 --api-key your-secret-key
```

### 3.2 服务发现

启动后，其他 Agent 可以通过以下 URL 获取 AgentCard：

```
GET http://localhost:8080/.well-known/agent.json
```

### 3.3 API 端点

| 端点 | 方法 | 描述 |
|------|------|------|
| `/.well-known/agent.json` | GET | 获取 AgentCard |
| `/a2a/tasks/send` | POST | 发送任务（异步） |
| `/a2a/tasks/sendSubscribe` | POST | 发送任务（同步等待） |
| `/a2a/tasks/sendStream` | POST | 发送任务（SSE 流式） |
| `/a2a/tasks/get` | POST | 查询任务状态 |
| `/a2a/tasks/cancel` | POST | 取消任务 |
| `/health` | GET | 健康检查 |

### 3.4 使用示例

#### 发送异步任务

```bash
curl -X POST http://localhost:8080/a2a/tasks/send \
  -H "Content-Type: application/json" \
  -d '{
    "message": {
      "parts": [
        {
          "type": "text",
          "text": "帮我分析 src/auth.py 的安全性"
        }
      ]
    }
  }'
```

#### 查询任务状态

```bash
curl -X POST http://localhost:8080/a2a/tasks/get \
  -H "Content-Type: application/json" \
  -d '{
    "id": "task-id-from-send-response"
  }'
```

#### 同步发送任务（等待完成）

```bash
curl -X POST http://localhost:8080/a2a/tasks/sendSubscribe \
  -H "Content-Type: application/json" \
  -d '{
    "message": {
      "parts": [
        {
          "type": "text",
          "text": "生成项目的 README 文档"
        }
      ]
    }
  }'
```

### 3.5 Python 客户端示例

```python
import httpx

# 发送任务
response = httpx.post(
    "http://localhost:8080/a2a/tasks/send",
    json={
        "message": {
            "parts": [
                {"type": "text", "text": "帮我修复登录 bug"}
            ]
        }
    }
)
task = response.json()
task_id = task["id"]

# 查询状态
status_response = httpx.post(
    "http://localhost:8080/a2a/tasks/get",
    json={"id": task_id}
)
print(status_response.json())
```

---

## 4. ACP Server 使用

ACP（Agent Communication Protocol）是由 AgentUnion 提出的 Agent 通信协议，支持 Agent 发现、会话管理和消息传递。

### 4.1 启动服务

```bash
# 默认启动（端口 8070）
cai-agent serve acp

# 指定端口
cai-agent serve acp --port 9000

# 指定工作区
cai-agent serve acp -w /path/to/project

# 启用认证
cai-agent serve acp --api-key your-secret-key
```

### 4.2 服务发现

```bash
# 获取 AgentProfile（标准路径）
curl http://localhost:8070/.well-known/agentprofile.json

# 获取 AgentProfile（ACP 路径）
curl http://localhost:8070/acp/agent/profile
```

### 4.3 API 端点

| 端点 | 方法 | 描述 |
|------|------|------|
| `/.well-known/agentprofile.json` | GET | AgentProfile（Well-Known） |
| `/acp/agent/profile` | GET | AgentProfile |
| `/acp/sessions/create` | POST | 创建会话 |
| `/acp/sessions/join` | POST | 加入会话 |
| `/acp/sessions/leave` | POST | 离开会话 |
| `/acp/sessions/close` | POST | 关闭会话 |
| `/acp/sessions/get` | POST | 获取会话信息 |
| `/acp/sessions/list` | GET | 列出所有会话 |
| `/acp/messages/send` | POST | 发送消息 |
| `/acp/messages/receive` | POST | 接收消息 |
| `/acp/messages/stream` | POST | 流式接收消息（SSE） |
| `/acp/tasks/execute` | POST | 执行任务 |
| `/acp/tasks/execute/stream` | POST | 流式执行任务（SSE） |
| `/health` | GET | 健康检查 |
| `/acp/health` | GET | ACP 健康检查 |

### 4.4 使用示例

#### 创建会话

```bash
curl -X POST http://localhost:8070/acp/sessions/create \
  -H "Content-Type: application/json" \
  -d '{
    "creator_aid": "agent:external-agent-001",
    "participants": ["agent:cai-agent"],
    "metadata": {"purpose": "code_review"}
  }'
```

#### 执行任务

```bash
curl -X POST http://localhost:8070/acp/tasks/execute \
  -H "Content-Type: application/json" \
  -d '{
    "sender_aid": "agent:external-agent-001",
    "session_id": "your-session-id",
    "goal": "分析 src/ 目录的代码质量",
    "task_type": "run",
    "params": {
      "max_iterations": 10
    }
  }'
```

#### 任务类型

| task_type | 描述 | params |
|-----------|------|--------|
| `run` | 执行 agent 普通任务 | `max_iterations`, `model`, `workspace` |
| `plan` | 执行规划任务 | `mode` (quick/full), `model` |
| `workflow` | 执行工作流 | `workflow_id`, `workflow_json`, `timeout_sec` |
| `doc` | 执行文档生成 | `doc_type`, `output`, `source_dirs`, `language` |

#### 流式任务执行（SSE）

```bash
curl -X POST http://localhost:8070/acp/tasks/execute/stream \
  -H "Content-Type: application/json" \
  -d '{
    "sender_aid": "agent:external-agent-001",
    "goal": "实现一个 TODO 应用",
    "task_type": "run"
  }'
```

#### 发送消息

```bash
curl -X POST http://localhost:8070/acp/messages/send \
  -H "Content-Type: application/json" \
  -d '{
    "sender_aid": "agent:external-agent-001",
    "receiver_aid": "agent:cai-agent",
    "session_id": "your-session-id",
    "content": {"type": "text", "content": "请帮我审查 main.py"},
    "content_type": 1
  }'
```

### 4.5 Python 客户端示例

```python
import requests

BASE_URL = "http://localhost:8070"

# 1. 创建会话
session_resp = requests.post(f"{BASE_URL}/acp/sessions/create", json={
    "creator_aid": "agent:my-agent",
    "participants": ["agent:cai-agent"],
}).json()
session_id = session_resp["data"]["session_id"]

# 2. 执行任务
result = requests.post(f"{BASE_URL}/acp/tasks/execute", json={
    "sender_aid": "agent:my-agent",
    "session_id": session_id,
    "goal": "优化 utils.py 的性能",
    "task_type": "run",
    "params": {"max_iterations": 10},
}).json()
print(result["data"]["answer"])

# 3. 关闭会话
requests.post(f"{BASE_URL}/acp/sessions/close", json={
    "session_id": session_id,
    "creator_aid": "agent:my-agent",
})
```

---

## 5. 同时启动所有服务

```bash
# 同时启动 MCP、A2A 和 ACP 服务
cai-agent serve all

# 指定端口
cai-agent serve all --mcp-port 8090 --a2a-port 8080 --acp-port 8070

# 启用认证
cai-agent serve all --api-key your-secret-key
```

---

## 6. 配置说明

### 6.1 环境变量

| 变量名 | 描述 | 默认值 |
|--------|------|--------|
| `CAI_WORKSPACE` | 工作区路径 | 当前目录 |
| `CAI_API_KEY` | LLM API Key | - |
| `CAI_BASE_URL` | LLM API Base URL | - |
| `CAI_MODEL` | 默认模型 | gpt-4o |

### 6.2 配置文件

创建 `cai-agent.toml` 配置文件：

```toml
[llm]
api_key = "your-api-key"
base_url = "https://api.openai.com/v1"
model = "gpt-4o"

[agent]
max_iterations = 15
max_tokens = 128000

[server]
mcp_port = 8090
a2a_port = 8080
acp_port = 8070
api_key = "your-a2a-api-key"
```

---

## 7. 安全建议

### 7.1 生产环境部署

1. **启用 API Key 认证**：始终在生产环境使用 `--api-key` 参数
2. **限制监听地址**：使用 `--host 127.0.0.1` 仅监听本地
3. **使用反向代理**：通过 Nginx/Caddy 等添加 HTTPS
4. **限制工作区**：确保 `CAI_WORKSPACE` 指向安全目录

### 7.2 防火墙配置

```bash
# 仅允许本地访问
ufw allow from 127.0.0.1 to any port 8080
ufw allow from 127.0.0.1 to any port 8090
ufw allow from 127.0.0.1 to any port 8070
```

---

## 8. 故障排查

### 8.1 依赖问题

```bash
# 检查依赖
cai-agent doctor

# 手动安装依赖
pip install mcp fastapi uvicorn starlette
```

### 8.2 端口占用

```bash
# 检查端口占用
netstat -tuln | grep 8080
netstat -tuln | grep 8090
netstat -tuln | grep 8070

# 杀死占用进程
kill -9 <PID>
```

### 8.3 日志调试

```bash
# 启用详细日志
PYTHONPATH=src python -m cai_agent.server.mcp_server --transport sse --port 8090 2>&1 | tee mcp.log
```

---

## 9. 更多资源

- [MCP 协议规范](https://modelcontextprotocol.io/)
- [A2A 协议规范](https://github.com/google/A2A)
- [ACP 协议规范](https://acp.agentunion.cn/introduction/)
- [Cai Agent 文档](../README.md)
