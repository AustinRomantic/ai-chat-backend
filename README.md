# AI Chat Backend

AI Chat Backend 是一个基于 FastAPI、PostgreSQL 和大语言模型 API 构建的 AI Chat 后端学习项目。

当前版本为 `v0.3.0`，已从无状态 LLM 调用升级为支持用户、会话、消息持久化、数据库多轮上下文和 SSE 流式回答的完整后端系统。

## 当前版本

```text
v0.3.0
```

## 核心能力

### v0.1.0：FastAPI 工程基础

- FastAPI Web 服务
- Swagger/OpenAPI 文档
- Pydantic 参数校验
- API、Schema、Service 分层
- `.env` 环境变量配置
- 统一业务异常处理
- 全局系统异常处理
- 基础日志
- 健康检查和版本接口

### v0.2.0：真实 LLM 与流式输出

- OpenAI-compatible SDK
- DeepSeek API 接入
- LLMService 模型服务封装
- 普通非流式回答
- SSE 流式回答
- system prompt
- 多轮上下文组装
- LLM 超时配置
- 模型调用重试
- 模型异常分类
- 统一业务错误码
- LLM 调用日志

### v0.3.0：PostgreSQL 会话系统

- PostgreSQL 17
- SQLAlchemy 2.x ORM
- Psycopg 3 数据库驱动
- Alembic 数据库迁移
- User、Conversation、Message 数据模型
- 数据库连接池与健康检查
- 开发用户初始化
- Conversation REST API
- 会话分页和状态筛选
- 会话归属校验
- 消息历史分页
- 数据库驱动的多轮上下文
- 普通 Chat 消息持久化
- SSE Chat 消息持久化
- 事务 commit/rollback
- 会话更新时间维护
- pytest 自动化测试
- 独立测试数据库保护

## 系统架构

```text
Client
  │
  ├── Conversation REST API
  │       ↓
  │   Conversation Service
  │       ↓
  │   Repository
  │       ↓
  │   SQLAlchemy
  │       ↓
  │   PostgreSQL
  │
  └── Chat API
          ↓
      读取 Conversation
          ↓
      读取最近历史消息
          ↓
      保存 user 消息
          ↓
      LLMService
          ↓
      普通回答 / SSE 流式回答
          ↓
      保存 assistant 消息
```

## 数据模型

```text
User 1 ─────── N Conversation

Conversation 1 ─────── N Message
```

### User

用于保存用户基础信息。

主要字段：

```text
id
email
display_name
created_at
updated_at
```

### Conversation

表示一次独立的 AI 对话。

主要字段：

```text
id
user_id
title
system_prompt
status
created_at
updated_at
```

会话状态：

```text
active
archived
```

### Message

表示会话中的一条用户或助手消息。

主要字段：

```text
id
conversation_id
role
content
created_at
```

消息角色：

```text
user
assistant
```

## Chat 持久化策略

普通和流式 Chat 都使用以下事务策略：

```text
事务 1：保存 user 消息并提交
  ↓
调用 LLM
  ↓
事务 2：保存 assistant 消息并提交
```

这样即使 LLM 调用失败，用户问题仍然会保留，可以在后续实现“重新生成回答”。

SSE 流式回答不会逐 Token 写入数据库：

```text
流式 chunk
  ↓
立即发送给客户端
  ↓
在内存中拼接完整回答
  ↓
流式结束后只写一次 assistant 消息
```

每次调用模型时，只加载最近 10 条历史消息，防止上下文无限增长。

## 技术栈

- Python 3.11+
- FastAPI 0.128
- Uvicorn
- Pydantic 2.x
- pydantic-settings
- PostgreSQL 17
- SQLAlchemy 2.x
- Psycopg 3
- Alembic
- OpenAI SDK
- DeepSeek OpenAI-compatible API
- SSE
- pytest

## 项目结构

