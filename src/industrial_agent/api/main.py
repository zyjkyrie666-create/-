from __future__ import annotations

from dataclasses import asdict

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse

from industrial_agent.api.schemas import RunRequest, RunResponse
from industrial_agent.app_factory import build_orchestrator
from industrial_agent.domain.models import TaskRequest

app = FastAPI(
    title="Campus Study Agent",
    version="0.1.0",
    description="A web AI Agent demo for college study planning and deadline management.",
)
orchestrator = build_orchestrator()


@app.get("/", response_class=HTMLResponse)
def index() -> str:
    return """
<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Campus Study Agent</title>
  <style>
    :root {
      color-scheme: light;
      --bg: #f6f7fb;
      --panel: #ffffff;
      --text: #172033;
      --muted: #667085;
      --line: #d9deea;
      --primary: #2563eb;
      --primary-dark: #1d4ed8;
      --soft: #eef4ff;
      --ok: #12805c;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      min-height: 100vh;
      background: var(--bg);
      color: var(--text);
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Microsoft YaHei", sans-serif;
    }
    .shell {
      width: min(1120px, calc(100% - 32px));
      margin: 0 auto;
      padding: 28px 0;
    }
    header {
      display: flex;
      justify-content: space-between;
      gap: 18px;
      align-items: flex-end;
      margin-bottom: 18px;
    }
    h1 {
      margin: 0;
      font-size: 30px;
      line-height: 1.2;
    }
    .subtitle {
      margin: 8px 0 0;
      color: var(--muted);
      font-size: 15px;
    }
    .status {
      padding: 8px 12px;
      border: 1px solid #b7e1cd;
      background: #ecfdf5;
      color: var(--ok);
      border-radius: 8px;
      font-size: 14px;
      white-space: nowrap;
    }
    main {
      display: grid;
      grid-template-columns: minmax(0, 0.95fr) minmax(0, 1.05fr);
      gap: 18px;
      align-items: start;
    }
    section {
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 18px;
    }
    h2 {
      margin: 0 0 14px;
      font-size: 18px;
    }
    label {
      display: block;
      margin: 14px 0 7px;
      color: #344054;
      font-size: 14px;
      font-weight: 600;
    }
    textarea, input, select {
      width: 100%;
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 11px 12px;
      color: var(--text);
      background: #fff;
      font: inherit;
      outline: none;
    }
    textarea {
      min-height: 178px;
      resize: vertical;
      line-height: 1.6;
    }
    textarea:focus, input:focus, select:focus {
      border-color: var(--primary);
      box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.12);
    }
    .row {
      display: grid;
      grid-template-columns: 1fr 160px;
      gap: 12px;
    }
    .actions {
      display: flex;
      gap: 10px;
      align-items: center;
      margin-top: 16px;
    }
    button {
      border: 0;
      border-radius: 8px;
      padding: 11px 16px;
      color: #fff;
      background: var(--primary);
      font: inherit;
      font-weight: 700;
      cursor: pointer;
    }
    button:hover { background: var(--primary-dark); }
    button:disabled { opacity: 0.65; cursor: wait; }
    .hint {
      margin: 0;
      color: var(--muted);
      font-size: 14px;
    }
    .examples {
      display: grid;
      gap: 8px;
      margin-top: 14px;
    }
    .example {
      border: 1px solid var(--line);
      background: var(--soft);
      color: #1f3b73;
      border-radius: 8px;
      padding: 10px 12px;
      text-align: left;
      font-weight: 600;
    }
    .result {
      min-height: 420px;
      white-space: pre-wrap;
      overflow-wrap: anywhere;
      line-height: 1.7;
      font-size: 15px;
      color: #1d2939;
      background: #fbfcff;
    }
    .meta {
      display: grid;
      gap: 8px;
      margin-top: 14px;
    }
    .pill {
      display: inline-flex;
      width: fit-content;
      padding: 5px 9px;
      border-radius: 999px;
      background: #f2f4f7;
      color: #475467;
      font-size: 13px;
    }
    .steps {
      margin: 12px 0 0;
      padding: 0;
      list-style: none;
      display: grid;
      gap: 8px;
    }
    .steps li {
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 9px 10px;
      color: #344054;
      background: #fff;
      font-size: 14px;
    }
    @media (max-width: 860px) {
      header { display: block; }
      .status { display: inline-block; margin-top: 12px; }
      main { grid-template-columns: 1fr; }
      .row { grid-template-columns: 1fr; }
    }
  </style>
</head>
<body>
  <div class="shell">
    <header>
      <div>
        <h1>Campus Study Agent</h1>
        <p class="subtitle">大学生学习任务规划助手</p>
      </div>
      <div class="status">本地离线规则 Agent</div>
    </header>

    <main>
      <section>
        <h2>学习需求</h2>
        <form id="agent-form">
          <label for="query">输入任务</label>
          <textarea id="query" required>我下周五要交机器学习作业，这周还有高数考试，帮我安排一下。</textarea>

          <div class="row">
            <div>
              <label for="user_id">用户 ID</label>
              <input id="user_id" value="student-001" />
            </div>
            <div>
              <label for="role">角色</label>
              <select id="role">
                <option value="operator" selected>student</option>
                <option value="viewer">viewer</option>
                <option value="admin">admin</option>
              </select>
            </div>
          </div>

          <div class="actions">
            <button id="submit-btn" type="submit">生成计划</button>
            <p id="message" class="hint"></p>
          </div>
        </form>

        <div class="examples">
          <button class="example" type="button">明天英语考试，但我还没复习，今天该怎么安排？</button>
          <button class="example" type="button">数据库课程项目两周后答辩，帮我拆成每日任务。</button>
          <button class="example" type="button">我有 Python 作业和高数小测，先做哪个？</button>
        </div>
      </section>

      <section>
        <h2>Agent 输出</h2>
        <div id="answer" class="result">提交后这里会显示学习计划。</div>
        <div class="meta">
          <span id="run-id" class="pill">run_id: -</span>
          <span id="status" class="pill">status: idle</span>
        </div>
        <ul id="steps" class="steps"></ul>
      </section>
    </main>
  </div>

  <script>
    const form = document.querySelector("#agent-form");
    const query = document.querySelector("#query");
    const userId = document.querySelector("#user_id");
    const role = document.querySelector("#role");
    const answer = document.querySelector("#answer");
    const statusEl = document.querySelector("#status");
    const runIdEl = document.querySelector("#run-id");
    const stepsEl = document.querySelector("#steps");
    const message = document.querySelector("#message");
    const submitBtn = document.querySelector("#submit-btn");

    document.querySelectorAll(".example").forEach((button) => {
      button.addEventListener("click", () => {
        query.value = button.textContent.trim();
        query.focus();
      });
    });

    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      submitBtn.disabled = true;
      message.textContent = "生成中...";
      statusEl.textContent = "status: running";
      stepsEl.innerHTML = "";

      try {
        const response = await fetch("/api/v1/runs", {
          method: "POST",
          headers: {"Content-Type": "application/json"},
          body: JSON.stringify({
            query: query.value,
            user_id: userId.value || "anonymous",
            role: role.value,
            context: {},
            metadata: {source: "web"}
          })
        });

        const data = await response.json();
        if (!response.ok) {
          throw new Error(data.detail || "请求失败");
        }

        answer.textContent = data.answer || "没有生成结果。";
        runIdEl.textContent = `run_id: ${data.run_id}`;
        statusEl.textContent = `status: ${data.status}`;
        stepsEl.innerHTML = data.steps.map((step) => {
          const status = step.error ? `${step.status}：${step.error}` : step.status;
          return `<li>${step.name} | ${status}</li>`;
        }).join("");
        message.textContent = "已完成";
      } catch (error) {
        answer.textContent = `出错了：${error.message}`;
        statusEl.textContent = "status: failed";
        message.textContent = "请查看错误信息";
      } finally {
        submitBtn.disabled = false;
      }
    });
  </script>
</body>
</html>
"""


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/api/v1/runs", response_model=RunResponse)
def create_run(payload: RunRequest) -> RunResponse:
    run = orchestrator.run(
        TaskRequest(
            query=payload.query,
            user_id=payload.user_id,
            role=payload.role,
            context=payload.context,
            metadata=payload.metadata,
        )
    )
    return RunResponse(
        run_id=run.id,
        status=run.status.value,
        answer=run.answer,
        policy_decisions=run.policy_decisions,
        steps=[asdict(step) for step in run.steps],
    )


@app.get("/api/v1/runs/{run_id}")
def get_run(run_id: str) -> dict:
    if orchestrator.repository is None:
        raise HTTPException(status_code=404, detail="repository is disabled")
    payload = orchestrator.repository.get_payload(run_id)
    if payload is None:
        raise HTTPException(status_code=404, detail="run not found")
    return payload


@app.get("/api/v1/audit-events")
def list_audit_events() -> list[dict]:
    return orchestrator.audit_sink.export()


@app.get("/api/v1/traces")
def list_traces() -> list[dict]:
    return [asdict(span) for span in orchestrator.trace_recorder.spans]
