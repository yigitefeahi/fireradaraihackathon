let API_BASE_URL =
  window.FIRERADAR_CONFIG && typeof window.FIRERADAR_CONFIG.getApiBaseUrl === "function"
    ? window.FIRERADAR_CONFIG.getApiBaseUrl()
    : typeof window.FIRERADAR_CONFIG?.defaultApiBase === "string"
      ? window.FIRERADAR_CONFIG.defaultApiBase
      : "http://localhost:8000";
const DEMO_PRODUCT_ID = "P001";

const state = {
  riskItems: [],
  selectedProductId: localStorage.getItem('fireradar_selected_product_id') || null,
  executiveDashboard: null,
  dailyWorkPlan: [],
  completedTasks: new Set(),
  operationsSnapshot: null,
  simpleMode: localStorage.getItem("fireradar_simple_mode") === "1",
};

const demoState = {
  steps: [],
  index: 0,
  timerId: null,
  isPlaying: false,
};

const els = {
  navLinks: document.querySelectorAll(".nav-link"),
  pages: document.querySelectorAll(".page"),
  demoBtn: document.querySelector("#demoBtn"),
  demoGuide: document.querySelector("#demoGuide"),
  demoTitle: document.querySelector("#demoTitle"),
  demoText: document.querySelector("#demoText"),
  demoCloseBtn: document.querySelector("#demoCloseBtn"),
  demoPrevBtn: document.querySelector("#demoPrevBtn"),
  demoNextBtn: document.querySelector("#demoNextBtn"),
  demoPlayPauseBtn: document.querySelector("#demoPlayPauseBtn"),
  simpleModeBtn: document.querySelector("#simpleModeBtn"),
  simpleModeHint: document.querySelector("#simpleModeHint"),
  impactSentence: document.querySelector("#impactSentence"),
  beforeLoss: document.querySelector("#beforeLoss"),
  afterLoss: document.querySelector("#afterLoss"),
  impactPreventable: document.querySelector("#impactPreventable"),
  impactFood: document.querySelector("#impactFood"),
  impactCo2: document.querySelector("#impactCo2"),
  impactSentenceReport: document.querySelector("#impactSentenceReport"),
  beforeLossReport: document.querySelector("#beforeLossReport"),
  afterLossReport: document.querySelector("#afterLossReport"),
  impactPreventableReport: document.querySelector("#impactPreventableReport"),
  impactFoodReport: document.querySelector("#impactFoodReport"),
  impactCo2Report: document.querySelector("#impactCo2Report"),
  impactSentenceStandalone: document.querySelector("#impactSentenceStandalone"),
  beforeLossStandalone: document.querySelector("#beforeLossStandalone"),
  afterLossStandalone: document.querySelector("#afterLossStandalone"),
  impactPreventableStandalone: document.querySelector("#impactPreventableStandalone"),
  impactFoodStandalone: document.querySelector("#impactFoodStandalone"),
  impactCo2Standalone: document.querySelector("#impactCo2Standalone"),
  headline: document.querySelector("#headline"),
  totalRisk: document.querySelector("#totalRisk"),
  preventableLoss: document.querySelector("#preventableLoss"),
  preventableLossHero: document.querySelector("#preventableLossHero"),
  wasteKgHero: document.querySelector("#wasteKgHero"),
  co2Hero: document.querySelector("#co2Hero"),
  revenueRisk: document.querySelector("#revenueRisk"),
  roiScore: document.querySelector("#roiScore"),
  riskTable: document.querySelector("#riskTable"),
  selectedProduct: document.querySelector("#selectedProduct"),
  dailySummary: document.querySelector("#dailySummary"),
  agentSteps: document.querySelector("#agentSteps"),
  agentStepsPage: document.querySelector("#agentStepsPage"),
  dailyTasks: document.querySelector("#dailyTasks"),
  dailyTasksPage: document.querySelector("#dailyTasksPage"),
  categoryBars: document.querySelector("#categoryBars"),
  categoryBarsReport: document.querySelector("#categoryBarsReport"),
  inventoryTable: document.querySelector("#inventoryTable"),
  productCards: document.querySelector("#productCards"),
  campaignProductSelect: document.querySelector("#campaignProductSelect"),
  campaignPageBtn: document.querySelector("#campaignPageBtn"),
  campaignPageOutput: document.querySelector("#campaignPageOutput"),
  supplierProductSelect: document.querySelector("#supplierProductSelect"),
  supplierPageBtn: document.querySelector("#supplierPageBtn"),
  supplierPageOutput: document.querySelector("#supplierPageOutput"),
  reportRisk: document.querySelector("#reportRisk"),
  reportSaved: document.querySelector("#reportSaved"),
  reportRevenueRisk: document.querySelector("#reportRevenueRisk"),
  reportCritical: document.querySelector("#reportCritical"),
  reportWasteKg: document.querySelector("#reportWasteKg"),
  reportCo2: document.querySelector("#reportCo2"),
  reportSummary: document.querySelector("#reportSummary"),
  decisionExplanation: document.querySelector("#decisionExplanation"),
  decisionExplanationPage: document.querySelector("#decisionExplanationPage"),
  decisionExplanationStandalone: document.querySelector("#decisionExplanationStandalone"),
  rescuePlaybook: document.querySelector("#rescuePlaybook"),
  rescuePlaybookPage: document.querySelector("#rescuePlaybookPage"),
  rescuePlaybookStandalone: document.querySelector("#rescuePlaybookStandalone"),
  actionComparisonTable: document.querySelector("#actionComparisonTable"),
  actionComparisonTablePage: document.querySelector("#actionComparisonTablePage"),
  actionComparisonTableStandalone: document.querySelector("#actionComparisonTableStandalone"),
  segmentMatches: document.querySelector("#segmentMatches"),
  segmentMatchesPage: document.querySelector("#segmentMatchesPage"),
  segmentMatchesStandalone: document.querySelector("#segmentMatchesStandalone"),
  supplierDecisionDetail: document.querySelector("#supplierDecisionDetail"),
  supplierDecisionOutput: document.querySelector("#supplierDecisionOutput"),
  discountRange: document.querySelector("#discountRange"),
  discountLabel: document.querySelector("#discountLabel"),
  channelSelect: document.querySelector("#channelSelect"),
  simulateBtn: document.querySelector("#simulateBtn"),
  simulationResult: document.querySelector("#simulationResult"),
  aiResult: document.querySelector("#aiResult"),
  refreshBtn: document.querySelector("#refreshBtn"),
  actionPlanBtn: document.querySelector("#actionPlanBtn"),
  campaignBtn: document.querySelector("#campaignBtn"),
  supplierBtn: document.querySelector("#supplierBtn"),
  copyTasksBtn: document.querySelector("#copyTasksBtn"),
  apiBaseInput: document.querySelector("#apiBaseInput"),
  apiBaseSaveBtn: document.querySelector("#apiBaseSaveBtn"),
  apiBaseDisplay: document.querySelector("#apiBaseDisplay"),
  chatToggle: document.querySelector("#chatToggle"),
  chatWidget: document.querySelector("#chatWidget"),
  chatCloseBtn: document.querySelector("#chatCloseBtn"),
  chatFullscreenBtn: document.querySelector("#chatFullscreenBtn"),
  chatForm: document.querySelector("#chatForm"),
  questionInput: document.querySelector("#questionInput"),
  chatLog: document.querySelector("#chatLog"),
  agentRailSteps: document.querySelector("#agentRailSteps"),
  operationsSnapshotPills: document.querySelector("#operationsSnapshotPills"),
  operationsDelayList: document.querySelector("#operationsDelayList"),
  analyticsFootnote: document.querySelector("#analyticsFootnote"),
  analyticsExpiring: document.querySelector("#analyticsExpiring"),
  analyticsVelocity: document.querySelector("#analyticsVelocity"),
  recommendationEvidenceTable: document.querySelector("#recommendationEvidenceTable"),
  aiCampaignChannel: document.querySelector("#aiCampaignChannel"),
  campaignChannelSelect: document.querySelector("#campaignChannelSelect"),
  ordersPageOpsPills: document.querySelector("#ordersPageOpsPills"),
  ordersPageDelayList: document.querySelector("#ordersPageDelayList"),
  runAgentBtn: document.querySelector("#runAgentBtn"),
  agentRunOutput: document.querySelector("#agentRunOutput"),
  actionLogList: document.querySelector("#actionLogList"),
};

