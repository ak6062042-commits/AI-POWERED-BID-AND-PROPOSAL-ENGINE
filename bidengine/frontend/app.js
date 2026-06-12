const API = "/api";
let currentWorkspace = null;
let selectedFile = null;

// ============================================================
// Init
// ============================================================
document.addEventListener("DOMContentLoaded", () => {
  checkHealth();
  loadWorkspaces();

  document.getElementById("newWorkspaceBtn").onclick = openModal;
  document.getElementById("welcomeNewBtn").onclick = openModal;
  document.getElementById("modalCancelBtn").onclick = closeModal;
  document.getElementById("modalCreateBtn").onclick = submitNewWorkspace;
  document.getElementById("workspaceNameInput").addEventListener("keydown", (e) => {
    if (e.key === "Enter") submitNewWorkspace();
  });

  // Tabs
  document.querySelectorAll(".tab").forEach((tab) => {
    tab.onclick = () => switchTab(tab.dataset.tab);
  });

  // Upload
  const dropzone = document.getElementById("dropzone");
  const fileInput = document.getElementById("fileInput");
  dropzone.onclick = () => fileInput.click();
  fileInput.onchange = (e) => handleFileSelect(e.target.files[0]);
  dropzone.ondragover = (e) => { e.preventDefault(); dropzone.classList.add("dragover"); };
  dropzone.ondragleave = () => dropzone.classList.remove("dragover");
  dropzone.ondrop = (e) => {
    e.preventDefault();
    dropzone.classList.remove("dragover");
    if (e.dataTransfer.files.length) handleFileSelect(e.dataTransfer.files[0]);
  };

  document.getElementById("uploadBtn").onclick = uploadFile;
  document.getElementById("analyzeBtn").onclick = runAnalysis;
  document.getElementById("exportBtn").onclick = exportProposal;

  const slider = document.getElementById("competitorSlider");
  slider.oninput = () => {
    document.getElementById("competitorValue").textContent = slider.value;
  };
});

// ============================================================
// Health check
// ============================================================
async function checkHealth() {
  const pill = document.getElementById("apiStatus");
  try {
    const res = await fetch(`${API}/health`);
    const data = await res.json();
    pill.classList.add("ok");
    const llmNote = data.llm_enrichment_available ? "LLM enrichment on" : "LLM enrichment off (rule-based only)";
    pill.innerHTML = `<span class="status-dot"></span> API connected · ${llmNote}`;
  } catch (e) {
    pill.innerHTML = `<span class="status-dot"></span> API offline`;
  }
}

// ============================================================
// Modal
// ============================================================
function openModal() {
  document.getElementById("modalOverlay").style.display = "flex";
  document.getElementById("workspaceNameInput").value = "";
  document.getElementById("workspaceNameInput").focus();
}
function closeModal() {
  document.getElementById("modalOverlay").style.display = "none";
}
async function submitNewWorkspace() {
  const name = document.getElementById("workspaceNameInput").value.trim();
  if (!name) return;
  const res = await fetch(`${API}/workspaces`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name }),
  });
  const record = await res.json();
  closeModal();
  await loadWorkspaces();
  selectWorkspace(record.id);
}

// ============================================================
// Workspace list (sidebar)
// ============================================================
async function loadWorkspaces() {
  const res = await fetch(`${API}/workspaces`);
  const list = await res.json();
  const container = document.getElementById("workspaceList");
  container.innerHTML = "";
  if (!list.length) {
    container.innerHTML = `<div class="empty-state">No workspaces yet. Create one to begin.</div>`;
    return;
  }
  list.forEach((ws) => {
    const item = document.createElement("div");
    item.className = "ws-item" + (currentWorkspace && currentWorkspace.id === ws.id ? " active" : "");
    item.onclick = () => selectWorkspace(ws.id);

    let badges = `<span class="ws-badge status-${ws.status}">${ws.status}</span>`;
    if (ws.go_no_go) {
      const cls = ws.go_no_go === "GO" ? "go" : ws.go_no_go === "NO-GO" ? "no-go" : "conditional";
      badges += `<span class="ws-badge ${cls}">${ws.go_no_go}</span>`;
    }

    item.innerHTML = `
      <div class="ws-item-name">${escapeHtml(ws.name)}</div>
      <div class="ws-item-meta">${badges}</div>
    `;
    container.appendChild(item);
  });
}

