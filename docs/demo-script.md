# IncidentOps Agent 演示脚本

## 1. 项目背景

这个项目解决的是 SRE 在生产事故中需要同时查询告警、日志、指标、部署记录、Runbook 和历史复盘的问题。

传统方式下，值班工程师需要在多个系统之间切换，手动拼接证据链。IncidentOps Agent 把这个流程做成一个可观察、可审批、可复盘的 Agent 工作流。

## 2. 技术架构

项目由四层组成：

- FastAPI 后端：提供告警、事故调查、工具调用和审批接口。
- RAG 知识库：检索 Runbook 和历史事故复盘。
- MCP 工具层：封装日志、指标、部署记录和工单能力。
- Skill + Agent 状态机：按 SRE 标准流程完成调查，并把结果写入 IncidentState。

## 3. 演示流程

1. 打开 `http://127.0.0.1:8000`。
2. 选择 `checkout-api` P1 告警。
3. 点击 `Start Investigation`。
4. 展示 Agent 调查 Timeline：
   - `load_skills`
   - `triage`
   - `rag_search`
   - `metrics`
   - `logs`
   - `deployments`
   - `hypotheses`
   - `actions`
   - `postmortem`
5. 切换 `RAG` 标签，展示命中的 Runbook 和历史复盘。
6. 切换 `Logs` 标签，展示 timeout 日志证据。
7. 切换 `Metrics` 标签，展示错误率和 p95 延迟趋势。
8. 切换 `Deploy` 标签，展示最近部署记录。
9. 展示 Root Cause Hypotheses 和 Recommended Actions。
10. 对高风险动作点击 `Approve`，展示人工审批结果。
11. 切换 `Postmortem` 标签，展示复盘草稿。

## 4. 推荐口播

这个项目不是普通问答助手，而是一个面向真实生产事故流程的 Agent 系统。它从告警开始，先通过 Skill 固化调查流程，再用 RAG 检索历史经验，用 MCP 工具查询现场证据，最终生成根因假设、处置建议和复盘草稿。

我特别强调了两个工程点：第一，Agent 的每一步都会写入 timeline，方便观察和审计；第二，回滚等高风险操作必须经过人工审批，避免 Agent 自动执行危险生产动作。

## 5. 面试追问准备

### 为什么使用 MCP？

MCP 把日志、指标、部署、工单封装成标准工具接口。现在底层是本地文件，未来可以替换成 Elasticsearch、Prometheus、Jenkins、Jira，而 Agent 主流程不需要大改。

### Skill 和 Prompt 有什么区别？

Prompt 更像一次性的模型指令，Skill 更像可复用的领域操作手册。这个项目用 Skill 固化 SRE 告警分诊、根因调查、安全处置和复盘写作流程。

### RAG 怎么评估？

我准备了 `data/eval_queries.json`，用 `rag/eval_retrieval.py` 计算 Hit@1、Hit@3、Hit@5，评估 query 是否能命中预期 Runbook 或 Postmortem。

### 如何避免危险操作？

项目把动作分成 low risk 和 high risk。创建工单、通知负责人属于低风险；回滚、生产配置修改、数据库操作属于高风险。高风险动作只记录审批结果，不会自动执行生产操作。

### 当前版本是否使用大模型？

当前根因假设使用可解释规则生成，保证离线演示稳定。系统已经把 evidence、skills 和 IncidentState 组织好，后续可以在 `build_hypotheses` 节点接入 LLM，同时保留规则模式作为降级方案。
