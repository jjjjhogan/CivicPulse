// CivicPulse source analytics page (source.html?source=tiktok).
//
// Shows per-source stats computed from the same signal list the dashboard
// uses: resident reports from localStorage + sample records, with live
// scraper data merged in when the Flask backend is running.

// ?source=tiktok or ?source=tiktok,reddit — any mix of sources.
// An empty selection means all sources combined.
const params = new URLSearchParams(window.location.search);
const selectedSources = new Set(
  (params.get("source") || "")
    .toLowerCase()
    .split(",")
    .map((s) => s.trim())
    .filter(Boolean)
);

let signals = [];

// ?issue=potholes or ?issue=potholes,noise — pre-selected issue filters.
const selectedCategories = new Set(
  (params.get("issue") || "")
    .toLowerCase()
    .split(",")
    .map((s) => s.trim())
    .filter(Boolean)
);

// ?outlet=@irvinemoms — drill into one account/outlet's scraped data.
let selectedOutlet = params.get("outlet") || null;

// ?conf=high,low — classifier confidence bands (see confidenceBand()).
const selectedBands = new Set(
  (params.get("conf") || "")
    .toLowerCase()
    .split(",")
    .map((s) => s.trim())
    .filter((band) => band in CONFIDENCE_BANDS)
);

// ?missed=1 — only "missed stories" the keyword pass dropped and the
// model pass rescued.
let missedOnly = params.get("missed") === "1";

function sourceLabel(source) {
  return SOURCE_LABELS[source] || source;
}

function sourceSignals() {
  if (selectedSources.size === 0) return [...signals];
  return signals.filter((s) => selectedSources.has(s.source));
}

function matchesCategories(signal) {
  return (
    selectedCategories.size === 0 ||
    (signal.categories || []).some((c) => selectedCategories.has(c))
  );
}

function matchesConfidence(signal) {
  return selectedBands.size === 0 || selectedBands.has(confidenceBand(signal));
}

// Source signals narrowed to the selected issue, outlet, confidence, and
// missed-story filters.
function filteredSignals() {
  return sourceSignals().filter(
    (s) =>
      matchesCategories(s) &&
      (!selectedOutlet || s.outlet === selectedOutlet) &&
      matchesConfidence(s) &&
      (!missedOnly || isRescuedSignal(s))
  );
}

function syncUrl() {
  const query = new URLSearchParams();
  if (selectedSources.size > 0) {
    query.set("source", [...selectedSources].join(","));
  }
  if (selectedCategories.size > 0) {
    query.set("issue", [...selectedCategories].join(","));
  }
  if (selectedOutlet) query.set("outlet", selectedOutlet);
  if (selectedBands.size > 0) {
    query.set("conf", [...selectedBands].join(","));
  }
  if (missedOnly) query.set("missed", "1");
  const qs = query.toString();
  history.replaceState(null, "", qs ? `source.html?${qs}` : "source.html");
}

function toggleSource(source) {
  if (selectedSources.has(source)) {
    selectedSources.delete(source);
  } else {
    selectedSources.add(source);
  }
  syncUrl();
  render();
}

function toggleOutlet(outlet) {
  selectedOutlet = selectedOutlet === outlet ? null : outlet;
  syncUrl();
  render();
}

// ── filter bar ──────────────────────────────────────────

function allSources() {
  const present = new Set(signals.map((s) => s.source));
  return [...new Set([...MAIN_SOURCES, ...present, ...selectedSources])];
}

