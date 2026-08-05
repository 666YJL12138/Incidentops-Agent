const alertsEl = document.querySelector("#alerts");
const timelineEl = document.querySelector("#timeline");
const refreshButton = document.querySelector("#refresh-alerts");
const alertForm = document.querySelector("#alert-form");
const submitAlertStatus = document.querySelector("#submit-alert-status");
const evidenceContentEl = document.querySelector("#evidence-content");
const workspaceTitleEl = document.querySelector("#workspace-title");
const workspaceSubtitleEl = document.querySelector("#workspace-subtitle");
const incidentStatusEl = document.querySelector("#incident-status");

let currentIncidentState = null;

async function api(path, options = {}) {
  const response = await fetch(path, {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
    ...options,
  });

  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`);
  }

  return response.json();
}

function renderAlerts(alerts) {
  alertsEl.innerHTML = "";

  for (const alert of alerts) {
    const card = document.createElement("article");
    card.className = "alert-card";

    const severityClass = alert.severity === "P1" ? "severity-p1" : "severity-p2";

    card.innerHTML = `
      <div class="alert-title">
        <span class="alert-service">${alert.service}</span>
        <span class="severity ${severityClass}">${alert.severity}</span>
      </div>
      <p class="alert-message">${alert.message}</p>
      <button class="start-button" type="button">Start Investigation</button>
    `;

    card.addEventListener("click", () => selectAlert(alert));

    const startButton = card.querySelector(".start-button");
    startButton.addEventListener("click", async (event) => {
      event.stopPropagation();
      await startInvestigation(alert.id);
    });

    alertsEl.appendChild(card);
  }

  renderAlertOverview(alerts);
}

function renderAlertOverview(alerts) {
  const activeCountEl = document.querySelector("#active-incident-count");
  const highestSeverityEl = document.querySelector("#highest-severity");

  activeCountEl.textContent = alerts.length;

  if (alerts.some(alert => alert.severity === "P1")) {
    highestSeverityEl.textContent = "P1";
    return;
  }

  if (alerts.some(alert => alert.severity === "P2")) {
    highestSeverityEl.textContent = "P2";
    return;
  }

  highestSeverityEl.textContent = "-";
}

function selectAlert(alert) {
  workspaceTitleEl.textContent = alert.id;
  workspaceSubtitleEl.textContent = `${alert.service} | ${alert.severity} | ${alert.message}`;
  incidentStatusEl.textContent = "Selected";

  timelineEl.innerHTML = `
    <div class="empty-state">
      Selected ${alert.id}. Click Start Investigation to run the Agent workflow.
    </div>
  `;

  evidenceContentEl.innerHTML = `<pre id="agent-output">${escapeHtml(JSON.stringify(alert, null, 2))}</pre>`;
}

async function startInvestigation(alertId) {
  timelineEl.innerHTML = `
    <div class="empty-state">
      Agent is investigating ${alertId}. Collecting RAG and MCP evidence...
    </div>
  `;
  evidenceContentEl.innerHTML = `<pre id="agent-output">Collecting evidence...</pre>`;
  incidentStatusEl.textContent = "Investigating";

  try {
    const state = await api("/api/incidents/start", {
      method: "POST",
      body: JSON.stringify({
        alert_id: alertId,
      }),
    });

    if (state.error) {
      timelineEl.innerHTML = `
        <div class="empty-state">
          ${state.message || "Failed to start investigation."}
        </div>
      `;
      evidenceContentEl.innerHTML = `<pre id="agent-output">${escapeHtml(JSON.stringify(state, null, 2))}</pre>`;
      incidentStatusEl.textContent = "Error";
      return;
    }

    renderIncident(state);
  } catch (error) {
    timelineEl.innerHTML = `
      <div class="empty-state">
        Failed to start investigation. Please check FastAPI server logs.
      </div>
    `;
    evidenceContentEl.innerHTML = `<pre id="agent-output">${escapeHtml(error.message)}</pre>`;
    incidentStatusEl.textContent = "Error";
  }
}

function renderIncident(state) {
  currentIncidentState = state;

  const timeline = state.timeline || [];
  const hypotheses = state.hypotheses || [];
  const actions = state.recommended_actions || [];

  workspaceTitleEl.textContent = state.incident_id;
  workspaceSubtitleEl.textContent = `${state.alert.service} | ${state.alert.severity} | ${state.alert.message}`;
  incidentStatusEl.textContent = state.status;

  timelineEl.innerHTML = `
    <div class="incident-header">
      <div>
        <h3>${state.incident_id}</h3>
        <p>${state.alert.service} | ${state.alert.severity} | ${state.status}</p>
      </div>
    </div>

    <h3>Timeline</h3>
    <div class="timeline-list">
      ${timeline.map(event => `
        <div class="timeline-item">
          <strong>${event.step}</strong>
          <p>${event.message}</p>
        </div>
      `).join("")}
    </div>

    <h3>Root Cause Hypotheses</h3>
    <div class="card-list">
      ${hypotheses.map(item => `
        <div class="hypothesis-card">
          <strong>${item.title}</strong>
          <p>Confidence: ${Math.round((item.confidence || 0) * 100)}%</p>
          <ul>
            ${(item.evidence || []).map(evidence => `<li>${escapeHtml(evidence)}</li>`).join("")}
          </ul>
        </div>
      `).join("") || `<div class="empty-state">No hypotheses generated.</div>`}
    </div>

    <h3>Recommended Actions</h3>
    <div class="card-list">
      ${actions.map(action => `
        <div class="action-card">
          <div class="action-title">
            <strong>${action.title}</strong>
            <span class="risk risk-${action.risk}">${action.risk}</span>
          </div>
          <p>${action.reason}</p>
          ${
            action.requires_approval
              ? `<button class="approve-button" type="button" onclick="approveAction('${state.incident_id}', '${action.id}')">
                   Approve
                 </button>`
              : `<span class="safe-action">No approval required</span>`
          }
        </div>
      `).join("") || `<div class="empty-state">No actions generated.</div>`}
    </div>
  `;

  renderEvidence("raw");
  setActiveEvidenceTab("raw");
}

function renderEvidence(tab) {
  if (!currentIncidentState) {
    evidenceContentEl.innerHTML = `<pre id="agent-output">No output yet.</pre>`;
    return;
  }

  const evidence = currentIncidentState.evidence || {};

  if (tab === "raw") {
    evidenceContentEl.innerHTML = `<pre id="agent-output">${escapeHtml(JSON.stringify(evidence, null, 2))}</pre>`;
    return;
  }

  if (tab === "knowledge") {
    const docs = evidence.knowledge || [];
    evidenceContentEl.innerHTML = docs.map(doc => `
      <div class="evidence-card">
        <strong>${escapeHtml(doc.title || "Untitled Document")}</strong>
        <p>${escapeHtml(doc.source || "")}</p>
        <small>Score: ${doc.score ?? "-"}</small>
        <pre>${escapeHtml(doc.preview || "")}</pre>
      </div>
    `).join("") || `<div class="empty-state">No RAG evidence.</div>`;
    return;
  }

  if (tab === "logs") {
    const logs = evidence.logs || [];
    evidenceContentEl.innerHTML = logs.map(item => `
      <div class="log-line">${escapeHtml(item.line || "")}</div>
    `).join("") || `<div class="empty-state">No log evidence.</div>`;
    return;
  }

  if (tab === "metrics") {
    const metrics = evidence.metrics || {};
    const summary = metrics.summary || {};
    const points = metrics.points || [];

    evidenceContentEl.innerHTML = `
      <div class="metric-summary">
        <div><span>Max Error Rate</span><strong>${summary.max_error_rate ?? "-"}%</strong></div>
        <div><span>Max p95 Latency</span><strong>${summary.max_p95_latency ?? "-"}ms</strong></div>
        <div><span>Max CPU</span><strong>${summary.max_cpu ?? "-"}%</strong></div>
        <div><span>Max Memory</span><strong>${summary.max_memory ?? "-"}%</strong></div>
      </div>
      <div class="chart-block">
        <h3>Error Rate</h3>
        ${renderSparkline(points.map(point => point.error_rate || 0))}
      </div>
      <div class="chart-block">
        <h3>p95 Latency</h3>
        ${renderSparkline(points.map(point => point.p95_latency || 0))}
      </div>
    `;
    return;
  }

  if (tab === "deployments") {
    const deployments = evidence.deployments || [];
    evidenceContentEl.innerHTML = deployments.map(item => `
      <div class="evidence-card">
        <strong>${escapeHtml(`${item.service} ${item.version}`)}</strong>
        <p>${escapeHtml(item.time || "")}</p>
        <p>${escapeHtml(item.summary || "")}</p>
        <small>commit: ${escapeHtml(item.commit || "-")}</small>
      </div>
    `).join("") || `<div class="empty-state">No deployment evidence.</div>`;
    return;
  }

  if (tab === "postmortem") {
    renderPostmortem();
  }
}

function renderPostmortem() {
  const postmortem = currentIncidentState.postmortem || {};

  evidenceContentEl.innerHTML = `
    <div class="postmortem-preview">
      <h3>Summary</h3>
      <p>${escapeHtml(postmortem.summary || "-")}</p>

      <h3>Impact</h3>
      <p>${escapeHtml(postmortem.impact || "-")}</p>

      <h3>Root Cause Hypotheses</h3>
      <ul>
        ${(postmortem.hypotheses || []).map(item => `<li>${escapeHtml(item.title || item)}</li>`).join("")}
      </ul>

      <h3>Follow-up Actions</h3>
      <ul>
        ${(postmortem.follow_up_actions || []).map(item => `<li>${escapeHtml(item)}</li>`).join("")}
      </ul>
    </div>
  `;
}

function renderSparkline(values) {
  if (!values.length) {
    return `<div class="empty-state">No metric points.</div>`;
  }

  const width = 260;
  const height = 80;
  const max = Math.max(...values, 1);
  const points = values.map((value, index) => {
    const x = values.length === 1 ? 0 : (index / (values.length - 1)) * width;
    const y = height - (value / max) * (height - 12) - 6;
    return `${x},${y}`;
  }).join(" ");

  return `
    <svg class="sparkline" viewBox="0 0 ${width} ${height}" role="img">
      <polyline points="${points}" fill="none" stroke="#1f6f78" stroke-width="3" />
    </svg>
  `;
}

function setActiveEvidenceTab(tab) {
  document.querySelectorAll(".tab-button").forEach(button => {
    button.classList.toggle("active", button.dataset.tab === tab);
  });
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

async function approveAction(incidentId, actionId) {
  evidenceContentEl.innerHTML = `<pre id="agent-output">Approving ${escapeHtml(actionId)}...</pre>`;

  try {
    const result = await api(`/api/incidents/${incidentId}/approve`, {
      method: "POST",
      body: JSON.stringify({
        action_id: actionId,
      }),
    });

    evidenceContentEl.innerHTML = `<pre id="agent-output">${escapeHtml(JSON.stringify(result, null, 2))}</pre>`;
    incidentStatusEl.textContent = result.status || "approved";
  } catch (error) {
    evidenceContentEl.innerHTML = `<pre id="agent-output">${escapeHtml(error.message)}</pre>`;
  }
}

async function loadAlerts() {
  alertsEl.innerHTML = `<div class="empty-state">Loading alerts...</div>`;

  try {
    const alerts = await api("/api/alerts");
    renderAlerts(alerts);
  } catch (error) {
    alertsEl.innerHTML = `
      <div class="empty-state">
        Failed to load alerts. Please check FastAPI server.
      </div>
    `;
    evidenceContentEl.innerHTML = `<pre id="agent-output">${escapeHtml(error.message)}</pre>`;
  }
}

alertForm.addEventListener("submit", async (event) => {
  event.preventDefault();

  const service = document.querySelector("#custom-service").value.trim();
  const severity = document.querySelector("#custom-severity").value;
  const message = document.querySelector("#custom-message").value.trim();

  submitAlertStatus.textContent = "Agent is investigating...";

  try {
    const state = await api("/api/incidents/start-from-alert", {
      method: "POST",
      body: JSON.stringify({
        service,
        severity,
        message,
        status: "open",
      }),
    });

    renderIncident(state);
    submitAlertStatus.textContent =
      `Investigation completed: ${state.incident_id}`;
  } catch (error) {
    submitAlertStatus.textContent =
      `Failed to analyze alert: ${error.message}`;
  }
});
document.querySelectorAll(".tab-button").forEach(button => {
  button.addEventListener("click", () => {
    setActiveEvidenceTab(button.dataset.tab);
    renderEvidence(button.dataset.tab);
  });
});

refreshButton.addEventListener("click", loadAlerts);

loadAlerts();