function formatCurrency(value) {
  return new Intl.NumberFormat("tr-TR", {
    style: "currency",
    currency: "TRY",
    maximumFractionDigits: 0,
  }).format(value || 0);
}

function formatKg(value) {
  return `${new Intl.NumberFormat("tr-TR", { maximumFractionDigits: 1 }).format(value || 0)} kg`;
}

function resolveApiBase() {
  if (window.FIRERADAR_CONFIG && typeof window.FIRERADAR_CONFIG.getApiBaseUrl === "function") {
    return window.FIRERADAR_CONFIG.getApiBaseUrl();
  }
  return API_BASE_URL;
}

async function copyTextToClipboard(text) {
  const value = String(text || "").trim();
  if (!value) {
    return false;
  }
  try {
    await navigator.clipboard.writeText(value);
    return true;
  } catch {
    try {
      const area = document.createElement("textarea");
      area.value = value;
      area.style.position = "fixed";
      area.style.left = "-9999px";
      document.body.appendChild(area);
      area.select();
      document.execCommand("copy");
      document.body.removeChild(area);
      return true;
    } catch {
      return false;
    }
  }
}

function readCopySource(selector) {
  const node = document.querySelector(selector);
  if (!node) {
    return "";
  }
  return node.innerText || node.textContent || "";
}

function downloadTextAsFile(filename, text) {
  const blob = new Blob([String(text || "")], { type: "text/plain;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = filename || "fireradar.txt";
  anchor.rel = "noopener";
  anchor.click();
  URL.revokeObjectURL(url);
}

function flashCopied(button) {
  if (!button) return;
  const previous = button.textContent;
  button.textContent = "Kopyalandı!";
  button.disabled = true;
  window.setTimeout(() => {
    button.textContent = previous;
    button.disabled = false;
  }, 1400);
}

function bindCopyDownloadHelpers() {
  document.body.addEventListener("click", async (event) => {
    const copyBtn = event.target.closest("[data-copy-from]");
    if (copyBtn) {
      event.preventDefault();
      const selector = copyBtn.getAttribute("data-copy-from");
      const text = readCopySource(selector);
      const control = copyBtn.closest("button") || copyBtn;
      const trimmed = String(text || "").trim();
      if (!trimmed) {
        const previous = control.textContent;
        control.textContent = "Metin yok";
        control.disabled = true;
        window.setTimeout(() => {
          control.textContent = previous;
          control.disabled = false;
        }, 1400);
        return;
      }
      const ok = await copyTextToClipboard(trimmed);
      if (ok) {
        flashCopied(control);
      } else {
        const previous = control.textContent;
        control.textContent = "Kopyalanamadı";
        control.disabled = true;
        window.setTimeout(() => {
          control.textContent = previous;
          control.disabled = false;
        }, 1400);
      }
      return;
    }

    const downloadBtn = event.target.closest("[data-download-from]");
    if (downloadBtn) {
      event.preventDefault();
      const selector = downloadBtn.getAttribute("data-download-from");
      const name = downloadBtn.getAttribute("data-download-name") || "fireradar.txt";
      const text = readCopySource(selector);
      const control = downloadBtn.closest("button") || downloadBtn;
      if (!String(text || "").trim()) {
        const previous = control.textContent;
        control.textContent = "İndirilecek metin yok";
        control.disabled = true;
        window.setTimeout(() => {
          control.textContent = previous;
          control.disabled = false;
        }, 1600);
        return;
      }
      downloadTextAsFile(name, text);
    }
  });
}

function initSettingsBar() {
  if (!window.FIRERADAR_CONFIG) {
    return;
  }
  const bar = document.querySelector(".settings-bar");
  if (typeof window.FIRERADAR_CONFIG.isLocalFrontend === "function" && !window.FIRERADAR_CONFIG.isLocalFrontend()) {
    bar?.remove();
    API_BASE_URL = resolveApiBase();
    return;
  }
  const input = els.apiBaseInput;
  const save = els.apiBaseSaveBtn;
  const display = els.apiBaseDisplay;
  if (!input || !save) {
    return;
  }
  API_BASE_URL = resolveApiBase();
  const current = API_BASE_URL;
  const defaulted = window.FIRERADAR_CONFIG.defaultApiBase;
  input.value = current === defaulted ? "" : current;
  if (display) {
    display.textContent = current;
  }
  save.addEventListener("click", () => {
    const raw = input.value.trim();
    window.FIRERADAR_CONFIG.setApiBaseUrl(raw);
    window.location.reload();
  });
}

function applySimpleMode() {
  document.body.classList.toggle("simple-mode", state.simpleMode);
  if (els.simpleModeBtn) {
    els.simpleModeBtn.textContent = `Sade Mod: ${state.simpleMode ? "Açık" : "Kapalı"}`;
  }
  if (els.simpleModeHint) {
    els.simpleModeHint.style.display = state.simpleMode ? "inline-flex" : "none";
  }
}

function setSimpleMode(nextValue) {
  state.simpleMode = Boolean(nextValue);
  localStorage.setItem("fireradar_simple_mode", state.simpleMode ? "1" : "0");
  applySimpleMode();
}

function toggleSimpleMode() {
  setSimpleMode(!state.simpleMode);
}

async function api(path, options = {}) {
  API_BASE_URL = resolveApiBase();
  let response;
  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      headers: {
        "Content-Type": "application/json",
        ...(options.headers || {}),
      },
      ...options,
    });
  } catch (error) {
    throw new Error(
      `Backend'e bağlanılamadı (${API_BASE_URL}). Yerelde: cd backend && uvicorn main:app --reload — Canlıda: API sunucusu veya CORS ayarlarını kontrol edin.`,
    );
  }

  if (!response.ok) {
    let detail = "";
    try {
      const payload = await response.json();
      detail = payload?.detail || payload?.message || "";
    } catch {
      detail = "";
    }
    throw new Error(`API hatası: ${response.status}${detail ? ` - ${detail}` : ""}`);
  }

  return response.json();
}

/** Eski backend sürümünde veya geçici hata olduğunda tüm dashboard'u düşürmemek için. */
async function apiOptional(path, options = {}) {
  try {
    return await api(path, options);
  } catch {
    return null;
  }
}

function settledValue(result, fallback) {
  return result?.status === "fulfilled" ? result.value : fallback;
}

