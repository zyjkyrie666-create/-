# Campus Study Agent

一个适合大学生使用和展示的 AI Agent 网页项目。

项目目标是帮助学生把课程、作业、考试和 DDL 拆解成可执行的学习计划。当前版本是一个可本地运行的 MVP：不依赖真实大模型，默认使用离线规则 Agent，方便演示、测试和后续接入 OpenAI 或其他模型。

## 核心功能

- 网页输入学习任务。
- 自动识别课程、作业、考试、DDL 等信息。
- 生成任务拆解和每日学习安排。
- 根据时间压力给出 DDL 风险提醒。
- 保留 Agent 编排、工具调用、策略校验、审计记录和 trace 结构。

## 快速开始

在项目根目录执行：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[api,dev]"
uvicorn industrial_agent.api.main:app --reload --host 127.0.0.1 --port 8000
```

然后打开：

```text
http://127.0.0.1:8000
```

## 测试

如果只想验证核心逻辑，可以执行：

```powershell
$env:PYTHONPATH = "src"
python -m unittest discover -s tests
```

## API 示例

```powershell
curl -X POST http://127.0.0.1:8000/api/v1/runs `
  -H "Content-Type: application/json" `
  -d '{"user_id":"student-001","role":"operator","query":"我下周五要交机器学习作业，这周还有高数考试，帮我安排一下。"}'
```

## 目录结构

```text
src/industrial_agent/
  agent/              # Agent 编排和运行流程
  api/                # FastAPI 接口和网页版首页
  domain/             # 领域模型、工具注册、策略规则
  infrastructure/     # SQLite 持久化和审计
  llm/                # 规划器适配层
  observability/      # trace/span 记录
tests/                # unittest 测试
docs/                 # 项目文档
```

## 环境变量

可以复制 `.env.example` 后按需配置：

```text
OPENAI_API_KEY=
AGENT_DB_PATH=.data/agent_runs.sqlite3
AGENT_LOG_LEVEL=INFO
```

默认情况下项目使用离线规则 Agent，不需要配置 `OPENAI_API_KEY`。
