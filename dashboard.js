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
    signalSource: "tiktok",
  },
  {
    id: "irvine-news",
    source: "news",
    name: "Irvine news scraper",
    desc: "Local outlets: Voice of OC, Irvine Standard, Irvine Weekly",
    signalSource: "news",
  },
  {
    id: "reddit",
    source: "reddit",
    name: "Reddit import",
    desc: "Paste or upload a Reddit scrape JSON export, then process into signals",
    signalSource: "reddit",
  },
  {
    id: "twitter",
    source: "twitter",
    name: "Twitter import",
    desc: "Paste or upload a Twitter/X scrape JSON export, then process into signals",
    signalSource: "twitter",
  },
];

const state = {
  signals: buildSignals([]),
  selectedCategories: new Set(),
  keyword: "",
  config: {
    tiktok_defaults: {
      tag_urls: [
        "https://www.tiktok.com/tag/irvine",
        "https://www.tiktok.com/tag/newportbeach",
      ],
      max_videos: 10,
      max_comments: 25,
    },
    news_defaults: {
      outlets: ["irvine-standard", "irvine-weekly", "voice-of-oc"],
      max_articles: 50,
      require_category_match: true,
    },
    news_outlets: [
      { id: "irvine-standard", name: "Irvine Standard" },
      { id: "irvine-weekly", name: "Irvine Weekly" },
      { id: "voice-of-oc", name: "Voice of OC" },
    ],
  },
  scrapeRunning: false,
  activeJobId: null,
  user: null,
  // Where the signal list came from: "loading" until the first fetch
  // resolves, then "live", "empty" (API up, nothing scraped yet), or
  // "offline" (API unreachable — samples stand in).
  live: "loading",
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

// One-line banner above the feed when the list isn't real live data.
function feedNotice() {
  if (state.live === "offline") {
    return "Couldn't reach the live signals API — showing sample data. Start the server with: python scripts/dashboard_server.py";
  }
  if (state.live === "empty") {
    return "No live signals yet — showing sample data. Run a scraper above to populate the feed.";
  }
  return null;
}

function renderFeed() {
  const el = document.getElementById("signalFeed");
  const records = visibleSignals();
  document.getElementById("feedCount").textContent =
    `${records.length} of ${state.signals.length} signals`;
  el.innerHTML = "";

  const notice = feedNotice();
  if (notice) {
    const note = document.createElement("p");
    note.className = "feed-notice";
    note.textContent = notice;
    el.appendChild(note);
  }

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
    appendClassificationBadges(top, record);

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
  const live = await fetchLiveSignals();
  state.live = live == null ? "offline" : live.length ? "live" : "empty";
  mergeSignals(live);
}

async function loadScraperConfig() {
  try {
    const res = await fetch("/api/config");
    if (!res.ok) return;
    const data = await res.json();
    state.config = {
      ...state.config,
      ...data,
      tiktok_defaults: {
        ...state.config.tiktok_defaults,
        ...(data.tiktok_defaults || {}),
      },
      news_defaults: {
        ...state.config.news_defaults,
        ...(data.news_defaults || {}),
      },
      news_outlets: data.news_outlets || state.config.news_outlets,
    };
  } catch {
    // Keep offline defaults.
  }
}

function setRunButtonsDisabled(disabled) {
  state.scrapeRunning = disabled;
  for (const btn of document.querySelectorAll("[data-scraper-run]")) {
    btn.disabled = disabled;
  }
}

// Python colorizes tracebacks with ANSI escapes; strip them for the browser.
function stripAnsi(text) {
  return (text || "").replace(/\u001b\[[0-9;]*m/g, "");
}

// Pull the most informative line out of a failed job's output so the log
// reads like a sentence, not just "exited with code 1".
function readableJobFailure(data) {
  const lines = stripAnsi(data.log)
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter(Boolean);
  const errorLine = [...lines]
    .reverse()
    .find((line) => /error|exception|failed|traceback|invalid|not found/i.test(line));
  const detail = errorLine || lines[lines.length - 1] || "";
  const base = data.error || "Scrape failed.";
  return detail && !base.includes(detail) ? `${base} — ${detail}` : base;
}

async function pollJobStatus(jobId, statusEl) {
  const logEl = document.getElementById("scraperLog");
  let misses = 0;
  while (true) {
    let data;
    try {
      const res = await fetch(`/api/jobs/${jobId}`, { credentials: "same-origin" });
      if (res.status === 401) {
        window.location.href = "login.html";
        return false;
      }
      if (!res.ok) throw new Error(`API returned ${res.status}`);
      data = await res.json();
      misses = 0;
    } catch {
      // A transient blip shouldn't kill the poll, but after ~15s of
      // silence stop with an honest message instead of spinning forever.
      misses += 1;
      if (misses >= 6) {
        statusEl.textContent = "Unknown";
        statusEl.className = "scraper-status error";
        logLine(
          `Lost contact with the server while job #${jobId} was running — refresh the page to check on it.`
        );
        return false;
      }
      await new Promise((r) => setTimeout(r, 2500));
      continue;
    }
    if (data.log) {
      logEl.hidden = false;
      logEl.textContent = stripAnsi(data.log);
      logEl.scrollTop = logEl.scrollHeight;
    }
    if (data.status === "completed") {
      statusEl.textContent = "Done";
      statusEl.className = "scraper-status done";
      return true;
    }
    if (data.status === "failed") {
      const reason = readableJobFailure(data);
      statusEl.textContent = "Failed";
      statusEl.className = "scraper-status failed";
      statusEl.title = reason;
      logLine(`Job #${jobId} failed: ${reason}`);
      return false;
    }
    await new Promise((r) => setTimeout(r, 1500));
  }
}

function collectTikTokPayload(card) {
  const maxVideos = Number(card.querySelector("[data-field=max_videos]").value);
  const maxComments = Number(card.querySelector("[data-field=max_comments]").value);
  const tagUrls = card
    .querySelector("[data-field=tag_urls]")
    .value.split("\n")
    .map((line) => line.trim())
    .filter(Boolean);
  return {
    mode: "tags",
    max_videos: Number.isFinite(maxVideos) ? maxVideos : state.config.tiktok_defaults.max_videos,
    max_comments: Number.isFinite(maxComments)
      ? maxComments
      : state.config.tiktok_defaults.max_comments,
    tag_urls: tagUrls,
  };
}

function collectNewsPayload(card) {
  const outlets = [...card.querySelectorAll("[data-outlet]:checked")].map(
    (input) => input.value
  );
  const maxArticles = Number(card.querySelector("[data-field=max_articles]").value);
  const requireCategory = card.querySelector("[data-field=require_category]").checked;
  return {
    outlets,
    max_articles: Number.isFinite(maxArticles)
      ? maxArticles
      : state.config.news_defaults.max_articles,
    require_category_match: requireCategory,
  };
}

async function buildJobRequest(scraper, card) {
  if (scraper.id === "tiktok") {
    return {
      body: JSON.stringify({ source: "tiktok", settings: collectTikTokPayload(card) }),
      headers: { "Content-Type": "application/json" },
    };
  }
  if (scraper.id === "irvine-news") {
    return {
      body: JSON.stringify({
        source: "irvine-news",
        settings: collectNewsPayload(card),
      }),
      headers: { "Content-Type": "application/json" },
    };
  }
  if (scraper.id === "reddit" || scraper.id === "twitter") {
    const fileInput = card.querySelector("[data-field=file]");
    const paste = (card.querySelector("[data-field=paste]").value || "").trim();
    if (fileInput?.files?.length) {
      const form = new FormData();
      form.append("source", scraper.id);
      form.append("file", fileInput.files[0]);
      return { body: form, isForm: true };
    }
    if (!paste) {
      throw new Error("Paste JSON or choose a .json file first.");
    }
    let parsed;
    try {
      parsed = JSON.parse(paste);
    } catch {
      throw new Error("Pasted text is not valid JSON.");
    }
    return {
      body: JSON.stringify({
        source: scraper.id,
        settings: { payload: parsed },
      }),
      headers: { "Content-Type": "application/json" },
    };
  }
  return { body: null };
}

async function runScraper(scraper, card, statusEl, btn) {
  if (state.scrapeRunning) {
    statusEl.textContent = "Busy";
    logLine("Another scrape is already running.");
    return;
  }

  let request;
  try {
    request = await buildJobRequest(scraper, card);
  } catch (err) {
    statusEl.textContent = "Needs input";
    statusEl.className = "scraper-status";
    logLine(err.message || String(err));
    return;
  }

  setRunButtonsDisabled(true);
  btn.disabled = true;
  statusEl.textContent = "Running…";
  statusEl.className = "scraper-status running";
  logLine(`Starting ${scraper.name}…`);

  try {
    const res = await fetch("/api/jobs", {
      method: "POST",
      credentials: "same-origin",
      body: request.body,
      headers: request.headers,
    });
    if (res.status === 401) {
      window.location.href = "login.html";
      return;
    }
    if (res.status === 501) {
      const body = await res.json();
      statusEl.textContent = "Not available";
      statusEl.className = "scraper-status";
      logLine(body.error || `${scraper.name} is not implemented yet.`);
      setRunButtonsDisabled(false);
      return;
    }
    if (res.status === 409) {
      statusEl.textContent = "Busy";
      statusEl.className = "scraper-status";
      logLine("Another scrape is already running.");
      setRunButtonsDisabled(false);
      return;
    }
    if (!res.ok) {
      const body = await res.json().catch(() => ({}));
      throw new Error(body.error || `API returned ${res.status}`);
    }

    const started = await res.json();
    logLine(`Job #${started.id} started.`);
    const ok = await pollJobStatus(started.id, statusEl);
    if (ok) {
      await loadSignals();
      const source = scraper.signalSource || scraper.id;
      const count = state.signals.filter((s) => s.source === source).length;
      logLine(`${scraper.name} finished — ${count} ${source} signals loaded.`);
      render();
    }
  } catch (err) {
    statusEl.textContent = "Offline";
    statusEl.className = "scraper-status";
    logLine(
      err?.message && !String(err.message).includes("Failed to fetch")
        ? err.message
        : `${scraper.name} could not start — run python scripts/dashboard_server.py and try again.`
    );
  }

  setRunButtonsDisabled(false);
}

function buildField(labelText, input) {
  const wrap = document.createElement("label");
  wrap.className = "scraper-field";
  const label = document.createElement("span");
  label.className = "scraper-field-label";
  label.textContent = labelText;
  wrap.append(label, input);
  return wrap;
}

function renderTikTokSettings(card) {
  const defaults = state.config.tiktok_defaults;
  const settings = document.createElement("div");
  settings.className = "scraper-settings";

  const maxVideos = document.createElement("input");
  maxVideos.type = "number";
  maxVideos.min = "1";
  maxVideos.max = "50";
  maxVideos.value = String(defaults.max_videos ?? 10);
  maxVideos.dataset.field = "max_videos";

  const maxComments = document.createElement("input");
  maxComments.type = "number";
  maxComments.min = "1";
  maxComments.max = "200";
  maxComments.value = String(defaults.max_comments ?? 25);
  maxComments.dataset.field = "max_comments";

  const nums = document.createElement("div");
  nums.className = "scraper-fields-row";
  nums.append(
    buildField("Max videos", maxVideos),
    buildField("Max comments", maxComments)
  );

  const tags = document.createElement("textarea");
  tags.rows = 3;
  tags.dataset.field = "tag_urls";
  tags.placeholder = "One TikTok tag URL per line";
  tags.value = (defaults.tag_urls || []).join("\n");

  settings.append(nums, buildField("Tag URLs", tags));
  card.appendChild(settings);
}

function renderNewsSettings(card) {
  const defaults = state.config.news_defaults;
  const outlets = state.config.news_outlets || [];
  const settings = document.createElement("div");
  settings.className = "scraper-settings";

  const outletList = document.createElement("div");
  outletList.className = "scraper-outlet-list";
  const selected = new Set(defaults.outlets || []);
  for (const outlet of outlets) {
    const row = document.createElement("label");
    row.className = "scraper-check";
    const input = document.createElement("input");
    input.type = "checkbox";
    input.value = outlet.id;
    input.dataset.outlet = outlet.id;
    input.checked = selected.size === 0 || selected.has(outlet.id);
    const text = document.createElement("span");
    text.textContent = outlet.name;
    row.append(input, text);
    outletList.appendChild(row);
  }

  const maxArticles = document.createElement("input");
  maxArticles.type = "number";
  maxArticles.min = "1";
  maxArticles.max = "200";
  maxArticles.value = String(defaults.max_articles ?? 50);
  maxArticles.dataset.field = "max_articles";

  const requireCategory = document.createElement("label");
  requireCategory.className = "scraper-check";
  const requireInput = document.createElement("input");
  requireInput.type = "checkbox";
  requireInput.dataset.field = "require_category";
  requireInput.checked = defaults.require_category_match !== false;
  const requireText = document.createElement("span");
  requireText.textContent = "Require civic category match";
  requireCategory.append(requireInput, requireText);

  settings.append(
    buildField("Outlets", outletList),
    buildField("Max articles", maxArticles),
    requireCategory
  );
  card.appendChild(settings);
}

function renderImportSettings(card, scraper) {
  const settings = document.createElement("div");
  settings.className = "scraper-settings";

  const paste = document.createElement("textarea");
  paste.rows = 5;
  paste.dataset.field = "paste";
  paste.placeholder =
    scraper.id === "reddit"
      ? 'Paste Reddit scrape JSON ({ "items": [...] } or nested scrapes)'
      : 'Paste Twitter scrape JSON ({ "tweets": [...] })';

  const file = document.createElement("input");
  file.type = "file";
  file.accept = "application/json,.json";
  file.dataset.field = "file";

  settings.append(
    buildField("Paste JSON", paste),
    buildField("Or upload .json", file)
  );
  card.appendChild(settings);
}

function renderScrapers() {
  const el = document.getElementById("scraperGrid");
  el.innerHTML = "";
  for (const scraper of SCRAPERS) {
    const card = document.createElement("div");
    card.className = "scraper-card";
    card.dataset.scraper = scraper.id;

    const name = document.createElement("div");
    name.className = "scraper-name";
    name.textContent = scraper.name;

    const desc = document.createElement("div");
    desc.className = "scraper-desc";
    desc.textContent = scraper.desc;

    const analytics = document.createElement("a");
    analytics.className = "scraper-analytics";
    analytics.href = `source.html?source=${encodeURIComponent(scraper.source || scraper.signalSource || scraper.id)}`;
    analytics.textContent = "View analytics →";

    card.append(name, desc, analytics);

    if (scraper.id === "tiktok") renderTikTokSettings(card);
    else if (scraper.id === "irvine-news") renderNewsSettings(card);
    else if (scraper.id === "reddit" || scraper.id === "twitter") {
      renderImportSettings(card, scraper);
    }

    const row = document.createElement("div");
    row.className = "scraper-row";
    const status = document.createElement("span");
    status.className = "scraper-status";
    status.textContent = "Idle";
    const btn = document.createElement("button");
    btn.className = "btn btn-sm";
    btn.textContent = scraper.id === "reddit" || scraper.id === "twitter" ? "Import" : "Run";
    btn.dataset.scraperRun = scraper.id;
    btn.addEventListener("click", () => runScraper(scraper, card, status, btn));
    row.append(status, btn);

    card.appendChild(row);
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

async function requireAuth() {
  try {
    const res = await fetch("/api/auth/me", { credentials: "same-origin" });
    const data = await res.json();
    if (!data.authenticated) {
      window.location.href = "login.html";
      return null;
    }
    return data.user;
  } catch {
    window.location.href = "login.html";
    return null;
  }
}

async function logout() {
  try {
    await fetch("/api/auth/logout", {
      method: "POST",
      credentials: "same-origin",
      headers: { Accept: "application/json" },
    });
  } catch {
    // Still leave the dashboard.
  }
  window.location.href = "login.html";
}

function showSignedInUser(user) {
  const el = document.getElementById("signedInUser");
  if (el && user) {
    el.textContent = user.name || user.email;
    el.hidden = false;
  }
}

// Shown between page load and the first successful signals fetch, so the
// feed isn't just blank while auth + data requests are in flight.
function renderLoadingPlaceholder() {
  document.getElementById("feedCount").textContent = "loading…";
  const el = document.getElementById("signalFeed");
  el.innerHTML = "";
  const p = document.createElement("p");
  p.className = "feed-empty";
  p.textContent = "Loading signals…";
  el.appendChild(p);
}

initSidebar();
initMap();
renderLoadingPlaceholder();
requireAuth().then((user) => {
  if (!user) return;
  showSignedInUser(user);
  const logoutBtn = document.getElementById("logoutBtn");
  if (logoutBtn) logoutBtn.addEventListener("click", (event) => {
    event.preventDefault();
    logout();
  });
  return loadScraperConfig()
    .then(() => {
      renderScrapers();
      return loadSignals();
    })
    .then(render);
});
