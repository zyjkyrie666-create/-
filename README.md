# Industrial AI Agent Platform

Love AI, passionate about AI, AI embracing life.

一个面向企业场景的工业化 AI Agent 项目骨架，适合作为 GitHub 展示项目和简历项目。项目重点不是简单聊天，而是围绕企业真实落地需要构建：任务编排、工具治理、权限策略、审计追踪、可观测性、API 服务、CLI 和自动化测试。

## 项目亮点

- **Agent 编排引擎**：将用户任务拆解为计划、工具调用、结果汇总和审计记录。
- **企业级工具治理**：通过工具注册表统一管理工具能力、风险等级和角色权限。
- **策略与安全控制**：内置 Policy Engine，拦截高风险动作、越权工具调用和危险指令。
- **可观测性设计**：每次运行生成 trace、step、latency、policy decision 和 audit event。
- **可扩展 LLM 适配层**：默认使用可离线演示的规则规划器，可替换为 OpenAI、私有模型或企业网关。
- **工程化交付**：提供 FastAPI 接口、CLI、Dockerfile、docker-compose、单元测试和架构文档。

## 适合简历的项目描述

> 设计并实现企业级 AI Agent 平台，支持任务编排、工具注册、权限策略、审计追踪和可观测性；采用分层架构解耦 API、Agent Runtime、Tool Registry、Policy Engine 与持久化模块，内置离线可运行的规则规划器，并预留 OpenAI/私有大模型适配层；通过 Docker、自动化测试和结构化日志提升项目可部署性和工程质量。

## 快速开始

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[api,dev]"
python -m industrial_agent.cli "帮我分析今天的生产告警并生成处理建议"
```

如果只想验证核心逻辑，不安装任何第三方依赖也可以运行测试：

```powershell
$env:PYTHONPATH = "src"
python -m unittest discover -s tests
```

## 启动 API

```powershell
uvicorn industrial_agent.api.main:app --reload --host 0.0.0.0 --port 8000
```

示例请求：

```bash
curl -X POST http://localhost:8000/api/v1/runs \
  -H "Content-Type: application/json" \
  -d '{"user_id":"u-1001","role":"operator","query":"查询 TICKET-1001 并评估风险"}'
```

## 目录结构

```text
src/industrial_agent/
  agent/              # Agent 编排、运行状态和工具执行
  api/                # FastAPI HTTP 接口
  domain/             # 领域模型、策略、工具契约
  infrastructure/     # SQLite 仓储、审计日志
  llm/                # LLM 适配层
  observability/      # trace/span 记录
tests/                # 标准库 unittest 测试
docs/                 # 架构与简历材料
```

## 环境变量

复制 `.env.example` 后按需配置：

```text
OPENAI_API_KEY=
AGENT_DB_PATH=.data/agent_runs.sqlite3
AGENT_LOG_LEVEL=INFO
```

默认情况下项目使用离线规则规划器，不需要 `OPENAI_API_KEY`。

## 可继续扩展的方向

- 接入真实知识库：Elasticsearch、Milvus、pgvector 或企业内部文档系统。
- 增加人工审批流：将高风险工具调用进入审批队列。
- 接入 OpenTelemetry：将 trace 上报到 Jaeger、Tempo 或云厂商 APM。
- 增加多租户隔离：按 tenant 维度隔离配置、工具权限和数据。
- 增加评测集：对任务成功率、工具选择准确率和安全拦截率做持续评估。
