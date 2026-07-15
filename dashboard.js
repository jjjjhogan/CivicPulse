// CivicPulse dashboard.
//
// Signal data, the CivicSignal schema notes, and shared helpers live in
// signals-data.js (loaded before this file).

const SCRAPERS = [
  {
    id: "tiktok",
    source: "tiktok",
    name: "TikTok scraper",
    desc: "Selenium scraper for Irvine tags & comments (scripts/scrape_tiktok.py)",
  },
  {
    id: "irvine-news",
    source: "news",
    name: "Irvine news scraper",
    desc: "Local outlets: Voice of OC, Irvine Standard, Irvine Weekly",
  },
  {
    id: "reddit",
    source: "reddit",
    name: "Reddit scraper",
    desc: "r/irvine and r/orangecounty resident posts",
  },
  {
    id: "twitter",
    source: "twitter",
    name: "Twitter scraper",
    desc: "X/Twitter search for Irvine civic posts (import via process_twitter_scrape.py)",
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
    const badge = document.createElement("a");
    badge.className = `source-badge ${record.source}`;
    badge.textContent = SOURCE_LABELS[record.source] || record.source;
    badge.href = `source.html?source=${encodeURIComponent(record.source)}`;
    badge.title = `${SOURCE_LABELS[record.source] || record.source} analytics`;
    top.appendChild(badge);
    for (const category of record.categories) {
      const tag = document.createElement("span");
      tag.className = "tag";
      tag.textContent = category.replaceAll("_", " ");
      top.appendChild(tag);
    }

    const title = document.createElement("h3");
    const link = document.createElement("a");
    link.href = signalUrl(record);
    link.textContent = record.title;
    title.appendChild(link);

    const meta = document.createElement("p");
    meta.className = "meta";
    meta.textContent = `${record.outlet} · ${record.published_utc}`;
    const open = document.createElement("a");
    open.href = signalUrl(record);
    open.textContent = "View signal →";
    meta.append(" · ", open);

    item.append(top, title, meta);
    el.appendChild(item);
  }
}

// ── sources ─────────────────────────────────────────────
// One card per source linking to its analytics page (source.html).

function renderSources() {
  const el = document.getElementById("sourceGrid");
  el.innerHTML = "";
  const total = state.signals.length;
  const counts = {};
  for (const signal of state.signals) {
    counts[signal.source] = (counts[signal.source] || 0) + 1;
  }
  const sources = [...new Set([...MAIN_SOURCES, ...Object.keys(counts)])];

  for (const source of sources) {
    const count = counts[source] || 0;
    const share = total ? Math.round((count / total) * 100) : 0;

    const card = document.createElement("a");
    card.className = "source-card";
    card.href = `source.html?source=${encodeURIComponent(source)}`;

    const badge = document.createElement("span");
    badge.className = `source-badge ${source}`;
    badge.textContent = SOURCE_LABELS[source] || source;

    const num = document.createElement("span");
    num.className = "source-count";
    num.textContent = count;

    const share_ = document.createElement("span");
    share_.className = "source-share";
    share_.textContent = `${share}% of all signals`;

    const open = document.createElement("span");
    open.className = "source-open";
    open.textContent = "View analytics →";

    card.append(badge, num, share_, open);
    el.appendChild(card);
  }
}

// ── verify issues ───────────────────────────────────────
// Residents vote on whether a reported issue is really there. Votes are
// stored locally per browser until a backend /api/votes endpoint exists.

const VOTES_STORAGE_KEY = "civicpulse_issue_votes";

function loadVotes() {
  try {
    return JSON.parse(localStorage.getItem(VOTES_STORAGE_KEY)) || {};
  } catch {
    return {};
  }
}

function saveVotes(votes) {
  localStorage.setItem(VOTES_STORAGE_KEY, JSON.stringify(votes));
}

// Resident reports have no id, so key votes on fields that identify one.
function reportKey(report) {
  const { lat, lng } = report.metadata || {};
  return `${report.title}|${report.published_utc}|${lat},${lng}`;
}

// Enough community confirmations — the issue is real and leaves the
// verification queue (it stays in the feed and on the map).
function isVerified(vote) {
  return vote.up >= 3 && vote.up > vote.down;
}

