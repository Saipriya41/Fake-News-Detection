"use strict";
const articleTA   = document.getElementById("article");
const wordCounter = document.getElementById("word-counter");
const clearBtn    = document.getElementById("clear-btn");
const checkBtn    = document.getElementById("check-btn");
const errorMsg    = document.getElementById("error-msg");
const resultPanel   = document.getElementById("result-panel");
const verdictBanner = document.getElementById("verdict-banner");
const verdictIcon   = document.getElementById("verdict-icon");
const verdictValue  = document.getElementById("verdict-value");
const ringFill      = document.getElementById("ring-fill");
const scoreNum      = document.getElementById("score-num");
const resultSummary = document.getElementById("result-summary");
const statsRow      = document.getElementById("stats-row");
const flagsSection  = document.getElementById("flags-section");
const flagsList     = document.getElementById("flags-list");
const breakdownTable = document.getElementById("breakdown-table");
const historySection = document.getElementById("history-section");
const historyList    = document.getElementById("history-list");
const historyCount   = document.getElementById("history-count");
function countWords(text) {
  return text.trim() === "" ? 0 : text.trim().split(/\s+/).length;
}
function showError(msg) {
  errorMsg.textContent = msg;
  errorMsg.classList.add("visible");
}
function clearError() {
  errorMsg.textContent = "";
  errorMsg.classList.remove("visible");
}
const ICONS = {
  real:       "✅",
  suspicious: "⚠️",
  fake:       "🚨",
};
function animateCount(el, end, ms = 800) {
  const start = parseInt(el.textContent, 10) || 0;
  const step  = (timestamp) => {
    if (!step.startTime) step.startTime = timestamp;
    const progress = Math.min((timestamp - step.startTime) / ms, 1);
    el.textContent  = Math.round(start + (end - start) * easeOut(progress));
    if (progress < 1) requestAnimationFrame(step);
  };
  requestAnimationFrame(step);
}
function easeOut(t) { return 1 - Math.pow(1 - t, 3); }
function setRing(score) {
  const CIRC = 150.796;
  const offset = CIRC - (score / 100) * CIRC;
  setTimeout(() => { ringFill.style.strokeDashoffset = offset; }, 60);
}
articleTA.addEventListener("input", () => {
  const wc = countWords(articleTA.value);
  wordCounter.textContent = `${wc} word${wc !== 1 ? "s" : ""}`;
  clearBtn.classList.toggle("visible", articleTA.value.length > 0);
  clearError();
});
clearBtn.addEventListener("click", () => {
  articleTA.value = "";
  wordCounter.textContent = "0 words";
  clearBtn.classList.remove("visible");
  clearError();
  articleTA.focus();
});
checkBtn.addEventListener("click", async () => {
  const text = articleTA.value.trim();
  if (!text) {
    showError("Please paste or type a news article first.");
    articleTA.focus();
    return;
  }
  if (text.length < 10) {
    showError("Article is too short to analyse. Please enter more text.");
    articleTA.focus();
    return;
  }
  clearError();
  setLoading(true);
  try {
    const response = await fetch("/check", {
      method:  "POST",
      headers: { "Content-Type": "application/json" },
      body:    JSON.stringify({ article: text }),
    });
    const data = await response.json();
    if (!response.ok) {
      showError(data.error || "Server error. Please try again.");
      return;
    }
    renderResult(data);
    loadHistory();     
  } catch (err) {
    showError("Network error. Make sure the Flask server is running.");
    console.error("Fetch error:", err);
  } finally {
    setLoading(false);
  }
});
function setLoading(state) {
  checkBtn.disabled = state;
  checkBtn.classList.toggle("loading", state);
}
function renderResult(data) {
  const { verdict, verdict_class, score, summary, flags, details, word_count } = data;
  resultPanel.removeAttribute("hidden");
  resultPanel.style.animation = "none";
  void resultPanel.offsetWidth;
  resultPanel.style.animation = "";
  verdictBanner.className = `verdict-banner ${verdict_class}`;
  verdictIcon.textContent = ICONS[verdict_class] || "🔍";
  verdictValue.textContent = verdict;
  setRing(score);
  animateCount(scoreNum, score);
  resultSummary.textContent = summary;
  statsRow.innerHTML = "";
  const chips = [
    { icon: "📝", val: word_count,            lbl: "Words" },
    { icon: "🎯", val: `${score}/100`,         lbl: "Risk Score" },
    { icon: "🚩", val: flags.length,           lbl: "Flags" },
    { icon: "📋", val: details.length,         lbl: "Rules Checked" },
  ];
  chips.forEach(chip => {
    statsRow.insertAdjacentHTML("beforeend", `
      <div class="stat-chip">
        <span class="stat-chip-icon">${chip.icon}</span>
        <span class="stat-chip-info">
          <span class="stat-chip-val">${chip.val}</span>
          <span class="stat-chip-lbl">${chip.lbl}</span>
        </span>
      </div>
    `);
  });
  if (flags.length > 0) {
    flagsSection.removeAttribute("hidden");
    flagsList.innerHTML = "";
    flags.forEach((flag, i) => {
      const li = document.createElement("li");
      li.textContent = flag;
      li.style.animationDelay = `${i * 0.06}s`;
      flagsList.appendChild(li);
    });
  } else {
    flagsSection.setAttribute("hidden", "");
  }
  breakdownTable.innerHTML = `
    <div class="bt-row bt-header">
      <span class="bt-rule">Rule</span>
      <span class="bt-detail">Detail</span>
      <span class="bt-impact">Impact</span>
    </div>
  `;
  details.forEach(row => {
    const impactNum = parseInt(row.impact, 10);
    let impactClass = "zero";
    if (impactNum > 0)  impactClass = "pos";
    if (impactNum < 0)  impactClass = "neg";
    breakdownTable.insertAdjacentHTML("beforeend", `
      <div class="bt-row">
        <span class="bt-rule">${escHtml(row.rule)}</span>
        <span class="bt-detail">${escHtml(row.detail)}</span>
        <span class="bt-impact ${impactClass}">${row.impact}</span>
      </div>
    `);
  });
  resultPanel.scrollIntoView({ behavior: "smooth", block: "nearest" });
}
async function loadHistory() {
  try {
    const res  = await fetch("/history");
    const data = await res.json();
    const items = data.history || [];
    if (items.length === 0) return;
    historySection.removeAttribute("hidden");
    historyCount.textContent = `${items.length} recent`;
    historyList.innerHTML = "";
    items.forEach(item => {
      historyList.insertAdjacentHTML("beforeend", `
        <div class="history-item">
          <span class="history-verdict ${item.verdict.toLowerCase().includes("fake") ? "fake"
            : item.verdict.toLowerCase().includes("suspicious") ? "suspicious"
            : "real"}">${item.verdict}</span>
          <span class="history-snippet">${escHtml(item.snippet)}</span>
          <span class="history-time">${item.timestamp}</span>
        </div>
      `);
    });
  } catch {
  }
}
function escHtml(str) {
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}
loadHistory();
articleTA.addEventListener("keydown", (e) => {
  if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
    checkBtn.click();
  }
});
