// CivicPulse dashboard.
//
// Signal data, the CivicSignal schema notes, and shared helpers live in
// signals-data.js (loaded before this file).

// Feed items rendered per page; "Show more" reveals the next batch.
const FEED_PAGE_SIZE = 20;

const state = {
  signals: buildSignals([]),
  selectedCategories: new Set(),
  keyword: "",
  feedShown: FEED_PAGE_SIZE,
  user: null,
  // Where the signal list came from: "loading" until the first fetch
  // resolves, then "live", "empty" (API up, nothing scraped yet),
  // "error" (API returned non-OK), or "offline" (unreachable — samples).
  live: "loading",
};

function signalsUnavailable() {
  return state.live === "offline" || state.live === "error";
}

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
    const inBody = (signal.body || "").toLowerCase().includes(kw);
    const inOutlet = signal.outlet.toLowerCase().includes(kw);
    const inCategoryKeywords = signal.categories.some((c) =>
      (CATEGORY_KEYWORDS[c] || []).some((k) => k.includes(kw))
    );
    if (!inTitle && !inBody && !inOutlet && !inCategoryKeywords) return false;
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
    btn.innerHTML =
      `<span class="tag-dot" style="background:${CATEGORY_COLORS[category] || "#666"}"></span>` +
      `${category.replaceAll("_", " ")}<span class="count">${count}</span>`;
    btn.addEventListener("click", () => {
      if (state.selectedCategories.has(category)) {
        state.selectedCategories.delete(category);
      } else {
        state.selectedCategories.add(category);
      }
      state.feedShown = FEED_PAGE_SIZE;
      render();
    });
    el.appendChild(btn);
  }
}

// ── feed ────────────────────────────────────────────────

// One-line banner above the feed when the list isn't real live data.
function feedNotice() {
  if (state.live === "loading") {
    return null; // placeholder is already showing
  }
  if (state.live === "offline") {
    return "Couldn't reach the signals API — showing sample data. Start the server and refresh.";
  }
  if (state.live === "error") {
    return "The signals API returned an error — showing sample data. Check the server and refresh.";
  }
  if (state.live === "empty") {
    return "No signals scraped yet — showing sample data. Run a scraper above to populate the feed.";
  }
  return null;
}

