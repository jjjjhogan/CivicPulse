// CivicPulse dashboard.
//
// Sample records follow the CivicSignal schema (scrapers/schema.py):
// { source, outlet, title, body, url, categories, published_utc, metadata }
// with optional metadata.lat / metadata.lng for map placement.
// When scripts/dashboard_server.py is running, live TikTok signals load from
// GET /api/signals and merge with sample news/reddit records below.

const SAMPLE_SIGNALS = [
  {
    source: "news",
    outlet: "Voice of OC",
    title: "Orange County's Growing E-bike Crackdown Continues Targeting Parents",
    url: "https://voiceofoc.org/2026/07/orange-countys-growing-e-bike-crackdown/",
    categories: ["public_safety"],
    published_utc: "2026-07-02",
    metadata: { lat: 33.6695, lng: -117.8231 },
  },
  {
    source: "tiktok",
    outlet: "@irvinemoms",
    title: "POV: the pothole on Culver ate my coffee again #irvine #potholes",
    url: "https://www.tiktok.com/@irvinemoms/video/7350000000000000001",
    categories: ["potholes"],
    published_utc: "2026-07-01",
    metadata: { lat: 33.6846, lng: -117.7998 },
  },
  {
    source: "news",
    outlet: "Irvine Standard",
    title: "No. 3 city in America to raise a family",
    url: "https://www.irvinestandard.com/2026/no-3-city-to-raise-a-family/",
    categories: ["public_safety"],
    published_utc: "2026-07-01",
    metadata: {},
  },
  {
    source: "reddit",
    outlet: "r/irvine",
    title: "Pothole on Culver and Alton has been there for a month now",
    url: "https://www.reddit.com/r/irvine/comments/pothole_culver_alton/",
    categories: ["potholes"],
    published_utc: "2026-06-30",
    metadata: { lat: 33.6603, lng: -117.8005 },
  },
  {
    source: "tiktok",
    outlet: "@ocpulsecheck",
    title: "Rent in Irvine just went up AGAIN — here's what residents told me",
    url: "https://www.tiktok.com/@ocpulsecheck/video/7350000000000000002",
    categories: ["housing"],
    published_utc: "2026-06-29",
    metadata: { lat: 33.6926, lng: -117.8352 },
  },
  {
    source: "news",
    outlet: "Voice of OC",
    title: "37 People Died 'Without Fixed Abode' in OC in May, the Highest Monthly Total in a Year",
    url: "https://voiceofoc.org/2026/06/37-people-died-without-fixed-abode/",
    categories: ["housing"],
    published_utc: "2026-06-28",
    metadata: {},
  },
  {
    source: "reddit",
    outlet: "r/irvine",
    title: "Construction noise starting before 7am near Woodbury — anyone else?",
    url: "https://www.reddit.com/r/irvine/comments/construction_noise_woodbury/",
    categories: ["noise"],
    published_utc: "2026-06-27",
    metadata: { lat: 33.7093, lng: -117.7411 },
  },
  {
    source: "tiktok",
    outlet: "@uciweekly",
    title: "Streetlights out near campus for 2 weeks — students walking home in the dark",
    url: "https://www.tiktok.com/@uciweekly/video/7350000000000000003",
    categories: ["public_safety"],
    published_utc: "2026-06-26",
    metadata: { lat: 33.6405, lng: -117.8443 },
  },
  {
    source: "news",
    outlet: "Irvine Weekly",
    title: "City council weighs new recycling and trash pickup schedule",
    url: "https://irvineweekly.com/city-council-recycling-trash-pickup/",
    categories: ["sanitation"],
    published_utc: "2026-06-25",
    metadata: { lat: 33.6784, lng: -117.7713 },
  },
  {
    source: "reddit",
    outlet: "r/irvine",
    title: "Illegal dumping behind the Northwood shopping plaza is getting worse",
    url: "https://www.reddit.com/r/irvine/comments/illegal_dumping_northwood/",
    categories: ["sanitation"],
    published_utc: "2026-06-24",
    metadata: { lat: 33.7152, lng: -117.7846 },
  },
];

// Mirrors CATEGORY_KEYWORDS in scrapers/categories.py — used so the keyword
// search also matches category keywords, not just words in the title.
const CATEGORY_KEYWORDS = {
  potholes: ["pothole", "road damage", "pavement crack", "street repair"],
  noise: ["noise complaint", "loud music", "construction noise", "loud neighbors"],
  sanitation: ["trash pickup", "garbage", "illegal dumping", "sanitation"],
  public_safety: ["break-in", "shooting", "assault", "streetlight out", "crime", "police"],
  housing: ["eviction", "rent increase", "affordable housing", "homeless", "housing crisis"],
};

