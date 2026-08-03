# IncidentOps Agent

IncidentOps Agent 是一个面向 SRE / 运维场景的 AI Agent 项目。

它从一条生产告警开始，自动检索 Runbook 和历史事故复盘，调用 MCP 工具查询日志、指标、部署记录，并生成根因假设、安全处置建议、事故工单和复盘报告。

## 项目背景

很多 AI Agent 项目只是简单的聊天机器人，缺少真实生产场景。

IncidentOps Agent 关注的是一个更贴近企业实际工作的流程：

- 告警分诊
- 基于工具的事故排查
- 基于 RAG 的 Runbook / 历史事故检索
- 基于 MCP 的外部系统工具调用
- 基于 Skill 的标准化运维流程
- 高风险操作前的人类审批
- 事故复盘报告自动生成
- HTML War Room 可视化展示界面

## 技术栈

- Python
- FastAPI
- Pydantic
- Uvicorn
- HTML
- CSS
- JavaScript
- RAG
- MCP
- Skill

## 项目结构

```text
incidentops-agent/
  apps/
    api/
      main.py
    web/
      index.html
      styles.css
      app.js
  agent/
  mcp_servers/
    logs_server.py
    metrics_server.py
    deploy_server.py
    ticket_server.py
    tool_logic.py
  rag/
  skills/
  data/
    logs/
    metrics/
    runbooks/
    postmortems/
  scripts/
    demo_mcp_tools.py
  tests/
  docs/
  README.md
  requirements.txt
```

## Day 1 已完成功能

- 初始化项目目录结构
- 初始化 Git 仓库
- 创建 FastAPI 后端服务
- 添加健康检查接口
- 添加模拟告警列表接口
- 添加静态 HTML 展示页面
- 在浏览器中渲染告警卡片
- 点击告警后展示告警详情 JSON


## Day 2 已完成功能

- 创建 Runbook 知识文档
- 创建历史事故复盘文档
- 实现本地 RAG 文档索引
- 实现关键词检索逻辑
- 新增 `/api/rag/search` 检索接口


## Day 3 已完成功能

- 准备模拟生产日志数据
- 准备模拟服务指标数据
- 准备模拟部署记录
- 实现日志 MCP 工具
- 实现指标 MCP 工具
- 实现部署 MCP 工具
- 实现工单 MCP 工具
- 新增工具验证脚本 `scripts/demo_mcp_tools.py`
- 新增工具验证 API


## Day 6 已完成功能

- 将基础页面升级为 IncidentOps War Room
- 增加告警和服务概览
- 增加事故调查状态栏
- 增加 RAG、日志、指标、部署和复盘证据标签
- 增加错误率和 p95 延迟趋势图
- 支持查看 Agent 调查时间线
- 支持查看根因假设和处置建议
- 保留高风险动作人工审批机制


## 快速启动

创建虚拟环境：

```powershell
python -m venv .venv
```

激活虚拟环境：

```powershell
.\.venv\Scripts\activate
```

安装依赖：

```powershell
pip install -r requirements.txt
```

启动开发服务：

```powershell
python -m uvicorn apps.api.main:app --reload
```

打开首页：

```text
http://127.0.0.1:8000
```

打开接口文档：

```text
http://127.0.0.1:8000/docs
```

## 当前 API 接口

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| GET | `/api/health` | 健康检查接口 |
| GET | `/api/alerts` | 获取模拟生产告警列表 |
| GET | `/api/alerts/{alert_id}` | 获取单条告警详情 |
| GET | `/api/rag/search?query=...` | 检索 Runbook 和历史事故复盘 |
| GET | `/api/tools/logs?service=...&keyword=...` | 查询服务日志 |
| GET | `/api/tools/metrics?service=...` | 查询服务指标 |
| GET | `/api/tools/deployments?service=...` | 查询服务部署记录 |
| POST | `/api/tools/tickets` | 创建事故工单 |

## 当前演示效果

启动服务后，浏览器打开首页，可以看到一个基础版 Incident War Room 页面。

页面目前包含三块区域：

- 左侧：生产告警列表
- 中间：事故调查时间线占位区
- 右侧：Agent 输出区

点击左侧告警卡片后，右侧会展示该告警的 JSON 数据。

## 后续计划

- Day 2：构建 RAG 知识库，引入 Runbook 和历史事故复盘
- Day 3：实现 MCP 工具服务，包括日志、指标、部署记录和工单
- Day 4：实现 Skill 驱动的 Agent 状态机
- Day 5：加入事故状态、事件流和人工审批机制
- Day 6：打磨 HTML War Room 展示界面
- Day 7：补充测试、评估脚本、README 截图和最终演示脚本

## 项目亮点

这个项目不是普通问答助手，而是一个面向真实生产流程的 Agent 系统。

它的核心特点是：

- Agent 会按照事故处理流程逐步执行任务
- RAG 用来检索运维经验，而不是简单聊天
- MCP 用来封装日志、指标、部署、工单等外部工具
- Skill 用来沉淀稳定的 SRE 操作流程
- 高风险处置动作需要人工确认
- 前端页面可以直观展示 Agent 的调查过程