function renderFeed() {
  const el = document.getElementById("signalFeed");
  const records = [...visibleSignals()].sort((a, b) =>
    (b.published_utc || "").localeCompare(a.published_utc || "")
  );
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

  for (const record of records.slice(0, state.feedShown)) {
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
    if (record.metadata?.lat != null && record.metadata?.lng != null) {
      const pin = document.createElement("button");
      pin.type = "button";
      pin.className = "pin-link";
      pin.textContent = "📍 map";
      pin.title = "Show this signal on the map";
      pin.addEventListener("click", () => focusOnMap(record));
      top.appendChild(pin);
    }

    const title = document.createElement("h3");
    const link = document.createElement("a");
    link.href = signalUrl(record);
    link.textContent = record.title;
    title.appendChild(link);

    const meta = buildSignalMeta(record);
    const open = document.createElement("a");
    open.href = signalUrl(record);
    open.textContent = "View signal →";
    meta.append(" · ", open);

    item.append(top, title, meta);
    el.appendChild(item);
  }

  const remaining = records.length - state.feedShown;
  if (remaining > 0) {
    const wrap = document.createElement("div");
    wrap.className = "feed-more";
    const btn = document.createElement("button");
    btn.className = "btn btn-sm";
    btn.textContent = `Show ${Math.min(FEED_PAGE_SIZE, remaining)} more (${remaining} left)`;
    btn.addEventListener("click", () => {
      state.feedShown += FEED_PAGE_SIZE;
      renderFeed();
    });
    wrap.appendChild(btn);
    el.appendChild(wrap);
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
// Community votes on whether a resident-reported issue is really there.
// Tallies live in SQLite via /api/votes (per logged-in user).

let voteState = {}; // { [signalId]: { up, down, mine } }

function reportVoteKey(report) {
  if (report.id != null) return String(report.id);
  const { lat, lng } = report.metadata || {};
  return `${report.title}|${report.published_utc}|${lat},${lng}`;
}

function isVerified(vote) {
  return vote.up >= 3 && vote.up > vote.down;
}

let votesLoadFailed = false;

async function loadVotesFromServer() {
  try {
    const res = await fetch("/api/votes", { credentials: "same-origin" });
    if (!res.ok) {
      votesLoadFailed = true;
      return;
    }
    const data = await res.json();
    voteState = data.votes || {};
    votesLoadFailed = false;
  } catch {
    votesLoadFailed = true;
  }
}

async function castVote(report, choice) {
  const signalId = report.id;
  if (signalId == null) {
    logLine("This report has no server id yet — reopen the dashboard after submitting via /api/reports.");
    return;
  }
  try {
    const res = await fetch("/api/votes", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "same-origin",
      body: JSON.stringify({ signal_id: signalId, choice }),
    });
    if (res.status === 401) {
      logLine("Log in to vote on resident reports.");
      return;
    }
    if (!res.ok) {
      const data = await res.json().catch(() => ({}));
      logLine(data.error || "Vote failed.");
      return;
    }
    const data = await res.json();
    voteState[String(signalId)] = {
      up: data.up || 0,
      down: data.down || 0,
      mine: data.mine ?? null,
    };
    renderVerify();
  } catch (err) {
    logLine(err.message || "Vote failed.");
  }
}

function renderVerify() {
  const el = document.getElementById("verifyList");
  const hint = document.getElementById("verifyHint");
  const reports = state.signals.filter((s) => s.source === "resident");
  el.innerHTML = "";

  if (signalsUnavailable()) {
    hint.textContent = "Vote on whether resident-reported issues are really there";
    const msg = document.createElement("p");
    msg.className = "feed-empty";
    msg.textContent =
      state.live === "error"
        ? "Can't load resident reports — the signals API returned an error."
        : "Can't load resident reports — the server is offline.";
    el.appendChild(msg);
    return;
  }

  if (reports.length === 0) {
    hint.textContent = "Vote on whether resident-reported issues are really there";
    const empty = document.createElement("p");
    empty.className = "feed-empty";
    empty.textContent = "No resident reports yet — submit one from the report page.";
    const link = document.createElement("a");
    link.href = "report.html";
    link.className = "verify-report-link";
    link.textContent = "Report an issue →";
    el.append(empty, link);
    return;
  }

  if (votesLoadFailed) {
    const note = document.createElement("p");
    note.className = "feed-notice";
    note.textContent = "Vote tallies couldn't be loaded — totals may be out of date.";
    el.appendChild(note);
  }

  const pending = reports.filter(
    (report) => !isVerified(voteState[reportVoteKey(report)] || { up: 0, down: 0 })
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
    const key = reportVoteKey(report);
    const vote = voteState[key] || { up: 0, down: 0, mine: null };

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
    yesBtn.addEventListener("click", () => castVote(report, "up"));

    const noBtn = document.createElement("button");
    noBtn.className = "vote-btn" + (vote.mine === "down" ? " voted-no" : "");
    noBtn.textContent = `👎 Not there (${vote.down})`;
    noBtn.addEventListener("click", () => castVote(report, "down"));

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

// Markers keyed by signalKey() so feed cards can jump to their marker.
const markersByKey = new Map();

function renderMarkers() {
  markerLayer.clearLayers();
  markersByKey.clear();
  const mapOverlay = document.getElementById("mapOverlay");
  const geoSignals = visibleSignals().filter(
    (r) => r.metadata?.lat != null && r.metadata?.lng != null
  );

  if (signalsUnavailable()) {
    if (mapOverlay) {
      mapOverlay.textContent =
        state.live === "error"
          ? "Map data unavailable — the signals API returned an error."
          : "Map data unavailable — the signals API is offline.";
      mapOverlay.hidden = false;
    }
    return;
  }
  if (geoSignals.length === 0) {
    if (mapOverlay) {
      mapOverlay.textContent =
        state.live === "empty"
          ? "No signals with locations yet — run a scraper or submit a report to populate the map."
          : "No signals match the current filters, or none have location data.";
      mapOverlay.hidden = false;
    }
    return;
  }
  if (mapOverlay) mapOverlay.hidden = true;

  for (const record of geoSignals) {
    const { lat, lng } = record.metadata;
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
    markersByKey.set(signalKey(record), marker);
  }
}

// Jump from a feed card to its marker: scroll the map into view, pan to
// the signal, and open its popup.
function focusOnMap(record) {
  const marker = markersByKey.get(signalKey(record));
  if (!marker) return;
  document.getElementById("map").scrollIntoView({ behavior: "smooth", block: "center" });
  // No animation: openPopup()'s auto-pan would cancel an animated setView.
  map.setView(marker.getLatLng(), 15, { animate: false });
  marker.openPopup();
}

function logLine(text) {
  console.info(`[CivicPulse] ${text}`);
}

function mergeSignals(liveSignals) {
  state.signals = buildSignals(liveSignals);
}

async function loadSignals() {
  const migrated = await migrateLocalReportsToServer();
  if (migrated > 0) {
    logLine(`Migrated ${migrated} local resident report(s) into SQLite.`);
  }
  const { signals, storage, status } = await fetchLiveSignalsResult();
  mergeSignals(signals);
  state.live = status || "offline";
  await loadVotesFromServer();
  renderVerify();
  if (storage === "db") {
    logLine(`Loaded ${signals.length} signals from SQLite.`);
  } else if (storage === "json") {
    logLine(
      `Loaded ${signals.length} signals from JSON fallback (run import_signals.py to use SQLite).`
    );
  } else if (state.live === "empty") {
    logLine("API is up but returned no signals — showing sample / resident data.");
  } else if (state.live === "error") {
    logLine("Signals API returned an error — showing sample / resident data.");
  } else if (state.live === "offline") {
    logLine("Couldn't reach the signals API — showing sample / resident data.");
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

const searchInput = document.getElementById("keywordSearch");
const searchClear = document.getElementById("searchClear");
let searchTimer;

function applyKeyword(value) {
  state.keyword = value.trim();
  state.feedShown = FEED_PAGE_SIZE;
  searchClear.hidden = state.keyword === "";
  renderFeed();
  renderMarkers();
}

// Debounced so a 120-item feed isn't re-rendered on every keystroke.
searchInput.addEventListener("input", (event) => {
  clearTimeout(searchTimer);
  searchTimer = setTimeout(() => applyKeyword(event.target.value), 200);
});

searchClear.addEventListener("click", () => {
  searchInput.value = "";
  applyKeyword("");
  searchInput.focus();
});

document.getElementById("clearFilters").addEventListener("click", () => {
  state.selectedCategories.clear();
  state.keyword = "";
  state.feedShown = FEED_PAGE_SIZE;
  searchInput.value = "";
  searchClear.hidden = true;
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
    // API unhealthy but reachable: stay on the dashboard so feed/map/verify
    // can show their own error states instead of bouncing to login.
    if (!res.ok) {
      return {
        user: { name: "Unavailable", offline: true },
        scrapers_allowed: false,
        scrapers_host_ok: false,
      };
    }
    const data = await res.json();
    if (!data.authenticated) {
      window.location.href = "login.html";
      return null;
    }
    return data;
  } catch {
    // Server unreachable (e.g. dashboard_server stopped) — stay put so
    // panels can explain the outage rather than redirecting to login.
    return {
      user: { name: "Offline", offline: true },
      scrapers_allowed: false,
      scrapers_host_ok: false,
    };
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
requireAuth().then((session) => {
  if (!session) return;
  const user = session.user;
  showSignedInUser(user);
  const scrapersNav = document.getElementById("scrapersNav");
  if (scrapersNav) scrapersNav.hidden = !session.scrapers_allowed;
  if (user.offline) {
    return loadSignals().then(render);
  }
  const logoutBtn = document.getElementById("logoutBtn");
  if (logoutBtn) logoutBtn.addEventListener("click", (event) => {
    event.preventDefault();
    logout();
  });
  return loadSignals().then(render);
});