const CATEGORY_COLORS = {
  potholes: "#b07a1e",
  noise: "#8a5fc9",
  sanitation: "#4c7a34",
  public_safety: "#c44f3f",
  housing: "#3a63c4",
};

const SOURCE_LABELS = { tiktok: "TikTok", news: "News", reddit: "Reddit", resident: "Resident" };

// Resident reports submitted through report.html (stored locally until a
// backend /api/reports endpoint exists).
const REPORTS_STORAGE_KEY = "civicpulse_resident_reports";

function loadResidentReports() {
  try {
    return JSON.parse(localStorage.getItem(REPORTS_STORAGE_KEY)) || [];
  } catch {
    return [];
  }
}

const SCRAPERS = [
  {
    id: "tiktok",
    name: "TikTok scraper",
    desc: "Selenium scraper for Irvine tags & comments (scripts/scrape_tiktok.py)",
  },
  {
    id: "irvine-news",
    name: "Irvine news scraper",
    desc: "Local outlets: Voice of OC, Irvine Standard, Irvine Weekly",
  },
  {
    id: "reddit",
    name: "Reddit scraper",
    desc: "r/irvine and r/orangecounty resident posts",
  },
];

const state = {
  signals: [...loadResidentReports(), ...SAMPLE_SIGNALS],
  selectedCategories: new Set(),
  keyword: "",
};

let map;
let markerLayer;

// ── filtering ───────────────────────────────────────────

function matchesFilters(signal) {
  if (state.selectedCategories.size > 0 &&
      !signal.categories.some((c) => state.selectedCategories.has(c))) {
    return false;
  }
  if (state.keyword) {
    const kw = state.keyword.toLowerCase();
    const inTitle = signal.title.toLowerCase().includes(kw);
    const inOutlet = signal.outlet.toLowerCase().includes(kw);
    const inCategoryKeywords = signal.categories.some((c) =>
      (CATEGORY_KEYWORDS[c] || []).some((k) => k.includes(kw))
    );
    if (!inTitle && !inOutlet && !inCategoryKeywords) return false;
  }
  return true;
}

function visibleSignals() {
  return state.signals.filter(matchesFilters);
}

// ── stats ───────────────────────────────────────────────

function renderStats() {
  const el = document.getElementById("dashStats");
  const total = state.signals.length;
  const tiktoks = state.signals.filter((s) => s.source === "tiktok").length;
  const articles = state.signals.filter((s) => s.source === "news").length;
  const reports = state.signals.filter((s) => s.source === "resident").length;
  el.innerHTML = "";
  for (const [num, label] of [[total, "signals"], [tiktoks, "tiktoks"], [articles, "articles"], [reports, "reports"]]) {
    const stat = document.createElement("div");
    stat.className = "stat";
    const n = document.createElement("span");
    n.className = "stat-num";
    n.textContent = num;
    const l = document.createElement("span");
    l.className = "stat-label";
    l.textContent = label;
    stat.append(n, l);
    el.appendChild(stat);
  }
}

// ── tag filters ─────────────────────────────────────────

function renderTagFilters() {
  const el = document.getElementById("tagFilters");
  el.innerHTML = "";
  for (const category of Object.keys(CATEGORY_KEYWORDS)) {
    const count = state.signals.filter((s) => s.categories.includes(category)).length;
    const btn = document.createElement("button");
    btn.className = "tag-filter" + (state.selectedCategories.has(category) ? " selected" : "");
    btn.innerHTML = `${category.replaceAll("_", " ")}<span class="count">${count}</span>`;
    btn.addEventListener("click", () => {
      if (state.selectedCategories.has(category)) {
        state.selectedCategories.delete(category);
      } else {
        state.selectedCategories.add(category);
      }
      render();
    });
    el.appendChild(btn);
  }
}

// ── feed ────────────────────────────────────────────────

