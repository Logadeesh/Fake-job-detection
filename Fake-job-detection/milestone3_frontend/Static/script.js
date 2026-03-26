// ========================================
// JOBSHIELD AI — script.js
// Connects to Flask /predict, /stats, /history
// ========================================

// ── On load: fetch model stats from DB ──
window.addEventListener("DOMContentLoaded", () => {
  fetchModelStats();
});

// ── Character counter ──
function onType() {
  const ta = document.getElementById("description");
  const cc = document.getElementById("charCount");
  const len = ta.value.length;
  cc.textContent = len + " / 5000";
  cc.className = "char-count" + (len > 4500 ? " warn" : "");

  const hint = document.getElementById("hintText");
  const words = ta.value.trim().split(/\s+/).filter(Boolean).length;
  if (words === 0) {
    hint.textContent = "Minimum 20 words recommended for accurate prediction.";
  } else if (words < 10) {
    hint.textContent = `${words} words — add more for better accuracy.`;
  } else if (words < 20) {
    hint.textContent = `${words} words — almost there.`;
  } else {
    hint.textContent = `${words} words — ready to analyze.`;
  }
}

// ── Main analyze function ──
async function analyzeJob() {
  const text = document.getElementById("description").value.trim();

  if (text.split(/\s+/).filter(Boolean).length < 5) {
    shakeTextarea();
    return;
  }

  const btn = document.getElementById("analyzeBtn");
  btn.disabled = true;
  btn.innerHTML = '<div class="spinner"></div><span class="btn-text">Analyzing...</span>';

  try {
    const response = await fetch("/predict", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ description: text }),
    });

    if (!response.ok) throw new Error("Server error");

    const data = await response.json();
    showResult(data);
    fetchModelStats(); // refresh DB stats after new prediction saved

  } catch (err) {
    showError();
  }

  btn.disabled = false;
  btn.innerHTML = '<span class="btn-text">Analyze Job Post</span><span class="btn-icon"><svg width="18" height="18" viewBox="0 0 18 18" fill="none"><circle cx="9" cy="9" r="7.5" stroke="currentColor" stroke-width="1.5"/><path d="M6 9l2.5 2.5L13 6" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg></span>';
}

// ── Render results ──
function showResult(data) {
  const isFake = data.verdict === "FAKE";
  const isSusp = data.verdict === "SUSPICIOUS";
  const isReal = data.verdict === "REAL";

  const cls   = isFake ? "verdict-fake" : isSusp ? "verdict-susp" : "verdict-real";
  const icoCls = isFake ? "verdict-icon-fake" : isSusp ? "verdict-icon-susp" : "verdict-icon-real";
  const icon  = isFake ? "🚨" : isSusp ? "⚠️" : "✅";
  const badge = isFake ? data.score + "%" : isReal ? data.real_probability + "%" : data.score + "%";
  const fillColor = isFake ? "#e84040" : isSusp ? "#d4860e" : "#3dba72";

  // verdict card
  const vc = document.getElementById("verdictCard");
  vc.className = "verdict-card " + cls;
  document.getElementById("verdictIcon").className = "verdict-icon " + icoCls;
  document.getElementById("verdictIcon").textContent = icon;
  document.getElementById("verdictTitle").textContent = data.result;
  document.getElementById("verdictSub").textContent =
    `Confidence: ${isFake || isSusp ? data.fake_probability : data.real_probability}% · ${data.word_count} words processed`;
  document.getElementById("verdictBadge").textContent = badge;

  // meter
  const fill = document.getElementById("meterFill");
  fill.style.background = fillColor;
  document.getElementById("meterVal").textContent = data.score + "%";
  setTimeout(() => { fill.style.width = data.score + "%"; }, 80);

  // stats
  document.getElementById("statFakeProb").textContent = data.fake_probability + "%";
  document.getElementById("statRealProb").textContent = data.real_probability + "%";
  document.getElementById("statWords").textContent = data.word_count;

  // keywords
  let kwHtml = "";
  if (data.matched_fake_keywords && data.matched_fake_keywords.length > 0) {
    kwHtml += `<div class="kw-group">
      <div class="kw-title">🔴 Fake keywords found in your text (TF-IDF)</div>
      <div class="kw-chips">${data.matched_fake_keywords.map(w =>
        `<span class="kw-chip kw-chip-red">${w}</span>`
      ).join("")}</div>
    </div>`;
  }
  if (data.matched_real_keywords && data.matched_real_keywords.length > 0) {
    kwHtml += `<div class="kw-group">
      <div class="kw-title">🟢 Legit keywords found in your text (TF-IDF)</div>
      <div class="kw-chips">${data.matched_real_keywords.map(w =>
        `<span class="kw-chip kw-chip-green">${w}</span>`
      ).join("")}</div>
    </div>`;
  }
  if (!kwHtml) {
    kwHtml = `<div class="kw-group">
      <div class="kw-title">Keywords</div>
      <div class="kw-chips"><span class="kw-chip kw-chip-gray">No top model keywords matched in this text</span></div>
    </div>`;
  }
  document.getElementById("keywordsSection").innerHTML = kwHtml;

  // cleaned preview (NLP pipeline output)
  document.getElementById("previewCard").innerHTML = `
    <div class="preview-label">NLP Pipeline Output — Cleaned & Lemmatized Text</div>
    <div class="preview-text">${escapeHtml(data.cleaned_preview)}</div>
  `;

  // show result, hide form
  document.getElementById("resultArea").classList.remove("hidden");
  document.getElementById("analyzeCard").classList.add("hidden");
  document.getElementById("resultArea").scrollIntoView({ behavior: "smooth", block: "start" });
}