function castVote(key, choice) {
  const votes = loadVotes();
  const vote = votes[key] || { up: 0, down: 0, mine: null };
  if (vote.mine === choice) {
    vote[choice] -= 1;
    vote.mine = null;
  } else {
    if (vote.mine) vote[vote.mine] -= 1;
    vote[choice] += 1;
    vote.mine = choice;
  }
  votes[key] = vote;
  saveVotes(votes);
  renderVerify();
}

function renderVerify() {
  const el = document.getElementById("verifyList");
  const hint = document.getElementById("verifyHint");
  const reports = state.signals.filter((s) => s.source === "resident");
  el.innerHTML = "";

  if (reports.length === 0) {
    hint.textContent = "Vote on whether resident-reported issues are really there";
    const empty = document.createElement("p");
    empty.className = "feed-empty";
    empty.textContent = "No issues right now.";
    el.appendChild(empty);
    return;
  }

  // Verified issues leave the queue so it only holds open questions.
  const votes = loadVotes();
  const pending = reports.filter(
    (report) => !isVerified(votes[reportKey(report)] || { up: 0, down: 0 })
  );
  const verifiedCount = reports.length - pending.length;
  const verifiedNote = verifiedCount > 0
    ? ` · ${verifiedCount} verified and cleared`
    : "";

  if (pending.length === 0) {
    hint.textContent = `All caught up${verifiedNote}`;
    const empty = document.createElement("p");
    empty.className = "feed-empty";
    empty.textContent = "Every reported issue has been verified by the community.";
    el.appendChild(empty);
    return;
  }

  hint.textContent =
    `${pending.length} resident-reported issue${pending.length === 1 ? "" : "s"} awaiting verification${verifiedNote}`;

  for (const report of pending) {
    const key = reportKey(report);
    const vote = votes[key] || { up: 0, down: 0, mine: null };

    const card = document.createElement("article");
    card.className = "verify-card";

    const top = document.createElement("div");
    top.className = "feed-top";
    for (const category of report.categories) {
      const tag = document.createElement("span");
      tag.className = "tag";
      tag.textContent = category.replaceAll("_", " ");
      top.appendChild(tag);
    }

    const title = document.createElement("h3");
    title.className = "verify-title";
    title.textContent = report.title;

    const meta = document.createElement("p");
    meta.className = "verify-meta";
    const address = report.metadata?.address ? ` · 📍 ${report.metadata.address}` : "";
    meta.textContent = `${report.outlet} · ${report.published_utc}${address}`;

    card.append(top, title, meta);

    if (report.body) {
      const body = document.createElement("p");
      body.className = "verify-body";
      body.textContent = report.body;
      card.appendChild(body);
    }

    const row = document.createElement("div");
    row.className = "vote-row";

    const yesBtn = document.createElement("button");
    yesBtn.className = "vote-btn" + (vote.mine === "up" ? " voted-yes" : "");
    yesBtn.textContent = `👍 It's there (${vote.up})`;
    yesBtn.addEventListener("click", () => castVote(key, "up"));

    const noBtn = document.createElement("button");
    noBtn.className = "vote-btn" + (vote.mine === "down" ? " voted-no" : "");
    noBtn.textContent = `👎 Not there (${vote.down})`;
    noBtn.addEventListener("click", () => castVote(key, "down"));

    const voteHint = document.createElement("span");
    voteHint.className = "vote-hint";
    voteHint.textContent =
      vote.mine === null ? "Have you seen this issue?" : "Click again to remove your vote";

    row.append(yesBtn, noBtn, voteHint);
    card.appendChild(row);
    el.appendChild(card);
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
    const link = `<a href="${escapeHtml(signalUrl(record))}">View signal →</a>`;
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

function mergeSignals(liveSignals) {
  state.signals = buildSignals(liveSignals);
}

async function loadSignals() {
  mergeSignals(await fetchLiveSignals());
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

    const analytics = document.createElement("a");
    analytics.className = "scraper-analytics";
    analytics.href = `source.html?source=${encodeURIComponent(scraper.source)}`;
    analytics.textContent = "View analytics →";

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

    card.append(name, desc, analytics, row);
    el.appendChild(card);
  }
}

// ── wiring ──────────────────────────────────────────────

function render() {
  renderStats();
  renderSources();
  renderTagFilters();
  renderFeed();
  renderMarkers();
  renderVerify();
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