function renderFeed() {
  const el = document.getElementById("signalFeed");
  const records = visibleSignals();
  document.getElementById("feedCount").textContent =
    `${records.length} of ${state.signals.length} signals`;
  el.innerHTML = "";

  if (records.length === 0) {
    const empty = document.createElement("p");
    empty.className = "feed-empty";
    empty.textContent = "No signals match the current filters.";
    el.appendChild(empty);
    return;
  }

  for (const record of records) {
    const item = document.createElement("article");
    item.className = "feed-item";

    const top = document.createElement("div");
    top.className = "feed-top";
    const badge = document.createElement("span");
    badge.className = `source-badge ${record.source}`;
    badge.textContent = SOURCE_LABELS[record.source] || record.source;
    top.appendChild(badge);
    for (const category of record.categories) {
      const tag = document.createElement("span");
      tag.className = "tag";
      tag.textContent = category.replaceAll("_", " ");
      top.appendChild(tag);
    }

    const title = document.createElement("h3");
    if (record.url) {
      const link = document.createElement("a");
      link.href = record.url;
      link.target = "_blank";
      link.rel = "noopener noreferrer";
      link.textContent = record.title;
      title.appendChild(link);
    } else {
      title.textContent = record.title;
    }

    const meta = document.createElement("p");
    meta.className = "meta";
    meta.textContent = `${record.outlet} · ${record.published_utc}`;
    if (record.url) {
      const open = document.createElement("a");
      open.href = record.url;
      open.target = "_blank";
      open.rel = "noopener noreferrer";
      open.textContent = record.source === "tiktok" ? "Watch on TikTok ↗" : "Open ↗";
      meta.append(" · ", open);
    }

    item.append(top, title, meta);
    el.appendChild(item);
  }
}

// ── map ─────────────────────────────────────────────────

const IRVINE_CENTER = [33.6846, -117.8265];

function initMap() {
  map = L.map("irvineMap", { scrollWheelZoom: false }).setView(IRVINE_CENTER, 12);
  L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 19,
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
  }).addTo(map);
  markerLayer = L.layerGroup().addTo(map);
  renderLegend();
}

function renderLegend() {
  const el = document.getElementById("mapLegend");
  el.innerHTML = "";
  for (const [category, color] of Object.entries(CATEGORY_COLORS)) {
    const item = document.createElement("span");
    item.className = "legend-item";
    const dot = document.createElement("span");
    dot.className = "legend-dot";
    dot.style.background = color;
    const label = document.createElement("span");
    label.textContent = category.replaceAll("_", " ");
    item.append(dot, label);
    el.appendChild(item);
  }
}

function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}

function renderMarkers() {
  markerLayer.clearLayers();
  for (const record of visibleSignals()) {
    const { lat, lng } = record.metadata || {};
    if (lat == null || lng == null) continue;
    const color = CATEGORY_COLORS[record.categories[0]] || "#666";
    const icon = L.divIcon({
      className: "civic-marker",
      html: "",
      iconSize: [16, 16],
    });
    const marker = L.marker([lat, lng], { icon }).addTo(markerLayer);
    marker.getElement().style.background = color;
    const link = record.url
      ? `<a href="${escapeHtml(record.url)}" target="_blank" rel="noopener noreferrer">Open source ↗</a>`
      : "";
    const address = record.metadata?.address
      ? `<div class="popup-meta">📍 ${escapeHtml(record.metadata.address)}</div>`
      : "";
    marker.bindPopup(
      `<div class="popup-title">${escapeHtml(record.title)}</div>
       <div class="popup-meta">${escapeHtml(record.outlet)} · ${escapeHtml(record.published_utc)}</div>${address}${link}`
    );
  }
}

// ── scraper panel ───────────────────────────────────────

function logLine(text) {
  const el = document.getElementById("scraperLog");
  el.hidden = false;
  const time = new Date().toLocaleTimeString();
  el.textContent += `[${time}] ${text}\n`;
  el.scrollTop = el.scrollHeight;
}

function mergeSignals(tiktokSignals) {
  const other = SAMPLE_SIGNALS.filter((s) => s.source !== "tiktok");
  if (!tiktokSignals.length) {
    state.signals = [...SAMPLE_SIGNALS];
    return;
  }
  state.signals = [...other, ...tiktokSignals];
}

async function loadSignals() {
  try {
    const res = await fetch("/api/signals");
    if (!res.ok) return;
    const data = await res.json();
    mergeSignals(data.signals || []);
  } catch {
    state.signals = [...SAMPLE_SIGNALS];
  }
}