```text
ai-chat-backend/
├── alembic/
│   ├── versions/
│   │   └── 1026c78a0231_create_user_conversation_message_tables.py
│   ├── env.py
│   └── script.py.mako
├── app/
│   ├── api/
│   │   ├── chat.py
│   │   ├── conversation.py
│   │   └── summary.py
│   ├── core/
│   │   ├── config.py
│   │   └── exceptions.py
│   ├── db/
│   │   ├── base.py
│   │   └── session.py
│   ├── models/
│   │   ├── user.py
│   │   ├── conversation.py
│   │   └── message.py
│   ├── repositories/
│   │   ├── user_repository.py
│   │   ├── conversation_repository.py
│   │   └── message_repository.py
│   ├── schemas/
│   │   ├── chat.py
│   │   ├── conversation.py
│   │   ├── message.py
│   │   └── summary.py
│   ├── services/
│   │   ├── chat_service.py
│   │   ├── conversation_service.py
│   │   ├── llm_service.py
│   │   └── summary_service.py
│   └── main.py
├── scripts/
│   ├── seed_dev_user.py
│   ├── test_db.py
│   ├── test_llm.py
│   └── test_orm.py
├── tests/
│   ├── conftest.py
│   ├── test_chat.py
│   └── test_conversations.py
├── .env.example
├── .gitignore
├── alembic.ini
├── pytest.ini
├── README.md
└── requirements.txt
```

## 环境要求

开始前需要安装：

- Python 3.11+
- Docker Desktop
- Git

## 本地启动

### 1. 进入项目

```bash
cd /Users/duanjiqiang/Desktop/Enn/backend/ai-chat-backend
```

### 2. 创建虚拟环境

```bash
python3.11 -m venv .venv
```

### 3. 激活虚拟环境

macOS/Linux：

```bash
source .venv/bin/activate
```

Windows PowerShell：

```powershell
.venv\Scripts\Activate.ps1
```

### 4. 安装依赖

```bash
python3 -m pip install -r requirements.txt
```

### 5. 启动 PostgreSQL

首次创建：

```bash
docker run --name ai-chat-postgres \
  -e POSTGRES_USER=ai_chat_user \
  -e POSTGRES_PASSWORD=ai_chat_dev_password \
  -e POSTGRES_DB=ai_chat_db \
  -p 5432:5432 \
  -v ai_chat_pg_data:/var/lib/postgresql/data \
  --health-cmd="pg_isready -U ai_chat_user -d ai_chat_db" \
  --health-interval=5s \
  --health-timeout=5s \
  --health-retries=10 \
  -d postgres:17
```

容器已存在时：

```bash
docker start ai-chat-postgres
```

检查状态：

```bash
docker ps --filter "name=ai-chat-postgres"
```

状态应包含：

```text
healthy
```

### 6. 创建环境变量

```bash
cp .env.example .env
```

编辑 `.env`，填写：

- 真实 `LLM_API_KEY`
- 本地 PostgreSQL 密码
- 测试数据库地址

`.env` 包含敏感信息，不允许提交到 Git。

### 7. 执行数据库迁移

```bash
alembic upgrade head
```

检查版本：

```bash
alembic current
alembic check
```

### 8. 初始化开发用户

```bash
python3 -m scripts.seed_dev_user
```

首次执行：

```text
dev_user_status=created
```

再次执行：

```text
dev_user_status=already_exists
```

### 9. 启动 FastAPI

```bash
python3 -m uvicorn app.main:app --reload
```

服务地址：

```text
http://127.0.0.1:8000
```

Swagger：

```text
http://127.0.0.1:8000/docs
```

ReDoc：

```text
http://127.0.0.1:8000/redoc
```

## 环境变量

```env
APP_NAME=AI Chat Backend
APP_ENV=dev
APP_VERSION=0.3.0
DEBUG=true

LLM_PROVIDER=deepseek
LLM_BASE_URL=https://api.deepseek.com
LLM_API_KEY=replace-with-your-api-key
LLM_MODEL=deepseek-v4-flash
LLM_TIMEOUT=60
LLM_MAX_RETRIES=2
LLM_RETRY_INTERVAL=1

DATABASE_URL=postgresql+psycopg://ai_chat_user:replace-with-password@127.0.0.1:5432/ai_chat_db?connect_timeout=5
DB_ECHO=false

TEST_DATABASE_URL=postgresql+psycopg://ai_chat_user:replace-with-password@127.0.0.1:5432/ai_chat_test_db?connect_timeout=5

DEV_USER_EMAIL=dev@ai-chat.local
DEV_USER_DISPLAY_NAME=开发用户
```

配置说明：

