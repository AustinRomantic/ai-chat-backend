# AI Chat Backend

AI Chat Backend 是一个基于 FastAPI 的 AI Chat 后端项目。当前版本为 `v0.1.0`，主要用于沉淀 AI 全栈转型第一阶段的后端基础能力，包括 FastAPI 服务、接口拆分、请求参数校验、环境变量配置、统一异常处理和基础日志。

## 当前版本

```text
v0.1.0
```

## 已实现功能

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

## 技术栈

```text
Python 3.11+
FastAPI
Uvicorn
Pydantic
pydantic-settings
python-dotenv
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
│   │   └── chat_service.py
│   └── main.py
├── .env.example
├── .gitignore
├── README.md
└── requirements.txt
```

## 本地启动

### 1. 创建虚拟环境

```bash
python -m venv .venv
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
python -m pip install -r requirements.txt
```

### 4. 创建配置文件

```bash
cp .env.example .env
```

### 5. 启动服务

```bash
python -m uvicorn app.main:app --reload
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
APP_VERSION=0.1.0
DEBUG=true

LLM_BASE_URL=https://api.deepseek.com
LLM_API_KEY=replace-with-your-api-key
LLM_MODEL=deepseek-chat
```

说明：

| 配置项            | 作用                   |
| -------------- | -------------------- |
| `APP_NAME`     | 应用名称                 |
| `APP_ENV`      | 当前运行环境               |
| `APP_VERSION`  | 当前应用版本               |
| `DEBUG`        | 是否开启调试模式             |
| `LLM_BASE_URL` | 大模型接口地址，当前版本暂未调用     |
| `LLM_API_KEY`  | 大模型 API Key，当前版本暂未调用 |
| `LLM_MODEL`    | 默认模型名称，当前版本暂未调用      |

注意：`.env` 文件包含本地真实配置，不应提交到 Git。

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
  "version": "0.1.0",
  "env": "dev",
  "debug": true,
  "llm_model": "deepseek-chat",
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
  "version": "0.1.0",
  "env": "dev"
}
```

### POST `/chat`

Chat Mock 接口。

请求示例：

```json
{
  "message": "你好，我正在学习 AI 全栈"
}
```

响应示例：

```json
{
  "reply": "你刚才说的是：你好，我正在学习 AI 全栈"
}
```

## 异常测试

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

### 系统异常

请求：

```json
{
  "message": "系统异常"
}
```

响应：

```json
{
  "success": false,
  "error_code": "INTERNAL_SERVER_ERROR",
  "message": "服务暂时不可用，请稍后重试"
}
```

## 当前版本边界

当前版本暂未实现：

* 用户注册 / 登录
* JWT 鉴权
* PostgreSQL 数据存储
* 多会话管理
* 真实 LLM API 调用
* SSE 流式输出
* Prompt 模板管理
* Token 统计
* Docker Compose 部署

这些能力会在后续版本中逐步实现。

## 版本规划

| 版本     | 目标                                          |
| ------ | ------------------------------------------- |
| v0.1.0 | FastAPI 基础服务、项目结构、配置管理、异常处理                 |
| v0.2.0 | 接入真实 LLM API、支持普通 Chat                      |
| v0.3.0 | 支持 SSE 流式输出                                 |
| v0.4.0 | 接入 PostgreSQL，实现会话和历史记录                     |
| v1.0.0 | 登录、鉴权、多会话、Prompt 模板、Token 统计、Docker Compose |
