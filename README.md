# AI Chat Backend

AI Chat Backend 是一个基于 FastAPI 的 AI Chat 后端学习项目。当前版本为 `v0.2.0`，用于沉淀 AI 全栈转型第一阶段的后端基础能力，包括 FastAPI 工程结构、配置管理、统一异常处理、真实 LLM 调用、多轮上下文结构、SSE 流式输出和模型调用异常治理。

## 当前版本

```text
v0.2.0
```

## 已实现功能

### v0.1.0 基础能力

* FastAPI Web 服务
* Swagger API 文档
* 健康检查接口
* 版本信息接口
* Chat Mock 接口
* Pydantic 请求参数校验
* API / Schema / Service 分层结构
* `.env` 环境变量配置
* `.env.example` 配置模板
* 业务异常处理
* 兜底系统异常处理
* 基础日志输出

### v0.2.0 新增能力

* OpenAI-compatible SDK 接入
* DeepSeek API 调用
* `LLMService` 模型服务封装
* `POST /chat` 真实模型回答
* `system_prompt` 支持
* `history` 多轮上下文支持
* `POST /chat/stream` SSE 流式输出
* DeepSeek `stream=True` 真实模型流式返回
* SSE `event: message` / `event: done` 格式封装
* 模型调用超时配置
* 模型调用重试机制
* 模型调用错误分类
* 统一转换为业务错误码 `BizException`
* LLM 调用日志增强

## 技术栈

```text
Python 3.11+
FastAPI
Uvicorn
Pydantic
pydantic-settings
python-dotenv
OpenAI SDK
DeepSeek OpenAI-compatible API
```

## 项目结构

```text
ai-chat-backend/
├── app/
│   ├── api/
│   │   └── chat.py
│   ├── core/
│   │   ├── config.py
│   │   └── exceptions.py
│   ├── schemas/
│   │   └── chat.py
│   ├── services/
│   │   ├── chat_service.py
│   │   └── llm_service.py
│   └── main.py
├── scripts/
│   ├── __init__.py
│   └── test_llm.py
├── .env.example
├── .gitignore
├── README.md
└── requirements.txt
```

## 本地启动

### 1. 创建虚拟环境

```bash
python3.11 -m venv .venv
```

### 2. 激活虚拟环境

macOS / Linux:

```bash
source .venv/bin/activate
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

### 3. 安装依赖

```bash
.venv/bin/python -m pip install -r requirements.txt
```

### 4. 创建配置文件

```bash
cp .env.example .env
```

然后在 `.env` 中填入真实的 `LLM_API_KEY`。

### 5. 启动服务

```bash
.venv/bin/python -m uvicorn app.main:app --reload
```

服务启动后访问：

```text
http://127.0.0.1:8000
```

Swagger API 文档：

```text
http://127.0.0.1:8000/docs
```

## 环境变量说明

```env
APP_NAME=AI Chat Backend
APP_ENV=dev
APP_VERSION=0.2.0
DEBUG=true

LLM_PROVIDER=deepseek
LLM_BASE_URL=https://api.deepseek.com
LLM_API_KEY=replace-with-your-api-key
LLM_MODEL=deepseek-v4-flash
LLM_TIMEOUT=60
LLM_MAX_RETRIES=2
LLM_RETRY_INTERVAL=1
```

| 配置项                  | 作用                       |
| -------------------- | ------------------------ |
| `APP_NAME`           | 应用名称                     |
| `APP_ENV`            | 当前运行环境                   |
| `APP_VERSION`        | 当前应用版本                   |
| `DEBUG`              | 是否开启调试模式                 |
| `LLM_PROVIDER`       | 模型供应商                    |
| `LLM_BASE_URL`       | OpenAI-compatible API 地址 |
| `LLM_API_KEY`        | 模型 API Key               |
| `LLM_MODEL`          | 默认模型名称                   |
| `LLM_TIMEOUT`        | 模型调用超时时间                 |
| `LLM_MAX_RETRIES`    | 模型调用最大重试次数               |
| `LLM_RETRY_INTERVAL` | 模型调用重试间隔                 |

注意：`.env` 文件包含真实配置，不应提交到 Git。

## API 说明

### GET `/`

根接口，用于确认服务是否运行。

响应示例：

```json
{
  "message": "AI Chat Backend is running",
  "env": "dev"
}
```

### GET `/health`

健康检查接口。

响应示例：

```json
{
  "status": "ok",
  "app_name": "AI Chat Backend",
  "version": "0.2.0",
  "env": "dev",
  "debug": true,
  "llm_model": "deepseek-v4-flash",
  "llm_base_url": "https://api.deepseek.com",
  "llm_api_key_configured": true
}
```

### GET `/version`

版本信息接口。

响应示例：

```json
{
  "app_name": "AI Chat Backend",
  "version": "0.2.0",
  "env": "dev"
}
```

### POST `/chat`

普通非流式 Chat 接口。

请求示例：

```json
{
  "message": "用一句话解释 FastAPI 是什么",
  "system_prompt": "你是一个擅长用大白话解释技术概念的 AI 助手。",
  "history": []
}
```

响应示例：

```json
{
  "reply": "FastAPI 是一个基于 Python 的现代 Web 框架，可以快速构建高性能 API，并自动生成接口文档。"
}
```

### POST `/chat/stream`

SSE 流式 Chat 接口。

请求示例：

```json
{
  "message": "用三句话解释 SSE 是什么",
  "system_prompt": "你是一个表达清晰的技术导师。",
  "history": []
}
```

响应示例：

```text
event: message
data: {"content": "SSE"}