- `APP_NAME`：应用名称
- `APP_ENV`：运行环境
- `APP_VERSION`：应用版本
- `DEBUG`：调试模式
- `LLM_PROVIDER`：模型供应商
- `LLM_BASE_URL`：OpenAI-compatible API 地址
- `LLM_API_KEY`：模型 API Key
- `LLM_MODEL`：模型名称
- `LLM_TIMEOUT`：模型超时时间
- `LLM_MAX_RETRIES`：最大重试次数
- `LLM_RETRY_INTERVAL`：重试间隔
- `DATABASE_URL`：开发数据库连接
- `DB_ECHO`：是否输出 SQL 日志
- `TEST_DATABASE_URL`：自动化测试数据库连接
- `DEV_USER_EMAIL`：当前开发用户邮箱
- `DEV_USER_DISPLAY_NAME`：当前开发用户名称

## API 说明

### GET `/`

服务运行状态。

```bash
curl http://127.0.0.1:8000/
```

### GET `/health`

应用健康检查。

```bash
curl http://127.0.0.1:8000/health
```

### GET `/health/db`

PostgreSQL连接检查。

```bash
curl http://127.0.0.1:8000/health/db
```

成功响应：

```json
{
  "status": "ok",
  "database": "ai_chat_db",
  "role": "ai_chat_user"
}
```

### GET `/version`

```bash
curl http://127.0.0.1:8000/version
```

响应：

```json
{
  "app_name": "AI Chat Backend",
  "version": "0.3.0",
  "env": "dev"
}
```

## Conversation API

### 创建会话

```http
POST /conversations
```

请求：

```json
{
  "title": "AI 全栈学习会话",
  "system_prompt": "你是一个耐心的 AI 全栈学习助手。"
}
```

测试：

```bash
curl -i -X POST http://127.0.0.1:8000/conversations \
  -H "Content-Type: application/json" \
  -d '{
    "title": "AI 全栈学习会话",
    "system_prompt": "你是一个耐心的 AI 全栈学习助手。"
  }'
```

### 查询会话列表

```http
GET /conversations?page=1&page_size=20
```

可选状态筛选：

```http
GET /conversations?page=1&page_size=20&status=active
GET /conversations?page=1&page_size=20&status=archived
```

### 查询会话详情

```http
GET /conversations/{conversation_id}
```

### 修改会话

```http
PATCH /conversations/{conversation_id}
```

请求示例：

```json
{
  "title": "新的会话标题",
  "status": "archived"
}
```

### 删除会话

```http
DELETE /conversations/{conversation_id}
```

删除会话时，所属消息通过数据库外键级联删除。

### 查询消息历史

```http
GET /conversations/{conversation_id}/messages?page=1&page_size=20
```

## Chat API

Chat 请求不再接受客户端传入的 `history` 和 `system_prompt`。

服务端根据 `conversation_id`：

1. 验证会话归属
2. 读取 Conversation 的 system prompt
3. 读取 PostgreSQL历史消息
4. 保存用户消息
5. 调用 LLM
6. 保存助手消息

### 普通 Chat

```http
POST /chat
```

请求：

```json
{
  "conversation_id": "真实会话 UUID",
  "message": "请解释什么是 ORM。"
}
```

响应：

```json
{
  "conversation_id": "会话 UUID",
  "user_message_id": "用户消息 UUID",
  "assistant_message_id": "助手消息 UUID",
  "reply": "模型回答"
}
```

测试：

```bash
CONVERSATION_ID="替换为真实会话 UUID"

curl -i -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d "{
    \"conversation_id\": \"$CONVERSATION_ID\",
    \"message\": \"请解释什么是 ORM。\"
  }"
```

### SSE 流式 Chat

```http
POST /chat/stream
```

测试：

```bash
curl -N -X POST http://127.0.0.1:8000/chat/stream \
  -H "Content-Type: application/json" \
  -d "{
    \"conversation_id\": \"$CONVERSATION_ID\",
    \"message\": \"用三句话解释数据库事务。\"
  }"
```

事件格式：

```text
event: message
data: {"content":"数据库"}

event: message
data: {"content":"事务"}

event: done
data: {
  "message":"[DONE]",
  "conversation_id":"...",
  "user_message_id":"...",
  "assistant_message_id":"..."
}
```

### 多轮上下文

客户端第二次请求仍然只提交：

```json
{
  "conversation_id": "同一个会话 UUID",
  "message": "我刚才问了什么？"
}
```

服务端会自动读取 PostgreSQL中的历史消息，不需要客户端重复提交 `history`。

