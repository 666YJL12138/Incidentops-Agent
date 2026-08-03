const alertsEl = document.querySelector("#alerts");
const timelineEl = document.querySelector("#timeline");
const outputEl = document.querySelector("#agent-output");
const refreshButton = document.querySelector("#refresh-alerts");

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
}

function selectAlert(alert) {
  timelineEl.innerHTML = `
    <div class="empty-state">
      Selected ${alert.id}. Click Start Investigation to run the Agent workflow.
    </div>
  `;

  outputEl.textContent = JSON.stringify(alert, null, 2);
}

async function startInvestigation(alertId) {
  timelineEl.innerHTML = `
    <div class="empty-state">
      Agent is investigating ${alertId}. Collecting RAG and MCP evidence...
    </div>
  `;
  outputEl.textContent = "Collecting evidence...";

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
      outputEl.textContent = JSON.stringify(state, null, 2);
      return;
    }

    renderIncident(state);
  } catch (error) {
    timelineEl.innerHTML = `
      <div class="empty-state">
        Failed to start investigation. Please check FastAPI server logs.
      </div>
    `;
    outputEl.textContent = error.message;
  }
}

function renderIncident(state) {
  const timeline = state.timeline || [];
  const hypotheses = state.hypotheses || [];
  const actions = state.recommended_actions || [];

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
            ${(item.evidence || []).map(evidence => `<li>${evidence}</li>`).join("")}
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

  outputEl.textContent = JSON.stringify(state.evidence || {}, null, 2);
}

async function approveAction(incidentId, actionId) {
  outputEl.textContent = `Approving ${actionId}...`;

  try {
    const result = await api(`/api/incidents/${incidentId}/approve`, {
      method: "POST",
      body: JSON.stringify({
        action_id: actionId,
      }),
    });

    outputEl.textContent = JSON.stringify(result, null, 2);
  } catch (error) {
    outputEl.textContent = error.message;
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
    outputEl.textContent = error.message;
  }
}

refreshButton.addEventListener("click", loadAlerts);

loadAlerts();