event: message
data: {"content": " 是一种"}

event: done
data: {"message": "[DONE]"}
```

## 多轮上下文格式

请求体中的 `history` 支持 `user` 和 `assistant` 两种角色：

```json
{
  "system_prompt": "你是一个擅长用前端工程师视角解释后端概念的 AI 助手。",
  "history": [
    {
      "role": "user",
      "content": "venv 是什么？"
    },
    {
      "role": "assistant",
      "content": "venv 是 Python 的项目级虚拟环境，可以类比成前端项目里的 node_modules。"
    }
  ],
  "message": "那它和 node_modules 最大的区别是什么？"
}
```

注意：`history` 中不允许传入 `system` 角色，避免前端注入系统级指令。

## 错误处理

### 参数校验错误

当 `message` 为空时，接口会返回 `422`。

### 业务异常

请求：

```json
{
  "message": "这是违规内容"
}
```

响应：

```json
{
  "success": false,
  "error_code": "INVALID_CHAT_CONTENT",
  "message": "输入内容不符合规范，请修改后重试"
}
```

### 模型调用异常

模型调用失败时，后端会将 OpenAI SDK / DeepSeek API 异常统一转换为业务错误码。

常见错误码：

| error_code                   | 含义           |
| ---------------------------- | ------------ |
| `LLM_API_KEY_NOT_CONFIGURED` | API Key 未配置  |
| `LLM_AUTH_FAILED`            | API Key 认证失败 |
| `LLM_BAD_REQUEST`            | 模型请求参数错误     |
| `LLM_RATE_LIMITED`           | 请求过快或限流      |
| `LLM_TIMEOUT`                | 模型服务响应超时     |
| `LLM_CONNECTION_FAILED`      | 模型服务连接失败     |
| `LLM_PROVIDER_SERVER_ERROR`  | 模型服务端异常      |
| `LLM_STREAM_INTERRUPTED`     | 流式输出中断       |
| `LLM_CALL_FAILED`            | 模型调用失败       |

## 当前版本边界

当前版本暂未实现：

* 用户注册 / 登录
* JWT 鉴权
* PostgreSQL 数据存储
* 多会话管理
* 对话历史持久化
* Prompt 模板管理
* Token 统计
* Docker Compose 部署
* 前端 Chat UI
* RAG 知识库
* Tool Calling / Agent 能力

这些能力会在后续版本中逐步实现。

## 版本规划

| 版本     | 目标                              |
| ------ | ------------------------------- |
| v0.1.0 | FastAPI 基础服务、项目结构、配置管理、异常处理     |
| v0.2.0 | 真实 LLM 调用、多轮上下文、SSE 流式输出、模型异常治理 |
| v0.3.0 | PostgreSQL 接入、用户 / 会话 / 消息数据模型  |
| v0.4.0 | 登录、JWT 鉴权、多会话、历史记录              |
| v0.5.0 | Prompt 模板、Token 统计、模型调用日志       |
| v1.0.0 | Docker Compose、本地完整交付版本         |