function renderFilters() {
  const sourceEl = document.getElementById("sourceFilters");
  sourceEl.innerHTML = "";
  for (const source of allSources()) {
    const count = signals.filter((s) => s.source === source).length;
    const btn = document.createElement("button");
    btn.className = "tag-filter" + (selectedSources.has(source) ? " selected" : "");
    btn.innerHTML = `${sourceLabel(source)}<span class="count">${count}</span>`;
    btn.addEventListener("click", () => toggleSource(source));
    sourceEl.appendChild(btn);
  }

  const issueEl = document.getElementById("issueFilters");
  issueEl.innerHTML = "";
  for (const category of Object.keys(CATEGORY_KEYWORDS)) {
    const count = sourceSignals().filter((s) =>
      (s.categories || []).includes(category)
    ).length;
    const btn = document.createElement("button");
    btn.className = "tag-filter" + (selectedCategories.has(category) ? " selected" : "");
    btn.innerHTML = `${category.replaceAll("_", " ")}<span class="count">${count}</span>`;
    btn.addEventListener("click", () => {
      if (selectedCategories.has(category)) {
        selectedCategories.delete(category);
      } else {
        selectedCategories.add(category);
      }
      syncUrl();
      render();
    });
    issueEl.appendChild(btn);
  }

  const confEl = document.getElementById("confFilters");
  confEl.innerHTML = "";
  for (const [band, meta] of Object.entries(CONFIDENCE_BANDS)) {
    const count = sourceSignals().filter((s) => confidenceBand(s) === band).length;
    const btn = document.createElement("button");
    btn.className = "tag-filter" + (selectedBands.has(band) ? " selected" : "");
    btn.innerHTML = `<span class="conf-dot ${band}"></span>${meta.label}<span class="count">${count}</span>`;
    btn.addEventListener("click", () => {
      if (selectedBands.has(band)) {
        selectedBands.delete(band);
      } else {
        selectedBands.add(band);
      }
      syncUrl();
      render();
    });
    confEl.appendChild(btn);
  }

  // Missed stories: signals the keyword pass dropped, rescued by the model.
  const missedEl = document.getElementById("missedFilter");
  missedEl.innerHTML = "";
  const missedCount = sourceSignals().filter(isRescuedSignal).length;
  const missedBtn = document.createElement("button");
  missedBtn.className = "tag-filter missed-filter" + (missedOnly ? " selected" : "");
  missedBtn.innerHTML = `Missed stories<span class="count">${missedCount}</span>`;
  missedBtn.title = "Signals the keyword filter would have dropped — caught by the model pass";
  missedBtn.addEventListener("click", () => {
    missedOnly = !missedOnly;
    syncUrl();
    render();
  });
  missedEl.appendChild(missedBtn);

  // The outlet row only appears while drilled into one outlet.
  const outletRow = document.getElementById("outletFilterRow");
  const outletEl = document.getElementById("outletFilter");
  outletEl.innerHTML = "";
  outletRow.hidden = !selectedOutlet;
  if (selectedOutlet) {
    const count = sourceSignals().filter((s) => s.outlet === selectedOutlet).length;
    const btn = document.createElement("button");
    btn.className = "tag-filter selected";
    btn.innerHTML = `${escapeText(selectedOutlet)}<span class="count">${count}</span> ✕`;
    btn.addEventListener("click", () => toggleOutlet(selectedOutlet));
    outletEl.appendChild(btn);
  }
}

function escapeText(text) {
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}

// ── sidebar: one link per source ────────────────────────

function renderNav() {
  const el = document.getElementById("sourceNav");
  el.innerHTML = "";
  const counts = {};
  for (const signal of signals) {
    counts[signal.source] = (counts[signal.source] || 0) + 1;
  }

  const all = document.createElement("a");
  all.className = "side-link" + (selectedSources.size === 0 ? " active" : "");
  all.href = "source.html";
  const allDot = document.createElement("span");
  allDot.className = "side-source-dot";
  const allCount = document.createElement("span");
  allCount.className = "side-count";
  allCount.textContent = signals.length;
  all.append(allDot, "All sources", allCount);
  el.appendChild(all);

  for (const source of allSources()) {
    const link = document.createElement("a");
    link.className = "side-link" + (selectedSources.has(source) ? " active" : "");
    link.href = `source.html?source=${encodeURIComponent(source)}`;

    const dot = document.createElement("span");
    dot.className = `side-source-dot ${source}`;

    const count = document.createElement("span");
    count.className = "side-count";
    count.textContent = counts[source] || 0;

    link.append(dot, sourceLabel(source), count);
    el.appendChild(link);
  }
}

// ── header stats ────────────────────────────────────────

