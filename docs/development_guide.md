# 从 0 到 1 制作思路

这份文档用于解释本项目是怎么从一个想法逐步做成可运行工程的，以及每个 `.py` 文件适合按什么顺序理解和编写。

## 1. 项目一开始要解决什么问题

本项目不是做一个普通聊天机器人，而是做一个更接近企业真实场景的 AI Agent 平台骨架。

核心问题是：

1. 用户输入一个任务后，Agent 要能规划步骤。
2. Agent 不能随便执行危险动作，要先经过策略检查。
3. Agent 调用工具后，要记录执行过程、审计日志和最终结果。
4. 项目既能通过命令行运行，也能通过 API 调用。
5. 没有真实大模型 Key 时，也能本地演示和测试。

所以项目从一开始就按“可运行、可治理、可扩展、可验证”的思路来拆分。

## 2. 从 0 到 1 的制作顺序

### 第一步：先定义数据结构

先写 `domain/models.py`。

原因是后面的 API、Agent 编排、工具调用、策略检查都要围绕同一批数据结构工作。比如用户请求是什么、角色有哪些、一次运行有哪些状态、工具计划长什么样，都应该先统一。

如果不先定义模型，后面每个模块都会自己造字段，项目很快会变乱。

### 第二步：定义工具系统

再写 `domain/tools.py`。

Agent 真正能做事，靠的是工具。这个文件定义了：

1. 工具叫什么。
2. 工具有多大风险。
3. 哪些角色可以调用。
4. 工具执行时调用哪个函数。
5. 默认内置哪些演示工具。

这样后面 Agent 只需要通过 `ToolRegistry` 找工具和执行工具，不需要关心每个工具内部怎么实现。

### 第三步：定义策略检查

再写 `domain/policy.py`。

企业级 Agent 不能只考虑“能不能完成任务”，还要考虑“该不该执行”。所以在工具真正执行前，需要检查：

1. 用户请求是否为空。
2. 是否包含危险指令。
3. 当前角色是否有权限调用工具。
4. 高风险工具是否只允许管理员使用。

这一层的作用是防止 Agent 越权、误操作或执行危险命令。

### 第四步：定义 LLM / Planner 接口

再写 `llm/base.py`。

这里不直接绑定某个大模型，而是先定义一个 `Planner` 协议。只要一个类能实现：

1. `plan()`：根据用户请求生成工具调用计划。
2. `summarize()`：根据工具结果生成最终回答。

它就可以被 Agent 编排器使用。

这样做的好处是：今天可以用本地规则规划器，明天也可以替换成 OpenAI、Azure OpenAI、私有大模型或企业网关。

### 第五步：实现离线规则规划器

再写 `llm/rule_based.py`。

这个文件是为了保证项目没有 API Key 也能跑。它用简单规则判断用户输入：

1. 默认先调用 `knowledge_search`。
2. 如果输入里有 ticket 或工单，就调用 `ticket_lookup`。
3. 如果输入里有风险、告警、incident、故障等关键词，就调用 `risk_assessment`。
4. 如果输入里有 override 或绕过，就尝试调用高风险工具 `change_freeze_override`。

它不是为了代替真实大模型，而是为了让项目可以稳定演示、稳定测试。

### 第六步：预留真实模型适配层

再写 `llm/openai_adapter.py`。

这个文件当前是一个轻量占位适配器，主要表达项目的扩展位置：以后接入真实 OpenAI 或企业模型服务时，应该改这里，而不是去改 Agent 主流程。

当前它内部仍然回退到 `RuleBasedPlanner`，这样项目不会因为没有模型 Key 而无法运行。

### 第七步：实现审计、持久化和追踪

再写这些基础设施文件：

1. `infrastructure/audit.py`
2. `infrastructure/repository.py`
3. `observability/tracing.py`

它们分别负责：

1. 记录审计事件。
2. 用 SQLite 保存每次 Agent 运行结果。
3. 记录每个关键步骤的耗时和状态。

这些能力让项目不只是“能回答”，还可以被回放、排查和审计。

### 第八步：实现 Agent 编排器

再写 `agent/orchestrator.py`。

这是项目最核心的文件。它把前面的模块串起来：

1. 接收 `TaskRequest`。
2. 先做请求级策略检查。
3. 调用 Planner 生成工具计划。
4. 对每个工具计划做权限和风险检查。
5. 执行允许的工具。
6. 记录审计事件和 trace。
7. 调用 Planner 汇总最终回答。
8. 保存整次运行结果。

也就是说，前面的文件都是零件，这个文件负责把零件装成完整工作流。

### 第九步：写应用装配入口

再写 `app_factory.py` 和 `config.py`。

`config.py` 负责从环境变量读取配置，比如数据库路径、日志等级、是否启用 OpenAI。

`app_factory.py` 负责把工具注册表、策略引擎、审计、仓储、Planner 和 Agent 编排器组装起来。

这样 CLI 和 API 都可以复用同一个 `build_orchestrator()`，避免两边各写一套初始化逻辑。

### 第十步：提供 CLI 和 API

最后写：

1. `cli.py`
2. `api/schemas.py`
3. `api/main.py`

`cli.py` 让项目可以通过命令行快速运行，适合本地演示。

`api/schemas.py` 定义 HTTP 请求和响应格式，避免接口参数混乱。

`api/main.py` 提供 FastAPI 接口，让前端、其他系统或接口测试工具可以调用这个 Agent。

### 第十一步：补测试

最后写 `tests/` 下的测试文件。

当前测试重点覆盖两类核心风险：

1. 正常工单和告警任务能跑通。
2. 危险指令和越权高风险工具会被拦截。

这能证明项目不是只有页面或接口，而是核心业务链路真的可以运行。

## 3. `.py` 文件建议阅读和制作顺序