async function pollScrapeStatus(statusEl) {
  const logEl = document.getElementById("scraperLog");
  while (true) {
    const res = await fetch("/api/scrape/status");
    const data = await res.json();
    if (data.log) {
      logEl.textContent = data.log;
      logEl.scrollTop = logEl.scrollHeight;
    }
    if (data.status === "completed") {
      statusEl.textContent = "Done";
      statusEl.className = "scraper-status done";
      return true;
    }
    if (data.status === "failed") {
      statusEl.textContent = "Failed";
      statusEl.className = "scraper-status failed";
      logLine(data.error || "Scrape failed.");
      return false;
    }
    await new Promise((r) => setTimeout(r, 1500));
  }
}

async function runScraper(scraper, statusEl, btn) {
  btn.disabled = true;
  statusEl.textContent = "Running…";
  statusEl.className = "scraper-status running";
  logLine(`Starting ${scraper.name}…`);

  try {
    const res = await fetch(`/api/scrape/${scraper.id}`, { method: "POST" });
    if (res.status === 501) {
      const body = await res.json();
      statusEl.textContent = "Not available";
      statusEl.className = "scraper-status";
      logLine(body.error || `${scraper.name} is not implemented yet.`);
      btn.disabled = false;
      return;
    }
    if (res.status === 409) {
      statusEl.textContent = "Busy";
      statusEl.className = "scraper-status";
      logLine("Another scrape is already running.");
      btn.disabled = false;
      return;
    }
    if (!res.ok) {
      const body = await res.json().catch(() => ({}));
      throw new Error(body.error || `API returned ${res.status}`);
    }

    const ok = await pollScrapeStatus(statusEl);
    if (ok) {
      await loadSignals();
      const count = state.signals.filter((s) => s.source === scraper.id).length;
      logLine(`${scraper.name} finished — ${count} signals in feed.`);
      render();
    }
  } catch {
    statusEl.textContent = "Offline";
    statusEl.className = "scraper-status";
    logLine(
      `${scraper.name} could not start — run python scripts/dashboard_server.py and try again.`
    );
  }

  btn.disabled = false;
}

function renderScrapers() {
  const el = document.getElementById("scraperGrid");
  for (const scraper of SCRAPERS) {
    const card = document.createElement("div");
    card.className = "scraper-card";

    const name = document.createElement("div");
    name.className = "scraper-name";
    name.textContent = scraper.name;

    const desc = document.createElement("div");
    desc.className = "scraper-desc";
    desc.textContent = scraper.desc;

    const row = document.createElement("div");
    row.className = "scraper-row";
    const status = document.createElement("span");
    status.className = "scraper-status";
    status.textContent = "Idle";
    const btn = document.createElement("button");
    btn.className = "btn btn-sm";
    btn.textContent = "Run";
    btn.addEventListener("click", () => runScraper(scraper, status, btn));
    row.append(status, btn);

    card.append(name, desc, row);
    el.appendChild(card);
  }
}

// ── wiring ──────────────────────────────────────────────

function render() {
  renderStats();
  renderTagFilters();
  renderFeed();
  renderMarkers();
}

document.getElementById("keywordSearch").addEventListener("input", (event) => {
  state.keyword = event.target.value.trim();
  renderFeed();
  renderMarkers();
});

document.getElementById("clearFilters").addEventListener("click", () => {
  state.selectedCategories.clear();
  state.keyword = "";
  document.getElementById("keywordSearch").value = "";
  render();
});

// ── sidebar active-section highlighting ────────────────

function initSidebar() {
  const links = [...document.querySelectorAll("#sidebarNav .side-link")];
  const sections = links
    .map((link) => document.querySelector(link.getAttribute("href")))
    .filter(Boolean);

  function setActive(id) {
    for (const link of links) {
      link.classList.toggle("active", link.getAttribute("href") === `#${id}`);
    }
  }

  const observer = new IntersectionObserver(
    (entries) => {
      const visible = entries
        .filter((e) => e.isIntersecting)
        .sort((a, b) => b.intersectionRatio - a.intersectionRatio);
      if (visible.length > 0) setActive(visible[0].target.id);
    },
    { rootMargin: "-20% 0px -55% 0px", threshold: [0, 0.25, 0.5] }
  );
  for (const section of sections) observer.observe(section);

  // Highlight immediately on click instead of waiting for the scroll.
  for (const link of links) {
    link.addEventListener("click", () => {
      setActive(link.getAttribute("href").slice(1));
    });
  }
}

initSidebar();
renderScrapers();
initMap();
loadSignals().then(render);