function renderHead() {
  const records = filteredSignals();
  const chosen = [...selectedSources];
  const label = chosen.length === 0
    ? "All sources"
    : chosen.map(sourceLabel).join(" + ");
  document.title = `CivicPulse — ${label} analytics`;

  const title = document.getElementById("sourceTitle");
  title.innerHTML = "";
  title.append(`${label} analytics`);
  for (const source of chosen) {
    const badge = document.createElement("span");
    badge.className = `source-badge head-badge ${source}`;
    badge.textContent = sourceLabel(source);
    title.append(" ", badge);
  }

  const share = signals.length
    ? Math.round((records.length / signals.length) * 100)
    : 0;
  const mapped = records.filter(
    (s) => s.metadata?.lat != null && s.metadata?.lng != null
  ).length;
  const outlets = new Set(records.map((s) => s.outlet)).size;

  let sub = chosen.length === 0
    ? "Signals from every source combined — categories, timing, and outlets."
    : `How ${label} signals contribute to the Irvine civic picture — categories, timing, and outlets.`;
  if (selectedOutlet) sub += ` Drilled into ${selectedOutlet}.`;
  document.getElementById("sourceSub").textContent = sub;

  const scored = records
    .map(signalConfidence)
    .filter((confidence) => confidence != null);
  const avgConfidence = scored.length
    ? `${Math.round((scored.reduce((a, b) => a + b, 0) / scored.length) * 100)}%`
    : "—";

  const el = document.getElementById("sourceStats");
  el.innerHTML = "";
  for (const [num, statLabel] of [
    [records.length, "signals"],
    [`${share}%`, "of all signals"],
    [mapped, "on the map"],
    [outlets, "outlets"],
    [avgConfidence, "avg confidence"],
  ]) {
    const stat = document.createElement("div");
    stat.className = "stat";
    const n = document.createElement("span");
    n.className = "stat-num";
    n.textContent = num;
    const l = document.createElement("span");
    l.className = "stat-label";
    l.textContent = statLabel;
    stat.append(n, l);
    el.appendChild(stat);
  }
}

// ── category breakdown ──────────────────────────────────

function renderCategories() {
  const el = document.getElementById("categoryBars");
  // Respect the outlet drill-down but not the issue filters, so all
  // category bars stay comparable.
  const records = sourceSignals().filter(
    (s) => !selectedOutlet || s.outlet === selectedOutlet
  );
  el.innerHTML = "";

  const counts = {};
  for (const category of Object.keys(CATEGORY_KEYWORDS)) counts[category] = 0;
  for (const record of records) {
    for (const category of record.categories || []) {
      counts[category] = (counts[category] || 0) + 1;
    }
  }
  const max = Math.max(1, ...Object.values(counts));

  document.getElementById("categoryHint").textContent =
    `Across ${records.length} signal${records.length === 1 ? "" : "s"}`;

  for (const [category, count] of Object.entries(counts)) {
    const row = document.createElement("div");
    row.className = "cat-row";
    if (selectedCategories.size > 0 && !selectedCategories.has(category)) {
      row.classList.add("cat-dimmed");
    }

    const label = document.createElement("span");
    label.className = "cat-label";
    label.textContent = category.replaceAll("_", " ");

    const track = document.createElement("div");
    track.className = "cat-track";
    const fill = document.createElement("div");
    fill.className = "cat-fill";
    fill.style.width = `${(count / max) * 100}%`;
    fill.style.background = CATEGORY_COLORS[category] || "#666";
    track.appendChild(fill);

    const num = document.createElement("span");
    num.className = "cat-count";
    num.textContent = count;

    row.append(label, track, num);
    el.appendChild(row);
  }
}

// ── signals over time ───────────────────────────────────

function renderTimeline() {
  const el = document.getElementById("timelineChart");
  el.innerHTML = "";

  const byDay = new Map();
  for (const record of filteredSignals()) {
    const day = (record.published_utc || "").slice(0, 10);
    if (!day) continue;
    byDay.set(day, (byDay.get(day) || 0) + 1);
  }
  const days = [...byDay.entries()].sort((a, b) => a[0].localeCompare(b[0]));

  if (days.length === 0) {
    const empty = document.createElement("p");
    empty.className = "feed-empty";
    empty.textContent = "No dated signals match the current selection.";
    el.appendChild(empty);
    return;
  }

  const max = Math.max(...days.map(([, count]) => count));
  for (const [day, count] of days) {
    const col = document.createElement("div");
    col.className = "tl-col";

    const num = document.createElement("span");
    num.className = "tl-count";
    num.textContent = count;

    const bar = document.createElement("div");
    bar.className = "tl-bar";
    bar.style.height = `${Math.max(6, (count / max) * 110)}px`;
    bar.title = `${day} — ${count} signal${count === 1 ? "" : "s"}`;

    const date = document.createElement("span");
    date.className = "tl-date";
    date.textContent = day.slice(5); // MM-DD

    col.append(num, bar, date);
    el.appendChild(col);
  }
}

// ── top outlets ─────────────────────────────────────────