下面是建议顺序。按这个顺序看，最容易理解整个项目。

| 顺序 | 文件 | 作用 |
| --- | --- | --- |
| 1 | `src/industrial_agent/domain/models.py` | 定义角色、风险等级、运行状态、用户请求、工具计划、运行步骤和运行结果。 |
| 2 | `src/industrial_agent/domain/tools.py` | 定义工具对象、工具注册表和默认演示工具。 |
| 3 | `src/industrial_agent/domain/policy.py` | 定义策略引擎，负责请求拦截、工具权限检查和高风险工具控制。 |
| 4 | `src/industrial_agent/llm/base.py` | 定义 Planner 接口，让 Agent 不绑定具体大模型。 |
| 5 | `src/industrial_agent/llm/rule_based.py` | 实现离线规则规划器，保证没有 API Key 也能演示和测试。 |
| 6 | `src/industrial_agent/llm/openai_adapter.py` | 预留真实大模型接入位置，目前回退到规则规划器。 |
| 7 | `src/industrial_agent/infrastructure/audit.py` | 记录审计事件，比如运行开始、工具完成、工具被拦截、运行结束。 |
| 8 | `src/industrial_agent/infrastructure/repository.py` | 用 SQLite 保存 Agent 运行结果，方便后续查询和回放。 |
| 9 | `src/industrial_agent/observability/tracing.py` | 记录规划、工具执行、结果汇总等步骤的耗时和状态。 |
| 10 | `src/industrial_agent/agent/orchestrator.py` | Agent 主流程，负责把策略、规划、工具、审计、存储和追踪串起来。 |
| 11 | `src/industrial_agent/config.py` | 从环境变量读取项目配置。 |
| 12 | `src/industrial_agent/app_factory.py` | 统一组装项目依赖，创建可运行的 Agent 编排器。 |
| 13 | `src/industrial_agent/cli.py` | 命令行入口，用于本地快速运行 Agent。 |
| 14 | `src/industrial_agent/api/schemas.py` | 定义 API 请求和响应数据结构。 |
| 15 | `src/industrial_agent/api/main.py` | FastAPI 服务入口，对外提供 HTTP 接口。 |
| 16 | `src/industrial_agent/__init__.py` | 包初始化文件，声明项目版本。 |

## 4. 一次请求的执行流程

以命令行为例：

```powershell
python -m industrial_agent.cli "查询 TICKET-1001 并评估生产告警风险"
```

执行流程是：

1. `cli.py` 读取命令行参数。
2. `app_factory.py` 创建 Agent 编排器。
3. `config.py` 读取环境变量配置。
4. `domain/tools.py` 注册默认工具。
5. `domain/policy.py` 创建策略引擎。
6. `llm/rule_based.py` 根据输入生成工具计划。
7. `agent/orchestrator.py` 先检查请求是否合法。
8. `agent/orchestrator.py` 再逐个检查工具调用是否允许。
9. `ToolRegistry` 执行对应工具。
10. `audit.py` 记录审计事件。
11. `tracing.py` 记录步骤耗时。
12. `repository.py` 保存本次运行结果。
13. `rule_based.py` 汇总最终回答。
14. `cli.py` 把最终回答打印到终端。

## 5. 每个核心模块的简单理解

### domain

`domain` 是项目的业务核心。它不关心 FastAPI、SQLite 或 OpenAI SDK，只定义项目最重要的业务概念：请求、角色、工具、策略。

### llm

`llm` 是规划层。它决定“为了完成用户任务，应该调用哪些工具”。当前默认用规则规划器，后续可以替换成真实大模型。

### agent

`agent` 是编排层。它负责控制一次完整运行的顺序，是整个项目最关键的主流程。

### infrastructure

`infrastructure` 是基础设施层。它负责审计、数据库存储等偏工程化的能力。

### observability

`observability` 是可观测性层。它记录每个关键步骤的状态和耗时，方便后续排查问题。

### api

`api` 是 HTTP 接口层。它只负责接收请求、调用 Agent、返回结果，不把核心业务逻辑写在接口里。

## 6. 为什么项目要这样拆

这样拆的主要原因是降低耦合。

如果把所有逻辑都写进一个文件，短期看起来快，但后续会很难维护。现在的拆分方式有几个好处：

1. 要改工具，只改 `domain/tools.py`。
2. 要改安全策略，只改 `domain/policy.py`。
3. 要接真实大模型，优先改 `llm/openai_adapter.py`。
4. 要换数据库，优先改 `infrastructure/repository.py`。
5. 要增加接口，优先改 `api/main.py` 和 `api/schemas.py`。
6. Agent 主流程仍然保持稳定，不容易被改乱。

## 7. 如何验证项目是否跑通

在项目根目录执行：

```powershell
$env:PYTHONPATH = "src"
python -m unittest discover -s tests
```

预期结果是测试全部通过。

也可以运行命令行演示：

```powershell
$env:PYTHONPATH = "src"
python -m industrial_agent.cli "查询 TICKET-1001 并评估生产告警风险"
```

预期结果是终端输出包含工单信息、风险等级和审计记录说明。

如果要启动 API：

```powershell
uvicorn industrial_agent.api.main:app --reload --host 0.0.0.0 --port 8000
```

然后访问：

```text
http://localhost:8000/health
```

预期返回：

```json
{"status":"ok"}
```

## 8. 后续扩展应该从哪里开始

如果后续继续完善，建议按这个顺序来，不要一次性大改：

1. 先补真实知识库检索工具。
2. 再接入真实大模型 Planner。
3. 再把审计日志从内存改成数据库持久化。
4. 再增加人工审批流。
5. 最后再考虑多租户、监控平台和部署流水线。

这样可以保证每一步都能运行、能验证、能回退。