// ============================================================
// Select / render workspace
// ============================================================
async function selectWorkspace(id) {
  const res = await fetch(`${API}/workspaces/${id}`);
  if (!res.ok) return;
  currentWorkspace = await res.json();

  document.getElementById("view-welcome").style.display = "none";
  document.getElementById("view-workspace").style.display = "block";

  await loadWorkspaces(); // refresh active highlight
  renderWorkspace();
}

function renderWorkspace() {
  const ws = currentWorkspace;
  document.getElementById("wsTitle").textContent = ws.name;

  const badge = document.getElementById("wsStatusBadge");
  badge.textContent = ws.status === "new" ? "Awaiting upload"
    : ws.status === "extracted" ? "Extracted — ready to analyze"
    : "Analyzed";

  document.getElementById("exportBtn").disabled = ws.status !== "analyzed";

  // Reset upload UI
  document.getElementById("dropzoneFile").textContent = ws.source_file ? `Loaded: ${ws.source_file}` : "";
  document.getElementById("uploadBtn").disabled = true;
  selectedFile = null;

  if (ws.extraction) {
    renderExtraction();
    document.getElementById("analyzeCard").style.display = "block";
  } else {
    document.getElementById("extractionSummaryCard").style.display = "none";
    document.getElementById("analyzeCard").style.display = "none";
  }

  if (ws.checklist) {
    renderChecklist();
  } else {
    document.getElementById("checklistPlaceholder").style.display = "block";
    document.getElementById("checklistContent").style.display = "none";
  }

  if (ws.draft) {
    renderDraft();
  } else {
    document.getElementById("draftPlaceholder").style.display = "block";
    document.getElementById("draftContent").style.display = "none";
  }

  if (ws.scoring_result) {
    renderDashboard();
  } else {
    document.getElementById("dashboardPlaceholder").style.display = "block";
    document.getElementById("dashboardContent").style.display = "none";
  }

  // jump to a sensible default tab
  if (ws.status === "analyzed") {
    switchTab("dashboard");
  } else if (ws.status === "extracted") {
    switchTab("upload");
  } else {
    switchTab("upload");
  }
}

// ============================================================
// Tabs
// ============================================================
function switchTab(tabName) {
  document.querySelectorAll(".tab").forEach((t) => t.classList.toggle("active", t.dataset.tab === tabName));
  document.querySelectorAll(".tab-panel").forEach((p) => p.classList.remove("active"));
  document.getElementById(`panel-${tabName}`).classList.add("active");
}

// ============================================================
// Upload + extraction
// ============================================================
function handleFileSelect(file) {
  if (!file) return;
  selectedFile = file;
  document.getElementById("dropzoneFile").textContent = `Selected: ${file.name}`;
  document.getElementById("uploadBtn").disabled = false;
}

async function uploadFile() {
  if (!selectedFile || !currentWorkspace) return;
  const btn = document.getElementById("uploadBtn");
  btn.disabled = true;
  btn.textContent = "Extracting…";

  const formData = new FormData();
  formData.append("file", selectedFile);

  try {
    const res = await fetch(`${API}/workspaces/${currentWorkspace.id}/upload`, {
      method: "POST",
      body: formData,
    });
    if (!res.ok) {
      const err = await res.json();
      alert("Extraction failed: " + (err.detail || res.statusText));
      return;
    }
    currentWorkspace = await res.json();
    renderWorkspace();
    await loadWorkspaces();
  } finally {
    btn.textContent = "Extract requirements";
    btn.disabled = !selectedFile;
  }
}

