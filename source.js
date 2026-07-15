// CivicPulse source analytics page (source.html?source=tiktok).
//
// Shows per-source stats computed from the same signal list the dashboard
// uses: resident reports from localStorage + sample records, with live
// scraper data merged in when the Flask backend is running.

const params = new URLSearchParams(window.location.search);
const currentSource = (params.get("source") || "tiktok").toLowerCase();

let signals = [];

function sourceLabel(source) {
  return SOURCE_LABELS[source] || source;
}

function sourceSignals() {
  return signals.filter((s) => s.source === currentSource);
}

// ── sidebar: one link per source ────────────────────────

function renderNav() {
  const el = document.getElementById("sourceNav");
  el.innerHTML = "";
  const counts = {};
  for (const signal of signals) {
    counts[signal.source] = (counts[signal.source] || 0) + 1;
  }
  const sources = [...new Set([...MAIN_SOURCES, ...Object.keys(counts), currentSource])];

  for (const source of sources) {
    const link = document.createElement("a");
    link.className = "side-link" + (source === currentSource ? " active" : "");
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
  const records = sourceSignals();
  const label = sourceLabel(currentSource);
  document.title = `CivicPulse — ${label} analytics`;

  const title = document.getElementById("sourceTitle");
  title.innerHTML = "";
  const badge = document.createElement("span");
  badge.className = `source-badge head-badge ${currentSource}`;
  badge.textContent = label;
  title.append(`${label} analytics `, badge);

  const share = signals.length
    ? Math.round((records.length / signals.length) * 100)
    : 0;
  const mapped = records.filter(
    (s) => s.metadata?.lat != null && s.metadata?.lng != null
  ).length;
  const outlets = new Set(records.map((s) => s.outlet)).size;

  document.getElementById("sourceSub").textContent =
    `How ${label} signals contribute to the Irvine civic picture — categories, timing, and outlets.`;

  const el = document.getElementById("sourceStats");
  el.innerHTML = "";
  for (const [num, statLabel] of [
    [records.length, "signals"],
    [`${share}%`, "of all signals"],
    [mapped, "on the map"],
    [outlets, "outlets"],
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
  const records = sourceSignals();
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
  for (const record of sourceSignals()) {
    const day = (record.published_utc || "").slice(0, 10);
    if (!day) continue;
    byDay.set(day, (byDay.get(day) || 0) + 1);
  }
  const days = [...byDay.entries()].sort((a, b) => a[0].localeCompare(b[0]));

  if (days.length === 0) {
    const empty = document.createElement("p");
    empty.className = "feed-empty";
    empty.textContent = "No dated signals for this source yet.";
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

  const counts = {};
  for (const record of sourceSignals()) {
    counts[record.outlet] = (counts[record.outlet] || 0) + 1;
  }
  const outlets = Object.entries(counts).sort((a, b) => b[1] - a[1]);
  const top = outlets.slice(0, 8);

  document.getElementById("outletHint").textContent = outlets.length > top.length
    ? `Top ${top.length} of ${outlets.length} outlets`
    : `${outlets.length} outlet${outlets.length === 1 ? "" : "s"}`;

  if (top.length === 0) {
    const empty = document.createElement("p");
    empty.className = "feed-empty";
    empty.textContent = "No outlets for this source yet.";
    el.appendChild(empty);
    return;
  }

  const max = top[0][1];
  for (const [outlet, count] of top) {
    const row = document.createElement("div");
    row.className = "outlet-row";

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
  const records = [...sourceSignals()].sort((a, b) =>
    (b.published_utc || "").localeCompare(a.published_utc || "")
  );
  document.getElementById("listHint").textContent =
    `${records.length} signal${records.length === 1 ? "" : "s"}, newest first`;
  el.innerHTML = "";

  if (records.length === 0) {
    const empty = document.createElement("p");
    empty.className = "feed-empty";
    empty.textContent = "No signals from this source yet.";
    el.appendChild(empty);
    return;
  }

  for (const record of records) {
    const item = document.createElement("article");
    item.className = "feed-item";

    const top = document.createElement("div");
    top.className = "feed-top";
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

// ── wiring ──────────────────────────────────────────────

function render() {
  renderNav();
  renderHead();
  renderCategories();
  renderTimeline();
  renderOutlets();
  renderList();
}

async function init() {
  signals = buildSignals(await fetchLiveSignals());
  render();
}

signals = buildSignals([]);
render();
init();
