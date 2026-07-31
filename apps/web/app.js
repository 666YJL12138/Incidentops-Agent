const alertsEl = document.querySelector("#alerts");
const timelineEl = document.querySelector("#timeline");
const outputEl = document.querySelector("#agent-output");
const refreshButton = document.querySelector("#refresh-alerts");

async function api(path) {
  const response = await fetch(path);

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
    `;

    card.addEventListener("click", () => selectAlert(alert));

    alertsEl.appendChild(card);
  }
}

function selectAlert(alert) {
  timelineEl.innerHTML = `
    <div class="empty-state">
      Selected ${alert.id}. Investigation flow will be implemented in Day 4.
    </div>
  `;

  outputEl.textContent = JSON.stringify(alert, null, 2);
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