function renderExtraction() {
  const ex = currentWorkspace.extraction;
  document.getElementById("extractionSummaryCard").style.display = "block";

  const metrics = document.getElementById("extractionMetrics");
  metrics.innerHTML = `
    <div class="metric"><div class="metric-value">${ex.mandatory_requirements.length}</div><div class="metric-label">Mandatory requirements</div></div>
    <div class="metric"><div class="metric-value">${ex.evaluation_criteria.length}</div><div class="metric-label">Evaluation criteria</div></div>
    <div class="metric"><div class="metric-value">${ex.qa_sections.length}</div><div class="metric-label">Narrative sections</div></div>
  `;

  // Deadlines
  const deadlines = ex.deadlines.filter(d => d.date);
  const deadlineContainer = document.getElementById("extractDeadlines");
  deadlineContainer.innerHTML = deadlines.length
    ? deadlines.map(d => `<span class="tag tag-strong">${escapeHtml(d.date)}</span>`).join("")
    : `<span class="tag">No explicit dates detected</span>`;

  // Budget
  const budgets = ex.budget.filter(b => b.amount);
  const budgetContainer = document.getElementById("extractBudget");
  budgetContainer.innerHTML = budgets.length
    ? budgets.map(b => `<span class="tag tag-strong">${escapeHtml(b.amount)}</span>`).join("")
    : `<span class="tag">No explicit budget figure detected</span>`;

  // Evaluation criteria
  const evalContainer = document.getElementById("extractEvalCriteria");
  evalContainer.innerHTML = ex.evaluation_criteria.length
    ? ex.evaluation_criteria.map(c => `
        <div class="eval-bar-row">
          <div class="eval-bar-label">${escapeHtml(c.criterion)}</div>
          <div class="eval-bar-track"><div class="eval-bar-fill" style="width:${c.weight_pct}%"></div></div>
          <div class="eval-bar-pct">${c.weight_pct}%</div>
        </div>`).join("")
    : `<div class="card-hint">No weighted evaluation criteria detected.</div>`;
}

// ============================================================
// Analysis
// ============================================================
async function runAnalysis() {
  const btn = document.getElementById("analyzeBtn");
  btn.disabled = true;
  btn.textContent = "Analyzing…";

  const payload = {
    estimated_competitor_count: parseInt(document.getElementById("competitorSlider").value, 10),
    past_relationship: document.getElementById("pastRelationshipCheckbox").checked,
    use_llm: document.getElementById("useLlmCheckbox").checked,
  };

  try {
    const res = await fetch(`${API}/workspaces/${currentWorkspace.id}/analyze`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!res.ok) {
      const err = await res.json();
      alert("Analysis failed: " + (err.detail || res.statusText));
      return;
    }
    currentWorkspace = await res.json();
    renderWorkspace();
    await loadWorkspaces();
  } finally {
    btn.disabled = false;
    btn.textContent = "Run full analysis →";
  }
}

// ============================================================
// Compliance checklist
// ============================================================
function renderChecklist() {
  document.getElementById("checklistPlaceholder").style.display = "none";
  document.getElementById("checklistContent").style.display = "block";

  const summary = currentWorkspace.checklist_summary;
  document.getElementById("checklistSummary").innerHTML = `
    <div class="summary-stat pass"><div class="value">${summary.pass}</div><div class="label">Pass</div></div>
    <div class="summary-stat partial"><div class="value">${summary.partial}</div><div class="label">Partial — needs review</div></div>
    <div class="summary-stat gap"><div class="value">${summary.gap}</div><div class="label">Gap — no evidence</div></div>
    <div class="summary-stat"><div class="value">${summary.requirements_matched_pct}%</div><div class="label">Overall coverage</div></div>
  `;

  const table = document.getElementById("checklistTable");
  table.innerHTML = currentWorkspace.checklist.map(item => {
    const best = item.best_match;
    const evidence = best
      ? `<div class="ev-title">${escapeHtml(best.title)}</div>
         <div class="ev-meta">${best.client_type} · ${best.year_completed} · PKR ${best.contract_value_pkr.toLocaleString()} · similarity ${best.similarity}</div>`
      : `<div class="ev-title">No matching capability found</div>
         <div class="ev-meta">Consider sourcing a case study or partnering for this requirement.</div>`;
    return `
      <div class="checklist-row">
        <div class="checklist-status ${item.status}">${item.status}</div>
        <div>
          <div class="checklist-req">${escapeHtml(item.requirement)}</div>
          <div class="checklist-evidence">${evidence}</div>
        </div>
      </div>`;
  }).join("");
}