// ── Reset ──
function resetForm() {
  document.getElementById("resultArea").classList.add("hidden");
  document.getElementById("analyzeCard").classList.remove("hidden");
  document.getElementById("meterFill").style.width = "0%";
  document.getElementById("description").value = "";
  document.getElementById("charCount").textContent = "0 / 5000";
  document.getElementById("hintText").textContent = "Minimum 20 words recommended for accurate prediction.";
  document.getElementById("analyzeCard").scrollIntoView({ behavior: "smooth" });
  closeHistory();
}

// ── Load history from SQLite via /history ──
async function loadHistory() {
  const panel = document.getElementById("historyPanel");
  panel.classList.remove("hidden");

  try {
    const res = await fetch("/history");
    const rows = await res.json();
    const list = document.getElementById("historyList");

    if (rows.length === 0) {
      list.innerHTML = '<p style="font-family: var(--mono); font-size: 12px; color: var(--text3);">No records yet.</p>';
      return;
    }

    list.innerHTML = rows.map(row => `
      <div class="history-item">
        <span class="history-desc">${escapeHtml(row.description)}</span>
        <span class="history-tag ${row.label === 1 ? 'history-tag-fake' : 'history-tag-real'}">
          ${row.label === 1 ? "FAKE" : "REAL"}
        </span>
      </div>
    `).join("");
  } catch {
    document.getElementById("historyList").innerHTML =
      '<p style="font-family: var(--mono); font-size: 12px; color: var(--text3);">Could not load history.</p>';
  }

  panel.scrollIntoView({ behavior: "smooth", block: "start" });
}

function closeHistory() {
  document.getElementById("historyPanel").classList.add("hidden");
}

// ── Fetch DB stats + top model words ──
async function fetchModelStats() {
  try {
    const res = await fetch("/stats");
    const data = await res.json();

    document.getElementById("dbTotal").textContent = data.total ?? "—";
    document.getElementById("dbFake").textContent  = data.fake  ?? "—";
    document.getElementById("dbReal").textContent  = data.real  ?? "—";

    let wordsHtml = "";
    if (data.top_fake_words && data.top_fake_words.length > 0) {
      wordsHtml += `<div class="word-group">
        <div class="word-group-title">Top fake indicator words</div>
        <div class="word-chips">${data.top_fake_words.map(w =>
          `<span class="kw-chip kw-chip-red">${w}</span>`).join("")}
        </div>
      </div>`;
    }
    if (data.top_real_words && data.top_real_words.length > 0) {
      wordsHtml += `<div class="word-group">
        <div class="word-group-title">Top legit indicator words</div>
        <div class="word-chips">${data.top_real_words.map(w =>
          `<span class="kw-chip kw-chip-green">${w}</span>`).join("")}
        </div>
      </div>`;
    }
    document.getElementById("topWordsRow").innerHTML = wordsHtml;
  } catch {
    // silently fail if model stats not available
  }
}

// ── Helpers ──
function escapeHtml(str) {
  if (!str) return "";
  return str.replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;");
}

function shakeTextarea() {
  const ta = document.getElementById("description");
  ta.style.transition = "none";
  ta.style.borderColor = "var(--red)";
  setTimeout(() => { ta.style.borderColor = ""; ta.style.transition = ""; }, 600);
  document.getElementById("hintText").textContent = "Please enter at least a few words from the job posting.";
  document.getElementById("hintText").style.color = "var(--red)";
  setTimeout(() => { document.getElementById("hintText").style.color = ""; }, 1500);
}

function showError() {
  document.getElementById("resultArea").classList.remove("hidden");
  document.getElementById("analyzeCard").classList.add("hidden");
  document.getElementById("resultArea").innerHTML = `
    <div style="background: var(--bg2); border: 1px solid rgba(232,64,64,0.3); border-radius: 18px; padding: 24px; text-align: center;">
      <p style="font-family: var(--mono); color: #ff6b6b; margin-bottom: 12px;">Server error — is Flask running?</p>
      <button class="reset-btn" onclick="resetForm()">← Try again</button>
    </div>
  `;
}