function formatPercentRate(value) {
  return `%${Math.round(Number(value || 0) * 100)}`;
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function safeRiskClass(level) {
  const known = new Set(["critical", "high", "medium", "low"]);
  return known.has(String(level || "").toLowerCase()) ? String(level).toLowerCase() : "low";
}

function setLoading(button, isLoading, label) {
  button.disabled = isLoading;
  button.textContent = isLoading ? "Hazırlanıyor..." : label;
}

function riskLabel(level) {
  const labels = {
    critical: "Çok acil",
    high: "Acil",
    medium: "Takip et",
    low: "Rahat",
  };
  return labels[level] || level;
}

function selectedItem() {
  return state.riskItems.find((item) => item.product_id === state.selectedProductId);
}

function demoScore(item) {
  return (item.preventable_loss || 0) * 0.5 + (item.estimated_revenue_at_risk || 0) * 0.3 + (item.risk_score || 0) * 10;
}

function selectBestDemoItem(items) {
  return [...items].sort((a, b) => demoScore(b) - demoScore(a))[0] || null;
}

function buildFriendlyHeadline(summary) {
  return (
    `Bugün hiçbir şey yapılmazsa yaklaşık ${formatCurrency(summary.total_estimated_loss)} fire maliyeti oluşabilir. ` +
    `Doğru ürünlere indirim ve müşteri mesajı ile yaklaşık ${formatCurrency(summary.total_preventable_loss)} geri kazanım fırsatı var.`
  );
}

function simplifyText(text) {
  return String(text || "")
    .replaceAll("AI aksiyonları", "önerilen adımlar")
    .replaceAll("ROI", "öncelik puanı")
    .replaceAll("projeksiyon", "tahmin")
    .replaceAll("operasyonel", "uygulanabilir")
    .replaceAll("net etki", "beklenen kazanç")
    .replaceAll("simülasyon", "karşılaştırma");
}

function renderAgentRailSteps(steps) {
  const target = els.agentRailSteps;
  if (!target) return;
  target.innerHTML = "";
  (steps || []).forEach((step, i) => {
    const chip = document.createElement("span");
    chip.className = "agent-rail-chip";
    chip.title = step.detail || "";
    chip.innerHTML = `<span class="rail-idx">${i + 1}</span><span class="rail-txt">${escapeHtml(step.title)}</span>`;
    target.appendChild(chip);
  });
}

function renderOperationsPillsHost(ops, pillsEl, delayEl) {
  if (!pillsEl) return;
  const s = ops?.summary || {};
  pillsEl.innerHTML = "";
  const rows = [
    ["Hazırlıkta", s.preparing, "sipariş"],
    ["Bugün başlayan hazırlık", s.preparing_started_today, ""],
    ["Son 14 gün teslim", s.recent_delivered_14d, ""],
    ["Son 14 gün iptal", s.recent_cancelled_14d, ""],
    ["Kritik gecikme", s.delay_flagged_orders, "sipariş"],
  ];
  rows.forEach(([label, n, suf]) => {
    const pill = document.createElement("div");
    pill.className = "ops-pill";
    pill.innerHTML = `<strong>${escapeHtml(n ?? 0)}</strong><span>${escapeHtml(label)}</span>${suf ? `<small>${escapeHtml(suf)}</small>` : ""}`;
    pillsEl.appendChild(pill);
  });

  if (!delayEl) return;
  delayEl.innerHTML = "";
  const items = ops?.delay_watch || [];
  if (!items.length) {
    const p = document.createElement("p");
    p.className = "delay-empty";
    p.textContent = "Şu anda gecikme uyarısı tetiklenen sipariş yok.";
    delayEl.appendChild(p);
    return;
  }
  items.forEach((row) => {
    const wrap = document.createElement("article");
    wrap.className = `delay-card ${row.delay_risk_level === "critical" ? "delay-critical" : "delay-warning"}`;
    const head = document.createElement("div");
    head.className = "delay-head";
    head.innerHTML = `<strong>${escapeHtml(row.order_id)}</strong> · ${escapeHtml(row.customer_name)} · ${escapeHtml(row.days_waiting)} gündür hazırlıkta`;
    const sub = document.createElement("small");
    sub.textContent = `Hedef çıkış: ${row.expected_dispatch_by}`;
    wrap.appendChild(head);
    wrap.appendChild(sub);
    if (row.customer_notify_draft) {
      const pre = document.createElement("pre");
      pre.className = "delay-draft";
      pre.textContent = row.customer_notify_draft;
      wrap.appendChild(pre);
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "ghost-btn delay-copy";
      btn.textContent = "Müşteri bilgilendirme taslağını kopyala";
      btn.addEventListener("click", async () => {
        await copyTextToClipboard(row.customer_notify_draft);
        flashCopied(btn);
      });
      wrap.appendChild(btn);
    }
    delayEl.appendChild(wrap);
  });
}

function renderAnalyticsPulseHost(analytics) {
  if (els.analyticsFootnote) {
    if (els.analyticsFootnote) els.analyticsFootnote.textContent = analytics?.footnote || "";
  }
  if (els.analyticsExpiring) {
    if (els.analyticsExpiring) els.analyticsExpiring.innerHTML = "<h4 class=\"pulse-h\">SKT 7 gün içinde — öncelik sırası</h4>";
    const ul = document.createElement("ul");
    ul.className = "pulse-ul";
    (analytics?.expiring_critical_7d || []).forEach((x) => {
      const li = document.createElement("li");
      li.textContent = `${x.name} · ${x.expiry_days_left} gün kaldı · ~${formatCurrency(x.preventable_loss)} kurtarılabilir`;
      ul.appendChild(li);
    });
    if (!ul.children.length) {
      const li = document.createElement("li");
      li.textContent = "Bu pencerede liste boş; yine de risk tablosunu kontrol edin.";
      ul.appendChild(li);
    }
    if (els.analyticsExpiring) els.analyticsExpiring.appendChild(ul);
  }
  if (els.analyticsVelocity) {
    if (els.analyticsVelocity) els.analyticsVelocity.innerHTML = "<h4 class=\"pulse-h\">Düşük hız + yakın SKT (izleme)</h4>";
    const ul = document.createElement("ul");
    ul.className = "pulse-ul muted";
    (analytics?.high_velocity_watch || []).forEach((x) => {
      const li = document.createElement("li");
      li.textContent = `${x.name} · ${x.daily_sales_velocity} adet/gün · ${x.note}`;
      ul.appendChild(li);
    });
    if (!ul.children.length) {
      const li = document.createElement("li");
      li.textContent = "Bu kural kombinasyonu için ek ürün yok.";
      ul.appendChild(li);
    }
    if (els.analyticsVelocity) els.analyticsVelocity.appendChild(ul);
  }
}

function renderRecommendationEvidence(data) {
  const tb = els.recommendationEvidenceTable;
  if (!tb) return;
  tb.innerHTML = "";
  if (!data || !data.facts) {
    const tr = document.createElement("tr");
    const td = document.createElement("td");
    td.colSpan = 3;
    td.textContent = state.selectedProductId
      ? "Kanıt tablosu bu API sürümünde yok veya yüklenemedi (404). Render’da backend’i son Git commit’iyle yeniden deploy edin."
      : "Ürün seçilince kanıt satırları yüklenecek.";
    tr.appendChild(td);
    tb.appendChild(tr);
    return;
  }
  data.facts.forEach((f) => {
    const tr = document.createElement("tr");
    [f.label, f.value, f.source].forEach((cell) => {
      const td = document.createElement("td");
      td.textContent = cell ?? "";
      tr.appendChild(td);
    });
    tb.appendChild(tr);
  });
}

const STALE_OPS_MESSAGE =
  "Sipariş & analitik özeti yeni API uçlarından gelir (/operations-snapshot). Backend eskiyse görünmez — Render üzerinden son GitHub commit’inde Manual Deploy yapın.";

function renderStaleOpsPanelsForDashboard() {
  if (els.operationsSnapshotPills) {
    if (els.operationsSnapshotPills) els.operationsSnapshotPills.innerHTML = `<p class="delay-empty ops-api-hint">${escapeHtml(STALE_OPS_MESSAGE)}</p>`;
  }
  if (els.operationsDelayList) if (els.operationsDelayList) els.operationsDelayList.innerHTML = "";
  if (els.analyticsFootnote) if (els.analyticsFootnote) els.analyticsFootnote.textContent = "";
  if (els.analyticsExpiring) if (els.analyticsExpiring) els.analyticsExpiring.innerHTML = "";
  if (els.analyticsVelocity) if (els.analyticsVelocity) els.analyticsVelocity.innerHTML = "";
}

function renderOperationsFromSnapshot(snapshot) {
  if (!snapshot || !snapshot.orders) {
    renderStaleOpsPanelsForDashboard();
    return;
  }
  const orders = snapshot.orders;
  renderOperationsPillsHost(orders, els.operationsSnapshotPills, els.operationsDelayList);
  renderAnalyticsPulseHost(snapshot.analytics);
}

function renderOperationsOntoSecondaryHosts() {
  if (!state.operationsSnapshot || !state.operationsSnapshot.orders) {
    if (els.ordersPageOpsPills) {
      if (els.ordersPageOpsPills) els.ordersPageOpsPills.innerHTML = `<p class="delay-empty ops-api-hint">${escapeHtml(STALE_OPS_MESSAGE)}</p>`;
    }
    if (els.ordersPageDelayList) if (els.ordersPageDelayList) els.ordersPageDelayList.innerHTML = "";
    return;
  }
  const orders = state.operationsSnapshot.orders;
  renderOperationsPillsHost(orders, els.ordersPageOpsPills, els.ordersPageDelayList);
}

function isElementVisible(node) {
  if (!node) return false;
  const style = window.getComputedStyle(node);
  if (style.display === "none" || style.visibility === "hidden") return false;
  return node.getClientRects().length > 0;
}

function highlightElement(selector, options = {}) {
  document.querySelectorAll(".demo-highlight").forEach((item) => item.classList.remove("demo-highlight"));
  const element = document.querySelector(selector);
  if (!element || !isElementVisible(element)) return false;
  const preciseSelectors = new Set([
    "#decisionSectionTitle",
    "#comparisonSectionTitle",
    "#segmentSectionTitle",
    "#decisionExplanation",
    "#actionComparisonTable",
    "#segmentMatches",
    "#riskTable tr.selected",
  ]);
  const highlightTarget = preciseSelectors.has(selector)
    ? element
    : element.closest(".panel, .card, .before-after, .headline-panel") || element;
  if (!isElementVisible(highlightTarget)) return false;
  highlightTarget.classList.add("demo-highlight");
  const block = options.block || (preciseSelectors.has(selector) ? "nearest" : "center");
  const forceTopOffset = Number(options.forceTopOffset || 0);
  if (forceTopOffset > 0) {
    const rect = highlightTarget.getBoundingClientRect();
    const targetTop = Math.max(window.scrollY + rect.top - forceTopOffset, 0);
    window.scrollTo({ top: targetTop, behavior: "smooth" });
  } else {
    highlightTarget.scrollIntoView({ behavior: "smooth", block });
    const offsetY = Number(options.offsetY || 0);
    if (offsetY !== 0) {
      window.setTimeout(() => {
        window.scrollBy({ top: offsetY, behavior: "smooth" });
      }, 180);
    }
  }
  return true;
}

async function startDemoScenario() {
  if (!state.riskItems.length) return;
  if (state.simpleMode) {
    setSimpleMode(false);
  }
  const fixedDemoItem =
    state.riskItems.find((item) => item.product_id === DEMO_PRODUCT_ID) || selectBestDemoItem(state.riskItems);
  state.selectedProductId = fixedDemoItem ? String(fixedDemoItem.product_id) : String(state.riskItems[0].product_id);
  localStorage.setItem("fireradar_selected_product_id", state.selectedProductId);
  renderTable(state.riskItems);
  renderSelectedProduct();
  await loadSelectedProductAgentDetails();
  if (els.demoGuide) els.demoGuide.classList.add("open");

  const selected = fixedDemoItem || selectedItem();
  const candidateSteps = [
    {
      title: "1. Problemin Finansal Büyüklüğü",
      text: "Hiç aksiyon alınmazsa bugünkü kayıp burada başlıyor. FireRadar, riski daha sorun büyümeden görünür hale getirir.",
      selector: "#totalRisk",
    },
    {
      title: "2. Önceliklendirilen Kritik Ürün",
      text: "Risk motoru, finansal etki ve zaman baskısını birlikte değerlendirerek bu ürünü ilk müdahale önceliği olarak seçti.",
      selector: "#selectedProduct",
      block: "nearest",
    },
    {
      title: "3. Karar Gerekçesi (Veri Temelli)",
      text: "AI; stok, son tüketim tarihi ve satış hızını birlikte okuyarak bu ürünün neden bugün aksiyon istediğini açıklar.",
      selector: "#decisionExplanation",
      forceTopOffset: 220,
    },
    {
      title: "4. Aksiyon Senaryoları ve Simülasyon",
      text: "Sistem tek öneri vermez; farklı aksiyonları yan yana karşılaştırır ve finansal etkisini şeffaf biçimde gösterir.",
      selector: "#actionComparisonTable",
      forceTopOffset: 220,
    },
    {
      title: "5. En Yüksek Net Etkiye Sahip Seçim",
      text: "Yeşil rozetli seçenek, beklenen kazanç ve risk azaltımı birlikte en güçlü sonucu verdiği için seçildi.",
      selector: ".best-action-row",
    },
    {
      title: "6. Doğru Segment, Doğru Kanal",
      text: "Doğru ürün + doğru müşteri + doğru kanal eşleşmesiyle kampanya metni operasyona hazır hale gelir.",
      selector: "#segmentSectionTitle",
    },
    {
      title: "7. Ölçülebilir Sonuç: AI Öncesi/AI Sonrası",
      text: "Özetle etki net: daha az fire, daha yüksek geri kazanım ve daha ölçülebilir operasyon yönetimi.",
      selector: "#impactSentence",
    },
  ];
  demoState.steps = candidateSteps.filter((step) => isElementVisible(document.querySelector(step.selector)));
  if (!demoState.steps.length) {
    if (els.demoTitle) els.demoTitle.textContent = "Demo hedefi bulunamadı";
    if (els.demoText) els.demoText.textContent = "Sayfayı yenileyip tekrar deneyin.";
    return;
  }
  demoState.index = 0;
  demoState.isPlaying = true;
  updateDemoGuideControls();
  renderCurrentDemoStep();
  scheduleDemoNext();
}

function updateDemoGuideControls() {
  if (els.demoPlayPauseBtn) {
    els.demoPlayPauseBtn.textContent = demoState.isPlaying ? "Duraklat" : "Devam";
  }
}

function stopDemoAutoplay() {
  if (demoState.timerId) {
    window.clearTimeout(demoState.timerId);
    demoState.timerId = null;
  }
}

function renderCurrentDemoStep() {
  if (!demoState.steps.length) return;
  const step = demoState.steps[demoState.index];
  if (els.demoTitle) {
    els.demoTitle.textContent = `${step.title} (${demoState.index + 1}/${demoState.steps.length})`;
  }
  if (els.demoText) els.demoText.textContent = step.text;
  const highlighted = highlightElement(step.selector, {
    block: step.block,
    offsetY: step.offsetY,
    forceTopOffset: step.forceTopOffset,
  });
  if (!highlighted && demoState.steps.length > 1) {
    nextDemoStep();
  }
}

function scheduleDemoNext() {
  stopDemoAutoplay();
  if (!demoState.isPlaying) return;
  demoState.timerId = window.setTimeout(() => {
    nextDemoStep();
  }, 3400);
}

function nextDemoStep() {
  if (!demoState.steps.length) return;
  demoState.index = (demoState.index + 1) % demoState.steps.length;
  renderCurrentDemoStep();
  scheduleDemoNext();
}

function prevDemoStep() {
  if (!demoState.steps.length) return;
  demoState.index = (demoState.index - 1 + demoState.steps.length) % demoState.steps.length;
  renderCurrentDemoStep();
  scheduleDemoNext();
}

function toggleDemoPlayPause() {
  demoState.isPlaying = !demoState.isPlaying;
  updateDemoGuideControls();
  if (demoState.isPlaying) {
    scheduleDemoNext();
  } else {
    stopDemoAutoplay();
  }
}

function closeDemoGuide() {
  if (els.demoGuide) els.demoGuide.classList.remove("open");
  stopDemoAutoplay();
  demoState.isPlaying = false;
  updateDemoGuideControls();
  document.querySelectorAll(".demo-highlight").forEach((item) => item.classList.remove("demo-highlight"));
}

function renderCards(summary) {
  if (els.totalRisk) els.totalRisk.textContent = formatCurrency(summary.total_estimated_loss);
  if (els.preventableLoss) els.preventableLoss.textContent = formatCurrency(summary.total_preventable_loss);
  if (els.preventableLossHero) els.preventableLossHero.textContent = formatCurrency(summary.total_preventable_loss);
  if (els.wasteKgHero) els.wasteKgHero.textContent = formatKg(summary.total_preventable_waste_kg);
  if (els.co2Hero) els.co2Hero.textContent = formatKg(summary.total_preventable_co2_kg);
  if (els.revenueRisk) els.revenueRisk.textContent = formatCurrency(summary.total_revenue_at_risk);
  if (els.roiScore) els.roiScore.textContent = summary.average_roi_score;
}

function renderProductCards(items) {
  if (els.productCards) els.productCards.innerHTML = "";
  items.slice(0, 8).forEach((item) => {
    const discount = Math.round((item.discount_recommendation || 0) * 100);
    const riskClass = safeRiskClass(item.risk_level);
    const card = document.createElement("article");
    card.className = "product-card";
    card.innerHTML = `
      <div class="product-card-top">
        <span class="badge ${riskClass}">${escapeHtml(riskLabel(item.risk_level))}</span>
        <small>${escapeHtml(item.expiry_days_left)} gün kaldı</small>
      </div>
      <strong>${escapeHtml(item.name)}</strong>
      <p>${escapeHtml(item.category)} | Stok: ${escapeHtml(item.stock_quantity)}</p>
      <div class="product-card-metrics">
        <span>%${escapeHtml(discount)} indirim</span>
        <span>${escapeHtml(formatCurrency(item.preventable_loss))}</span>
        <span>${escapeHtml(formatKg(item.preventable_waste_kg))} fire</span>
      </div>
    `;
    card.addEventListener("click", () => {
      state.selectedProductId = item.product_id;
    localStorage.setItem('fireradar_selected_product_id', item.product_id);
      renderTable(state.riskItems);
      renderSelectedProduct(item);
      loadSelectedProductAgentDetails();
      /* page switch handled by actual navigation */
    });
    if (els.productCards) els.productCards.appendChild(card);
  });
}

function renderInventoryTable(items) {
  if (els.inventoryTable) els.inventoryTable.innerHTML = "";
  items.forEach((item) => {
    const discount = Math.round((item.discount_recommendation || 0) * 100);
    const riskClass = safeRiskClass(item.risk_level);
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td><strong>${escapeHtml(item.name)}</strong></td>
      <td>${escapeHtml(item.category)}</td>
      <td>${escapeHtml(item.stock_quantity)}</td>
      <td>${escapeHtml(item.expiry_days_left)} gün</td>
      <td>%${escapeHtml(discount)}</td>
      <td>${escapeHtml(item.supplier)}</td>
      <td><span class="badge ${riskClass}">${escapeHtml(riskLabel(item.risk_level))}</span></td>
    `;
    tr.addEventListener("click", () => {
      state.selectedProductId = item.product_id;
    localStorage.setItem('fireradar_selected_product_id', item.product_id);
      renderTable(state.riskItems);
      renderSelectedProduct(item);
      loadSelectedProductAgentDetails();
      /* page switch handled by actual navigation */
    });
    if (els.inventoryTable) els.inventoryTable.appendChild(tr);
  });
}

function renderTable(items) {
  if (els.riskTable) els.riskTable.innerHTML = "";

  items.forEach((item) => {
    const riskClass = safeRiskClass(item.risk_level);
    const tr = document.createElement("tr");
    tr.dataset.productId = item.product_id;
    tr.className = item.product_id === state.selectedProductId ? "selected" : "";
    tr.innerHTML = `
      <td>
        <strong>${escapeHtml(item.name)}</strong><br />
        <span class="badge ${riskClass}">${escapeHtml(riskLabel(item.risk_level))}</span>
      </td>
      <td>${escapeHtml(item.stock_quantity)}</td>
      <td>${escapeHtml(item.expiry_days_left)} gün</td>
      <td>${escapeHtml(formatCurrency(item.estimated_loss))}</td>
      <td><strong>${escapeHtml(Math.round(item.roi_score))}</strong></td>
    `;
    tr.addEventListener("click", () => {
      state.selectedProductId = item.product_id;
    localStorage.setItem('fireradar_selected_product_id', item.product_id);
      renderTable(state.riskItems);
      renderSelectedProduct(item);
      loadSelectedProductAgentDetails();
      if (els.aiResult) els.aiResult.textContent = "";
    });
    if (els.riskTable) els.riskTable.appendChild(tr);
  });
}

function renderSelectedProduct(item = selectedItem()) {
  if (!els.selectedProduct) {
    return;
  }
  if (!item) {
    if (els.selectedProduct) els.selectedProduct.textContent = "Henüz ürün seçilmedi.";
    return;
  }

  const discount = Math.round((item.discount_recommendation || 0) * 100);
  els.selectedProduct.innerHTML = `
    <div>
      <span>Şimdi önerilen ürün</span>
      <strong>${escapeHtml(item.name)}</strong>
      <p>${escapeHtml(item.expiry_days_left)} gün kaldı. Ürün için tahmini fire maliyeti ${escapeHtml(formatCurrency(item.estimated_loss))}.</p>
      <p>Doğru aksiyonla yaklaşık ${escapeHtml(formatCurrency(item.preventable_loss))} geri kazanım fırsatı var.</p>
    </div>
    <div class="next-step">
      <b>Basit öneri</b>
      <p>%${escapeHtml(discount)} indirim yap, ürünü görünür yere koy, müşteriye mesaj gönder.</p>
    </div>
  `;
}

function renderAgentSteps(steps, target = els.agentSteps) {
  if (!target) return;
  target.innerHTML = "";
  steps.forEach((step) => {
    const item = document.createElement("div");
    item.className = "agent-step";
    item.innerHTML = `
      <span>✓</span>
      <div>
        <strong>${escapeHtml(step.title)}</strong>
        <p>${escapeHtml(step.detail)}</p>
      </div>
    `;
    target.appendChild(item);
  });
}

function renderDailyTasks(tasks, target = els.dailyTasks) {
  if (!target) return;
  target.innerHTML = "";
  tasks.forEach((task) => {
    const isDone = state.completedTasks.has(`${target.id}-${task.product_id}`);
    const item = document.createElement("div");
    item.className = `task-item ${isDone ? "done" : ""}`;
    item.innerHTML = `
      <span>${escapeHtml(task.order)}</span>
      <div>
        <strong>${escapeHtml(task.urgency)}: ${escapeHtml(task.product_name)}</strong>
        <p>${escapeHtml(task.task)}</p>
        <small>${escapeHtml(task.customer_action)} ${escapeHtml(task.why)}</small>
      </div>
      <button class="task-done-btn" type="button">${isDone ? "Tamamlandı" : "Tamamla"}</button>
    `;
    item.addEventListener("click", () => {
      state.selectedProductId = task.product_id;
    localStorage.setItem('fireradar_selected_product_id', task.product_id);
      renderTable(state.riskItems);
      renderSelectedProduct();
      loadSelectedProductAgentDetails();
    });
    item.querySelector(".task-done-btn").addEventListener("click", (event) => {
      event.stopPropagation();
      const key = `${target.id}-${task.product_id}`;
      if (state.completedTasks.has(key)) {
        state.completedTasks.delete(key);
      } else {
        state.completedTasks.add(key);
      }
      renderDailyTasks(tasks, target);
    });
    target.appendChild(item);
  });
}

function renderCategoryBars(categories, target = els.categoryBars) {
  if (!target) return;
  target.innerHTML = "";
  const maxLoss = Math.max(...categories.map((item) => item.preventable_loss), 1);
  categories.forEach((item) => {
    const row = document.createElement("div");
    row.className = "bar-row";
    const width = Math.max(8, (item.preventable_loss / maxLoss) * 100);
    row.innerHTML = `
      <div class="bar-meta">
        <strong>${escapeHtml(item.category)}</strong>
        <span>${escapeHtml(formatCurrency(item.preventable_loss))}</span>
      </div>
      <div class="bar-track"><div style="width: ${width}%"></div></div>
      <small>Risk puanı: ${escapeHtml(item.average_risk_score)} | Çok acil ürün: ${escapeHtml(item.critical_count)}</small>
    `;
    target.appendChild(row);
  });
}

function populateProductSelects(items) {
  [els.campaignProductSelect, els.supplierProductSelect].forEach((select) => {
    if (!select) return;
    select.innerHTML = "";
    items.forEach((item) => {
      const option = document.createElement("option");
      option.value = item.product_id;
      option.textContent = `${item.name} (${riskLabel(item.risk_level)})`;
      select.appendChild(option);
    });
  });
}

function renderReports(summary) {
  if (els.reportRisk) els.reportRisk.textContent = formatCurrency(summary.total_estimated_loss);
  if (els.reportSaved) els.reportSaved.textContent = formatCurrency(summary.total_preventable_loss);
  if (els.reportRevenueRisk) els.reportRevenueRisk.textContent = formatCurrency(summary.total_revenue_at_risk);
  if (els.reportCritical) els.reportCritical.textContent = summary.critical_product_count;
  if (els.reportWasteKg) els.reportWasteKg.textContent = formatKg(summary.total_preventable_waste_kg);
  if (els.reportCo2) els.reportCo2.textContent = formatKg(summary.total_preventable_co2_kg);
  if (!els.reportSummary) return;
  els.reportSummary.textContent =
    `Bugün ${summary.high_risk_product_count} ürün dikkat istiyor. ` +
    `Hiçbir şey yapılmazsa yaklaşık ${formatCurrency(summary.total_estimated_loss)} fire maliyeti oluşabilir. ` +
    `Doğru ürünlere indirim, görünür raf ve müşteri mesajı ile yaklaşık ${formatCurrency(summary.total_preventable_loss)} kurtarılabilir değer var. ` +
    `Bu aynı zamanda yaklaşık ${formatKg(summary.total_preventable_waste_kg)} fire ve ${formatKg(summary.total_preventable_co2_kg)} CO₂ etkisinin önüne geçmek demek.`;
}

async function initApp() {
  if (els.dailySummary) els.dailySummary.textContent = "Yükleniyor...";
  if (els.aiResult) els.aiResult.textContent = "";
  if (els.simulationResult) els.simulationResult.textContent = "";

  const [riskResult, dailySummaryResult, executiveResult, beforeAfterResult, opsSnapshotResult] = await Promise.allSettled([
    api("/risk-analysis"),
    api("/daily-summary"),
    api("/executive-dashboard"),
    api("/before-after-impact"),
    api("/operations-snapshot"),
  ]);

  if (riskResult.status !== "fulfilled") {
    throw riskResult.reason;
  }
  const riskAnalysis = riskResult.value;
  const dailySummary = settledValue(dailySummaryResult, { message: "Günlük özet şu an alınamadı." });
  const executive = settledValue(executiveResult, {
    dashboard: null,
    agent_activity: [],
    daily_work_plan: [],
    category_heatmap: [],
  });
  const beforeAfter = settledValue(beforeAfterResult, {
    impact: {
      one_sentence_impact: "Etki bilgisi şu an alınamadı.",
      before_ai_estimated_loss: 0,
      after_ai_remaining_loss: 0,
      preventable_loss: 0,
      preventable_waste_kg: 0,
      preventable_co2_kg: 0,
    },
  });
  const opsSnapshot = settledValue(opsSnapshotResult, null);

  state.operationsSnapshot = opsSnapshot;
  renderOperationsFromSnapshot(opsSnapshot);
  renderAgentRailSteps(executive.agent_activity || []);

  state.riskItems = riskAnalysis.items;
  const pinnedDemo = riskAnalysis.items.find((item) => item.product_id === DEMO_PRODUCT_ID);
  state.selectedProductId = pinnedDemo?.product_id || selectBestDemoItem(riskAnalysis.items)?.product_id || null;
  localStorage.setItem("fireradar_selected_product_id", state.selectedProductId || "");
  state.executiveDashboard = executive.dashboard;
  if (els.headline) els.headline.textContent = buildFriendlyHeadline(riskAnalysis.summary);
  renderCards(riskAnalysis.summary);
  renderTable(riskAnalysis.items);
  renderProductCards(riskAnalysis.items);
  renderInventoryTable(riskAnalysis.items);
  populateProductSelects(riskAnalysis.items);
  renderSelectedProduct();
  renderAgentSteps(executive.agent_activity || []);
  renderAgentSteps(executive.agent_activity || [], els.agentStepsPage);
  state.dailyWorkPlan = executive.daily_work_plan || [];
  renderDailyTasks(state.dailyWorkPlan);
  renderDailyTasks(state.dailyWorkPlan, els.dailyTasksPage);
  renderCategoryBars(executive.category_heatmap || []);
  renderCategoryBars(executive.category_heatmap || [], els.categoryBarsReport);
  renderReports(riskAnalysis.summary);
  renderBeforeAfter(beforeAfter.impact);
  if (els.dailySummary) els.dailySummary.textContent = simplifyText(dailySummary.message);
  await loadSelectedProductAgentDetails();
}

async function runAgentFlow() {
  if (!els.runAgentBtn) return;
  const productId = state.selectedProductId || DEMO_PRODUCT_ID;
  setLoading(els.runAgentBtn, true, "AI Agent'i Çalıştır");
  if (els.agentRunOutput) els.agentRunOutput.textContent = "Agent akışı çalışıyor...";
  try {
    const result = await api(`/run-agent/${productId}`, {
      method: "POST",
      body: JSON.stringify({ log_actions: true }),
    });

    renderDecisionExplanation(result.decision_explanation || {});
    renderActionComparison(result.action_comparison || { comparison: [], best_action: null });
    renderSegmentMatches(result.customer_segment || { target_customers: [] });

    const supplier = result.supplier_email_draft || {};
    if (els.supplierDecisionOutput) {
      els.supplierDecisionOutput.textContent =
        `Konu: ${supplier.subject || "-"}\n` +
        `Önerilen miktar değişimi: ${supplier.recommended_quantity_change ?? "-"}\n\n` +
        `${supplier.reason || ""}\n\n${supplier.body || ""}`;
    }

    const risk = result.product_risk_analysis || {};
    const loss = result.loss_estimation || {};
    const best = result.best_action_recommendation || {};
    if (els.agentRunOutput) {
      els.agentRunOutput.textContent =
        `Ürün: ${risk.product_name} (${risk.product_id})\n` +
        `Risk: ${risk.risk_level} / skor ${risk.risk_score}\n` +
        `Kalan süre: ${risk.expiry_days_left} gün\n` +
        `Tahmini fire maliyeti: ${formatCurrency(loss.estimated_loss)}\n` +
        `Kaçan ciro riski: ${formatCurrency(loss.estimated_revenue_at_risk)}\n` +
        `Kurtarılabilir değer: ${formatCurrency(loss.preventable_loss)}\n\n` +
        `En iyi aksiyon: ${best.action_name || "-"}\n` +
        `Kanal: ${best.channel || "-"}\n` +
        `İndirim: ${formatPercentRate(best.discount_rate)}\n` +
        `Operasyon maliyeti: ${formatCurrency(best.operation_cost)}\n` +
        `Beklenen kazanç: ${formatCurrency(best.net_impact)}\n` +
        `Kayıp azaltımı: %${Math.round(Number(best.loss_reduction_percent || 0))}\n\n` +
        `Güven skoru: ${best.confidence || "-"} / 100\n` +
        `Neden: ${best.why_this_action || "-"}\n` +
        `${best.hard_constraint_applied ? `Gıda güvenliği kuralı: ${best.constraint_reason || "aktif"}\n` : ""}` +
        `Agent açıklaması: ${result.agent_explanation || "-"}`;
    }

    const logs = result.action_logs || [];
    if (els.actionLogList) {
      if (!logs.length) {
        els.actionLogList.textContent = "Henüz log yok.";
      } else {
        els.actionLogList.textContent = logs
          .map((log) => `- [${log.status || "completed"}] ${log.timestamp}: ${log.message} (${log.action_type})`)
          .join("\n");
      }
    }
  } catch (error) {
    if (els.agentRunOutput) els.agentRunOutput.textContent = error.message;
  } finally {
    setLoading(els.runAgentBtn, false, "AI Agent'i Çalıştır");
  }
}

function renderBeforeAfter(impact) {
  if (els.impactSentence) els.impactSentence.textContent = impact.one_sentence_impact;
  if (els.beforeLoss) els.beforeLoss.textContent = formatCurrency(impact.before_ai_estimated_loss);
  if (els.afterLoss) els.afterLoss.textContent = formatCurrency(impact.after_ai_remaining_loss);
  if (els.impactPreventable) els.impactPreventable.textContent = formatCurrency(impact.preventable_loss);
  if (els.impactFood) els.impactFood.textContent = formatKg(impact.preventable_waste_kg);
  if (els.impactCo2) els.impactCo2.textContent = formatKg(impact.preventable_co2_kg);
  if (els.impactSentenceReport) els.impactSentenceReport.textContent = impact.one_sentence_impact;
  if (els.beforeLossReport) els.beforeLossReport.textContent = formatCurrency(impact.before_ai_estimated_loss);
  if (els.afterLossReport) els.afterLossReport.textContent = formatCurrency(impact.after_ai_remaining_loss);
  if (els.impactPreventableReport) els.impactPreventableReport.textContent = formatCurrency(impact.preventable_loss);
  if (els.impactFoodReport) els.impactFoodReport.textContent = formatKg(impact.preventable_waste_kg);
  if (els.impactCo2Report) els.impactCo2Report.textContent = formatKg(impact.preventable_co2_kg);
  if (els.impactSentenceStandalone) els.impactSentenceStandalone.textContent = impact.one_sentence_impact;
  if (els.beforeLossStandalone) els.beforeLossStandalone.textContent = formatCurrency(impact.before_ai_estimated_loss);
  if (els.afterLossStandalone) els.afterLossStandalone.textContent = formatCurrency(impact.after_ai_remaining_loss);
  if (els.impactPreventableStandalone) els.impactPreventableStandalone.textContent = formatCurrency(impact.preventable_loss);
  if (els.impactFoodStandalone) els.impactFoodStandalone.textContent = formatKg(impact.preventable_waste_kg);
  if (els.impactCo2Standalone) els.impactCo2Standalone.textContent = formatKg(impact.preventable_co2_kg);
}

async function loadSelectedProductAgentDetails() {
  if (!state.selectedProductId) {
    renderRecommendationEvidence(null);
    return;
  }
  try {
    const [decision, comparison, playbook, segments, supplierDecision, evidence] = await Promise.all([
      api(`/decision-explanation/${state.selectedProductId}`),
      api(`/action-comparison/${state.selectedProductId}`),
      api(`/rescue-playbook/${state.selectedProductId}`),
      api(`/segment-matches/${state.selectedProductId}`),
      api(`/supplier-decision/${state.selectedProductId}`),
      apiOptional(`/recommendation-evidence/${state.selectedProductId}`),
    ]);
    renderRecommendationEvidence(evidence && !evidence.error && evidence.facts ? evidence : null);
    renderDecisionExplanation(decision);
    renderDecisionExplanation(decision, els.decisionExplanationPage);
    renderDecisionExplanation(decision, els.decisionExplanationStandalone);
    renderActionComparison(comparison);
    renderActionComparison(comparison, els.actionComparisonTablePage);
    renderActionComparison(comparison, els.actionComparisonTableStandalone);
    renderRescuePlaybook(playbook);
    renderRescuePlaybook(playbook, els.rescuePlaybookPage);
    renderRescuePlaybook(playbook, els.rescuePlaybookStandalone);
    renderSegmentMatches(segments);
    renderSegmentMatches(segments, els.segmentMatchesPage);
    renderSegmentMatches(segments, els.segmentMatchesStandalone);
    renderSupplierDecision(supplierDecision);
  } catch (error) {
    renderRecommendationEvidence(null);
    if (els.decisionExplanation) els.decisionExplanation.textContent = "AI detayları yüklenemedi.";
    if (els.rescuePlaybook) els.rescuePlaybook.textContent = error.message;
  }
}

function renderDecisionExplanation(decision, target = els.decisionExplanation) {
  if (!target) return;
  target.classList.add("decision-rich");
  const evidenceItems = (decision.evidence || [])
    .map((item) => `<li>${escapeHtml(item)}</li>`)
    .join("");
  target.innerHTML = `
    <strong>${escapeHtml(decision.decision_summary)}</strong>
    <p>${escapeHtml(decision.why_critical)}</p>
    <ul>${evidenceItems}</ul>
    <div class="confidence">
      Güven skoru: <b>${escapeHtml(decision.confidence_score)}/100</b>
      <span>Veri kalitesi: ${escapeHtml(decision.data_quality || "Orta")}</span>
    </div>
    <p>${escapeHtml(decision.confidence_reason || "")}</p>
    <p><b>Beklenen sonuç:</b> ${escapeHtml(decision.expected_result)}</p>
  `;
}

function renderActionComparison(comparison, target = els.actionComparisonTable) {
  if (!target) return;
  target.innerHTML = "";
  (comparison.comparison || []).forEach((action) => {
    const tr = document.createElement("tr");
    tr.className = action.action_key === comparison.best_action ? "best-action-row" : "";
    tr.innerHTML = `
      <td><strong>${escapeHtml(action.action_name)}</strong>${action.action_key === comparison.best_action ? '<br><span class="ai-choice-badge">AI Seçimi</span>' : ""}</td>
      <td>${escapeHtml(action.channel)}</td>
      <td>%${escapeHtml(Math.round((action.discount_rate || 0) * 100))}</td>
      <td>${escapeHtml(action.expected_units_sold)}</td>
      <td>${escapeHtml(formatCurrency(action.prevented_loss))}</td>
      <td>${escapeHtml(formatCurrency(action.net_impact))}</td>
      <td>%${escapeHtml(action.loss_reduction_percent)}</td>
      <td>${escapeHtml(formatCurrency(action.operation_cost))}</td>
      <td>${escapeHtml(action.confidence || "-")}/100</td>
      <td>${escapeHtml(action.why_this_action || "-")}</td>
    `;
    target.appendChild(tr);
  });
}

function renderRescuePlaybook(playbook, target = els.rescuePlaybook) {
  if (!target) return;
  target.innerHTML = `
    <div><span>Birincil plan</span><p>${escapeHtml(playbook.primary_playbook)}</p></div>
    <div><span>Acil durum</span><p>${escapeHtml(playbook.emergency_playbook)}</p></div>
    <div><span>Bundle önerisi</span><p>${escapeHtml(playbook.suggested_bundle)}</p></div>
    <div><span>Hedef segment</span><p>${escapeHtml(playbook.ideal_customer_segment)}</p></div>
    <div><span>Mesaj açısı</span><p>${escapeHtml(playbook.message_angle)}</p></div>
    <div><span>Bağış / ikincil kullanım</span><p>${escapeHtml(playbook.donation_or_secondary_use || "Uygun bağış veya ikincil kullanım kanalını değerlendir.")}</p></div>
  `;
}

function renderSegmentMatches(segments, target = els.segmentMatches) {
  if (!target) return;
  target.innerHTML = "";
  (segments.target_customers || []).slice(0, 3).forEach((customer, index) => {
    const card = document.createElement("article");
    card.className = "customer-message-card";
    const messageId = `segment-msg-${target.id}-${index}`;
    card.innerHTML = `
      <strong>${escapeHtml(customer.customer_name)}</strong>
      <span>${escapeHtml(customer.segment)} | ${escapeHtml(customer.channel)}</span>
      <p>${escapeHtml(customer.reason)}</p>
      <div id="${escapeHtml(messageId)}" class="customer-message-body">${escapeHtml(customer.message)}</div>
      <div class="customer-message-actions">
        <button type="button" class="ghost-btn" data-copy-from="#${escapeHtml(messageId)}">Mesajı kopyala</button>
      </div>
    `;
    target.appendChild(card);
  });
}

function renderSupplierDecision(decision) {
  const labels = {
    reduce_or_delay_order: "Siparişi azalt / ertele",
    increase_order: "Siparişi artır",
    keep_order: "Siparişi aynı tut",
  };
  const inv = decision.inventory_signals;
  const text =
    `Karar: ${labels[decision.supplier_action_type] || decision.supplier_action_type}\n` +
    `Önerilen değişiklik (satır): ${decision.recommended_quantity_change}\n\n` +
    `Neden: ${decision.reason}\n\n` +
    `Konu: ${decision.email_subject}\n\n` +
    `${decision.email_body}`;

  const fillNode = (node) => {
    if (!node) return;
    node.innerHTML = "";
    if (inv) {
      const box = document.createElement("div");
      box.className = "supplier-inv-signals";
      const title = document.createElement("strong");
      title.textContent = "Stok & SKT sinyalleri";
      const ul = document.createElement("ul");
      const li1 = document.createElement("li");
      li1.textContent = `Stok ${inv.stock_quantity} adet · minimum eşik ${inv.min_stock_threshold} · durum: ${inv.stock_status}`;
      ul.appendChild(li1);
      const li2 = document.createElement("li");
      li2.textContent = `Stok örtüşmesi ≈ ${inv.days_of_cover} gün · SKT’ye ${inv.expiry_days_left} gün`;
      ul.appendChild(li2);
      if (decision.suggested_next_order_qty) {
        const li3 = document.createElement("li");
        li3.textContent = `Önerilen sipariş adedi (yönetime): ${decision.suggested_next_order_qty} birim`;
        ul.appendChild(li3);
      }
      if (decision.suggested_adjustment_note) {
        const li4 = document.createElement("li");
        li4.textContent = decision.suggested_adjustment_note;
        ul.appendChild(li4);
      }
      box.appendChild(title);
      box.appendChild(ul);
      node.appendChild(box);
    }
    const pre = document.createElement("pre");
    pre.className = "supplier-decision-pre";
    pre.textContent = text;
    node.appendChild(pre);
  };

  fillNode(els.supplierDecisionOutput);
  fillNode(els.supplierDecisionDetail);
}

async function simulateAction() {
  setLoading(els.simulateBtn, true, "Sonucu Göster");
  try {
    const discountRate = Number(els.discountRange.value) / 100;
    const result = await api("/simulate-action", {
      method: "POST",
      body: JSON.stringify({
        product_id: state.selectedProductId,
        discount_rate: discountRate,
        channel: els.channelSelect.value,
      }),
    });
    els.simulationResult.textContent =
      `${result.product_name}\n\n` +
      `Bu indirimle yaklaşık ${result.with_action.expected_units_sold} adet satılabilir.\n` +
      `Kurtarılabilecek para: ${formatCurrency(result.impact.prevented_loss)}\n` +
      `Operasyon maliyeti: ${formatCurrency(result.impact.operation_cost)}\n` +
      `Hiçbir şey yapılmazsa fire maliyeti: ${formatCurrency(result.no_action.estimated_loss)}\n` +
      `Fire maliyeti azaltımı: %${result.impact.loss_reduction_percent}`;
  } catch (error) {
    if (els.simulationResult) els.simulationResult.textContent = error.message;
  } finally {
    setLoading(els.simulateBtn, false, "Sonucu Göster");
  }
}

async function generateActionPlan() {
  setLoading(els.actionPlanBtn, true, "Bana Yapılacakları Yaz");
  try {
    const result = await api("/generate-action-plan", {
      method: "POST",
      body: JSON.stringify({ product_id: state.selectedProductId }),
    });
    if (els.aiResult) els.aiResult.textContent = result.action_plan;
  } catch (error) {
    if (els.aiResult) els.aiResult.textContent = error.message;
  } finally {
    setLoading(els.actionPlanBtn, false, "Bana Yapılacakları Yaz");
  }
}

async function generateCampaignMessage() {
  setLoading(els.campaignBtn, true, "Müşteri Mesajı Hazırla");
  try {
    const ch = els.aiCampaignChannel?.value || "SMS";
    const result = await api("/generate-campaign-message", {
      method: "POST",
      body: JSON.stringify({
        product_id: state.selectedProductId,
        channel: ch,
        tone: "samimi",
      }),
    });
    if (els.aiResult) els.aiResult.textContent = result.campaign_message;
  } catch (error) {
    if (els.aiResult) els.aiResult.textContent = error.message;
  } finally {
    setLoading(els.campaignBtn, false, "Müşteri Mesajı Hazırla");
  }
}

async function generateSupplierOrder() {
  setLoading(els.supplierBtn, true, "Tedarikçi Kararı Oluştur");
  try {
    const result = await api("/generate-supplier-order", {
      method: "POST",
      body: JSON.stringify({ product_id: state.selectedProductId }),
    });
    const order = result.supplier_order;
    els.aiResult.textContent =
      `Konu: ${order.subject}\n` +
      `Önerilen adet: ${order.recommended_quantity}\n\n` +
      `${order.body}`;
  } catch (error) {
    if (els.aiResult) els.aiResult.textContent = error.message;
  } finally {
    setLoading(els.supplierBtn, false, "Tedarikçi Kararı Oluştur");
  }
}

async function generateCampaignPageMessage() {
  setLoading(els.campaignPageBtn, true, "Müşteri Mesajı Hazırla");
  if (els.campaignPageOutput) els.campaignPageOutput.textContent = "Mesaj hazırlanıyor...";
  try {
    const ch = els.campaignChannelSelect?.value || "SMS";
    const result = await api("/generate-campaign-message", {
      method: "POST",
      body: JSON.stringify({
        product_id: els.campaignProductSelect.value,
        channel: ch,
        tone: "samimi",
      }),
    });
    if (els.campaignPageOutput) els.campaignPageOutput.textContent = result.campaign_message;
  } catch (error) {
    if (els.campaignPageOutput) els.campaignPageOutput.textContent = error.message;
  } finally {
    setLoading(els.campaignPageBtn, false, "Müşteri Mesajı Hazırla");
  }
}

async function generateSupplierPageOrder() {
  setLoading(els.supplierPageBtn, true, "Tedarikçi Kararı Oluştur");
  if (els.supplierPageOutput) els.supplierPageOutput.textContent = "Tedarikçi mesajı hazırlanıyor...";
  try {
    const result = await api("/generate-supplier-order", {
      method: "POST",
      body: JSON.stringify({ product_id: els.supplierProductSelect.value }),
    });
    const order = result.supplier_order;
    els.supplierPageOutput.textContent =
      `Konu: ${order.subject}\n` +
      `Önerilen adet: ${order.recommended_quantity}\n\n` +
      `${order.body}`;
  } catch (error) {
    if (els.supplierPageOutput) els.supplierPageOutput.textContent = error.message;
  } finally {
    setLoading(els.supplierPageBtn, false, "Tedarikçi Kararı Oluştur");
  }
}

function addChatMessage(text, type) {
  const div = document.createElement("div");
  div.className = type;
  div.textContent = text;
  if (els.chatLog) els.chatLog.appendChild(div);
  els.chatLog.scrollTop = els.chatLog.scrollHeight;
}

function openChat() {
  if (els.chatWidget) els.chatWidget.classList.add("open");
  if (els.chatToggle) els.chatToggle.classList.add("hidden");
  setTimeout(() => els.questionInput.focus(), 120);
}

function closeChat() {
  if (els.chatWidget) els.chatWidget.classList.remove("open", "fullscreen");
  if (els.chatToggle) els.chatToggle.classList.remove("hidden");
}

function toggleChatFullscreen() {
  if (els.chatWidget) els.chatWidget.classList.toggle("fullscreen");
}

async function askAI(event) {
  event.preventDefault();
  const question = els.questionInput.value.trim();
  if (!question) return;

  if (els.questionInput) els.questionInput.value = "";
  addChatMessage(question, "user");
  addChatMessage("Yanıt hazırlanıyor...", "bot");
  const pending = els.chatLog.lastElementChild;

  try {
    const result = await api("/ask-ai", {
      method: "POST",
      body: JSON.stringify({
        question,
        product_id: DEMO_PRODUCT_ID,
      }),
    });
    pending.textContent = result.answer;
  } catch (error) {
    pending.textContent = error.message;
  }
}

function copyDailyTasksList() {
  const tasks = state.dailyWorkPlan || [];
  if (!tasks.length) {
    return;
  }
  const lines = tasks.map(
    (task) =>
      `${task.order}. ${task.urgency}: ${task.product_name}\n   ${task.task}\n   ${task.customer_action} ${task.why}`,
  );
  copyTextToClipboard(lines.join("\n\n"));
  flashCopied(els.copyTasksBtn);
}

bindCopyDownloadHelpers();
initSettingsBar();
applySimpleMode();

/* els.navLinks.forEach((link) => {
  link.addEventListener("click", () => switchPage(link.dataset.pageTarget));
}); */
if (els.copyTasksBtn) {
  els.copyTasksBtn?.addEventListener("click", copyDailyTasksList);
}
if (els.demoBtn) els.demoBtn?.addEventListener("click", startDemoScenario);
if (els.demoCloseBtn) els.demoCloseBtn?.addEventListener("click", closeDemoGuide);
if (els.demoNextBtn) els.demoNextBtn?.addEventListener("click", nextDemoStep);
if (els.demoPrevBtn) els.demoPrevBtn?.addEventListener("click", prevDemoStep);
if (els.demoPlayPauseBtn) els.demoPlayPauseBtn?.addEventListener("click", toggleDemoPlayPause);
if (els.refreshBtn) els.refreshBtn?.addEventListener("click", initApp);
if (els.simpleModeBtn) els.simpleModeBtn?.addEventListener("click", toggleSimpleMode);
els.simulateBtn?.addEventListener("click", simulateAction);
els.discountRange?.addEventListener("input", () => {
  if (els.discountLabel) els.discountLabel.textContent = `%${els.discountRange.value}`;
});
els.actionPlanBtn?.addEventListener("click", generateActionPlan);
els.campaignBtn?.addEventListener("click", generateCampaignMessage);
els.supplierBtn?.addEventListener("click", generateSupplierOrder);
els.campaignPageBtn?.addEventListener("click", generateCampaignPageMessage);
els.supplierPageBtn?.addEventListener("click", generateSupplierPageOrder);
els.chatToggle?.addEventListener("click", openChat);
els.chatCloseBtn?.addEventListener("click", closeChat);
els.chatFullscreenBtn?.addEventListener("click", toggleChatFullscreen);
els.chatForm?.addEventListener("submit", askAI);
els.runAgentBtn?.addEventListener("click", runAgentFlow);

initApp().catch((error) => {
  if (els.headline) els.headline.textContent = "Backend bağlantısı yok.";
  if (els.dailySummary) els.dailySummary.textContent = "Backend'e bağlanılamadı. Önce backend sunucusunu çalıştırın: uvicorn main:app --reload";
  if (els.aiResult) els.aiResult.textContent = error.message;
});