// ============================================================
// Proposal draft
// ============================================================
function renderDraft() {
  document.getElementById("draftPlaceholder").style.display = "none";
  const container = document.getElementById("draftContent");
  container.style.display = "block";

  container.innerHTML = currentWorkspace.draft.map(section => {
    const evidence = (section.evidence_used || []).map(e => e.title).join(", ") || "No evidence matched";
    return `
      <div class="draft-section" data-section-id="${section.id}">
        <div class="draft-question">${escapeHtml(section.id)} — ${escapeHtml(section.question)}</div>
        <textarea class="draft-textarea">${escapeHtml(section.draft_response)}</textarea>
        <div class="draft-footer">
          <div class="draft-evidence">Evidence: ${escapeHtml(evidence)}</div>
          <div style="display:flex; align-items:center; gap:10px;">
            <span class="draft-status ${section.status}">${section.status.replace("_"," ")}</span>
            <button class="btn draft-save-btn" onclick="saveDraftSection('${section.id}', this)">Mark approved</button>
          </div>
        </div>
      </div>`;
  }).join("");
}

async function saveDraftSection(sectionId, btn) {
  const sectionEl = document.querySelector(`.draft-section[data-section-id="${sectionId}"]`);
  const text = sectionEl.querySelector(".draft-textarea").value;
  btn.disabled = true;
  btn.textContent = "Saving…";

  const res = await fetch(`${API}/workspaces/${currentWorkspace.id}/draft/${sectionId}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ draft_response: text, status: "approved" }),
  });
  currentWorkspace = await res.json();
  renderDraft();
}

// ============================================================
// Dashboard
// ============================================================
function renderDashboard() {
  document.getElementById("dashboardPlaceholder").style.display = "none";
  const container = document.getElementById("dashboardContent");
  container.style.display = "block";

  const score = currentWorkspace.scoring_result;
  const decision = currentWorkspace.go_no_go;
  const stampClass = decision.decision === "GO" ? "go" : decision.decision === "NO-GO" ? "no-go" : "conditional";

  const factorsHtml = score.top_contributing_factors.map(f => {
    const cls = f.contribution >= 0 ? "positive" : "negative";
    const sign = f.contribution >= 0 ? "+" : "";
    return `
      <div class="factor-row">
        <div class="factor-name">${formatFeatureName(f.feature)} <span style="color:var(--text-faint)">(value: ${f.value})</span></div>
        <div class="factor-value ${cls}">${sign}${f.contribution}</div>
      </div>`;
  }).join("");

  container.innerHTML = `
    <div class="dashboard-grid">
      <div>
        <div class="stamp ${stampClass}">
          <div class="stamp-label">Recommendation</div>
          <div class="stamp-decision">${decision.decision}</div>
        </div>
        <div class="win-prob-card">
          <div class="win-prob-value">${score.win_probability_pct}%</div>
          <div class="win-prob-bar"><div class="win-prob-fill" style="width:${score.win_probability_pct}%"></div></div>
          <div class="win-prob-compare">
            Modeled win probability vs. historical base rate of ${score.base_win_rate_pct}%
            (model trained on 120 past bids, ${score.model_train_accuracy_pct}% training accuracy)
          </div>
        </div>
      </div>
      <div>
        <div class="card" style="margin-bottom:18px;">
          <h3>Why this recommendation</h3>
          <ul class="reasons-list">
            ${decision.reasons.map(r => `<li>${escapeHtml(r)}</li>`).join("")}
          </ul>
        </div>
        <div class="factors-card">
          <h3>Top factors driving the score</h3>
          <p class="card-hint">Each factor's contribution to the win-probability prediction (logistic regression, standardized).</p>
          ${factorsHtml}
        </div>
      </div>
    </div>
  `;
}

function formatFeatureName(f) {
  const map = {
    certifications_match_pct: "Certification match",
    requirements_matched_pct: "Requirements coverage",
    past_relationship: "Existing client relationship",
    budget_alignment_score: "Budget alignment",
    technical_score_pct: "Technical score proxy",
    estimated_competitor_count: "Competitor count",
  };
  return map[f] || f;
}

// ============================================================
// Export
// ============================================================
function exportProposal() {
  if (!currentWorkspace) return;
  window.open(`${API}/workspaces/${currentWorkspace.id}/export`, "_blank");
}

// ============================================================
// Helpers
// ============================================================
function escapeHtml(str) {
  if (str === null || str === undefined) return "";
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}