## 数据库迁移

创建 Migration：

```bash
alembic revision --autogenerate -m "migration description"
```

升级到最新版本：

```bash
alembic upgrade head
```

查看当前版本：

```bash
alembic current
```

查看历史：

```bash
alembic history
```

检查 Model 和数据库是否一致：

```bash
alembic check
```

回退一个版本：

```bash
alembic downgrade -1
```

正式环境禁止使用 `Base.metadata.create_all()` 代替 Alembic。

## 自动化测试

### 创建测试数据库

首次执行：

```bash
docker exec ai-chat-postgres \
  createdb -U ai_chat_user ai_chat_test_db
```

如果数据库已经存在，不需要重复创建。

### 运行测试

```bash
python3 -m pytest -v
```

当前测试覆盖：

- Conversation 创建、查询、更新、删除
- Conversation 分页
- 普通 Chat 消息持久化
- 数据库多轮上下文
- SSE 完整回答持久化
- 归档会话禁止聊天
- 不存在会话返回 404

测试使用 Mock LLM，不调用真实模型，不消耗 Token。

测试只允许连接：

```text
ai_chat_test_db
```

`tests/conftest.py` 包含防误删检查，禁止测试连接开发数据库。

`pytest.ini` 将自动化测试范围限制在：

```text
tests/
```

`scripts/test_orm.py` 是人工学习脚本，不会被 pytest 自动收集。

## 常用开发命令

检查 Python 语法：

```bash
python3 -m compileall app scripts tests
```

检查数据库连接：

```bash
python3 -m scripts.test_db
```

检查 LLM：

```bash
python3 -m scripts.test_llm
```

运行 ORM 学习脚本：

```bash
python3 -m scripts.test_orm
```

运行自动化测试：

```bash
python3 -m pytest -v
```

检查 Migration：

```bash
alembic current
alembic check
```

## 错误响应格式

业务异常统一返回：

```json
{
  "success": false,
  "error_code": "ERROR_CODE",
  "message": "错误说明"
}
```

常见错误码：

- `CONVERSATION_NOT_FOUND`
- `CONVERSATION_ARCHIVED`
- `DEVELOPMENT_USER_NOT_FOUND`
- `INVALID_CHAT_CONTENT`
- `USER_MESSAGE_SAVE_FAILED`
- `ASSISTANT_MESSAGE_SAVE_FAILED`
- `DATABASE_UNAVAILABLE`
- `LLM_API_KEY_NOT_CONFIGURED`
- `LLM_AUTH_FAILED`
- `LLM_BAD_REQUEST`
- `LLM_RATE_LIMITED`
- `LLM_TIMEOUT`
- `LLM_CONNECTION_FAILED`
- `LLM_PROVIDER_SERVER_ERROR`
- `LLM_STREAM_INTERRUPTED`
- `LLM_EMPTY_RESPONSE`
- `LLM_CALL_FAILED`

## 当前版本边界

v0.3.0 暂未实现：

- 用户注册和登录
- JWT 鉴权
- 真实多用户身份
- 角色和权限
- Prompt 模板管理
- Token 用量统计
- 模型调用记录
- Redis
- Docker Compose 完整编排
- 前端 Chat UI
- RAG 知识库
- Tool Calling
- Agent Workflow
- 评测和观测

当前所有 API 使用 `.env` 中配置的开发用户：

```text
DEV_USER_EMAIL
```

因此当前版本仅适用于学习和本地开发，不适合直接部署到生产环境。

## 版本规划

- `v0.1.0`：FastAPI 工程基础、配置、异常处理
- `v0.2.0`：真实 LLM、多轮上下文、SSE、模型异常治理
- `v0.3.0`：PostgreSQL、Conversation API、消息持久化、自动化测试
- `v0.4.0`：用户注册、登录、密码安全、JWT 鉴权、用户隔离
- `v0.5.0`：Prompt 模板、Token 统计、模型调用日志
- `v1.0.0`：Docker Compose 和本地完整交付

## 安全说明

- 不要提交 `.env`
- 不要在日志中输出 API Key
- 不要在接口中返回数据库连接字符串
- 正式环境应关闭 `DEBUG`
- 正式环境必须替换开发用户机制
- 正式环境应使用强数据库密码
- 数据库 Migration 应作为独立部署步骤执行