function renderOutlets() {
  const el = document.getElementById("outletList");
  el.innerHTML = "";

  // Respect the issue filters but not the outlet drill-down, so the other
  // outlets stay visible (dimmed) while one is selected.
  const counts = {};
  for (const record of sourceSignals().filter(matchesCategories)) {
    counts[record.outlet] = (counts[record.outlet] || 0) + 1;
  }
  const outlets = Object.entries(counts).sort((a, b) => b[1] - a[1]);
  const top = outlets.slice(0, 8);

  document.getElementById("outletHint").textContent = selectedOutlet
    ? `Showing ${selectedOutlet} — click it again to clear`
    : (outlets.length > top.length
        ? `Top ${top.length} of ${outlets.length} outlets — click one to drill in`
        : `${outlets.length} outlet${outlets.length === 1 ? "" : "s"} — click one to drill in`);

  if (top.length === 0) {
    const empty = document.createElement("p");
    empty.className = "feed-empty";
    empty.textContent = "No outlets match the current selection.";
    el.appendChild(empty);
    return;
  }

  const max = top[0][1];
  for (const [outlet, count] of top) {
    const row = document.createElement("button");
    row.className = "outlet-row";
    if (selectedOutlet === outlet) row.classList.add("outlet-selected");
    if (selectedOutlet && selectedOutlet !== outlet) row.classList.add("outlet-dimmed");
    row.title = `View analytics for ${outlet}`;
    row.addEventListener("click", () => toggleOutlet(outlet));

    const name = document.createElement("span");
    name.className = "outlet-name";
    name.textContent = outlet;

    const track = document.createElement("div");
    track.className = "cat-track";
    const fill = document.createElement("div");
    fill.className = "cat-fill outlet-fill";
    fill.style.width = `${(count / max) * 100}%`;
    track.appendChild(fill);

    const num = document.createElement("span");
    num.className = "cat-count";
    num.textContent = count;

    row.append(name, track, num);
    el.appendChild(row);
  }
}

// ── signal list ─────────────────────────────────────────

function renderList() {
  const el = document.getElementById("signalList");
  const records = [...filteredSignals()].sort((a, b) =>
    (b.published_utc || "").localeCompare(a.published_utc || "")
  );
  const all = sourceSignals().length;
  document.getElementById("listHint").textContent =
    selectedCategories.size > 0 || selectedOutlet || selectedBands.size > 0 || missedOnly
      ? `${records.length} of ${all} signals, newest first`
      : `${records.length} signal${records.length === 1 ? "" : "s"}, newest first`;
  el.innerHTML = "";

  if (records.length === 0) {
    const empty = document.createElement("p");
    empty.className = "feed-empty";
    empty.textContent = "No signals match the current selection.";
    el.appendChild(empty);
    return;
  }

  // With several sources mixed together, badge each signal with its source.
  const multiSource = selectedSources.size !== 1;

  for (const record of records) {
    const item = document.createElement("article");
    item.className = "feed-item";

    const top = document.createElement("div");
    top.className = "feed-top";
    if (multiSource) {
      const badge = document.createElement("a");
      badge.className = `source-badge ${record.source}`;
      badge.textContent = sourceLabel(record.source);
      badge.href = `source.html?source=${encodeURIComponent(record.source)}`;
      badge.title = `${sourceLabel(record.source)} analytics`;
      top.appendChild(badge);
    }
    for (const category of record.categories || []) {
      const tag = document.createElement("span");
      tag.className = "tag";
      tag.textContent = category.replaceAll("_", " ");
      top.appendChild(tag);
    }
    if (record.metadata?.lat != null && record.metadata?.lng != null) {
      const pin = document.createElement("span");
      pin.className = "pin-badge";
      pin.textContent = "📍 on the map";
      top.appendChild(pin);
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

// ── wiring ──────────────────────────────────────────────

function render() {
  renderNav();
  renderHead();
  renderFilters();
  renderCategories();
  renderTimeline();
  renderOutlets();
  renderList();
}

document.getElementById("clearIssueFilters").addEventListener("click", () => {
  selectedCategories.clear();
  selectedSources.clear();
  selectedOutlet = null;
  selectedBands.clear();
  missedOnly = false;
  syncUrl();
  render();
});

async function init() {
  signals = buildSignals(await fetchLiveSignals());
  render();
}

signals = buildSignals([]);
render();
init();
