// CivicPulse signal detail page (signal.html?id=<source|date|title>).
//
// Shows one scraped signal with context — where it came from, what issue
// it covers, where it is — plus the link out to the original post/article.
// Links from feeds are built with signalUrl() in signals-data.js.

const params = new URLSearchParams(window.location.search);
const id = params.get("id") || "";

let signals = [];
let map = null;

function findRecord() {
  return signals.find((s) => signalKey(s) === id) || null;
}

function sourceLabel(source) {
  return SOURCE_LABELS[source] || source;
}

function categoryLabel(category) {
  return category.replaceAll("_", " ");
}

// ── header ──────────────────────────────────────────────

function renderHead(record) {
  document.title = `CivicPulse — ${record.title}`;

  const badges = document.getElementById("signalBadges");
  badges.innerHTML = "";
  const badge = document.createElement("a");
  badge.className = `source-badge ${record.source}`;
  badge.textContent = sourceLabel(record.source);
  badge.href = `source.html?source=${encodeURIComponent(record.source)}`;
  badge.title = `${sourceLabel(record.source)} analytics`;
  badges.appendChild(badge);
  for (const category of record.categories || []) {
    const tag = document.createElement("span");
    tag.className = "signal-tag";
    tag.textContent = categoryLabel(category);
    badges.appendChild(tag);
  }

  document.getElementById("signalTitle").textContent = record.title;
  document.getElementById("signalMeta").textContent =
    `${record.outlet} · ${record.published_utc}`;

  const open = document.getElementById("openOriginal");
  if (record.url) {
    open.hidden = false;
    open.href = record.url;
    open.textContent =
      record.source === "tiktok" ? "Watch on TikTok ↗" : "Open the original ↗";
  } else {
    open.hidden = true;
  }
}

// ── where it's from ─────────────────────────────────────

function infoRow(label, valueNode, linkHref, linkText) {
  const row = document.createElement("div");
  row.className = "info-row";

  const l = document.createElement("span");
  l.className = "info-label";
  l.textContent = label;

  const v = document.createElement("span");
  v.className = "info-value";
  v.append(valueNode);

  row.append(l, v);
  if (linkHref) {
    const a = document.createElement("a");
    a.className = "info-link";
    a.href = linkHref;
    a.textContent = linkText;
    row.appendChild(a);
  }
  return row;
}

function renderFrom(record) {
  const el = document.getElementById("fromBody");
  el.innerHTML = "";
  document.getElementById("fromPanel").hidden = false;

  const fromSource = signals.filter((s) => s.source === record.source);
  const share = signals.length
    ? Math.round((fromSource.length / signals.length) * 100)
    : 0;
  const fromOutlet = fromSource.filter((s) => s.outlet === record.outlet);

  const sourceValue = document.createElement("span");
  const badge = document.createElement("span");
  badge.className = `source-badge ${record.source}`;
  badge.textContent = sourceLabel(record.source);
  sourceValue.append(
    badge,
    ` ${fromSource.length} signal${fromSource.length === 1 ? "" : "s"} · ${share}% of all`
  );
  el.appendChild(
    infoRow(
      "Source",
      sourceValue,
      `source.html?source=${encodeURIComponent(record.source)}`,
      "View source analytics →"
    )
  );

  el.appendChild(
    infoRow(
      "Outlet",
      `${record.outlet} · ${fromOutlet.length} signal${fromOutlet.length === 1 ? "" : "s"}`,
      `source.html?source=${encodeURIComponent(record.source)}&outlet=${encodeURIComponent(record.outlet)}`,
      "View outlet analytics →"
    )
  );

  el.appendChild(infoRow("Published", record.published_utc));
}

// ── the issue ───────────────────────────────────────────

function renderIssue(record) {
  const el = document.getElementById("issueBody");
  el.innerHTML = "";
  document.getElementById("issuePanel").hidden = false;

  for (const category of record.categories || []) {
    const count = signals.filter((s) =>
      (s.categories || []).includes(category)
    ).length;

    const value = document.createElement("span");
    const dot = document.createElement("span");
    dot.className = "issue-dot";
    dot.style.background = CATEGORY_COLORS[category] || "#666";
    value.append(
      dot,
      ` ${categoryLabel(category)} · ${count} signal${count === 1 ? "" : "s"} across all sources`
    );

    el.appendChild(
      infoRow(
        "Issue",
        value,
        `source.html?issue=${encodeURIComponent(category)}`,
        `View ${categoryLabel(category)} analytics →`
      )
    );
  }

  if (record.body) {
    const body = document.createElement("p");
    body.className = "signal-body";
    body.textContent = record.body;
    el.appendChild(body);
  }
}

// ── location ────────────────────────────────────────────

function renderLocation(record) {
  const panel = document.getElementById("locationPanel");
  const { lat, lng, address } = record.metadata || {};
  if (lat == null || lng == null) {
    panel.hidden = true;
    return;
  }
  panel.hidden = false;
  document.getElementById("locationHint").textContent = address
    ? `📍 ${address}`
    : `${lat.toFixed(4)}, ${lng.toFixed(4)}`;

  if (map) {
    map.remove();
    map = null;
  }
  map = L.map("signalMap", { scrollWheelZoom: false }).setView([lat, lng], 14);
  L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 19,
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
  }).addTo(map);
  const icon = L.divIcon({ className: "civic-marker", html: "", iconSize: [16, 16] });
  const marker = L.marker([lat, lng], { icon }).addTo(map);
  marker.getElement().style.background =
    CATEGORY_COLORS[(record.categories || [])[0]] || "#666";
}

// ── related signals ─────────────────────────────────────

function renderRelated(record) {
  const panel = document.getElementById("relatedPanel");
  const el = document.getElementById("relatedList");
  el.innerHTML = "";

  const related = signals
    .filter(
      (s) =>
        signalKey(s) !== id &&
        (s.outlet === record.outlet ||
          (s.categories || []).some((c) => (record.categories || []).includes(c)))
    )
    .sort((a, b) => (b.published_utc || "").localeCompare(a.published_utc || ""))
    .slice(0, 4);

  if (related.length === 0) {
    panel.hidden = true;
    return;
  }
  panel.hidden = false;
  document.getElementById("relatedHint").textContent =
    "Same outlet or same issue";

  for (const rel of related) {
    const item = document.createElement("article");
    item.className = "feed-item";

    const top = document.createElement("div");
    top.className = "feed-top";
    const badge = document.createElement("a");
    badge.className = `source-badge ${rel.source}`;
    badge.textContent = sourceLabel(rel.source);
    badge.href = `source.html?source=${encodeURIComponent(rel.source)}`;
    top.appendChild(badge);
    for (const category of rel.categories || []) {
      const tag = document.createElement("span");
      tag.className = "tag";
      tag.textContent = categoryLabel(category);
      top.appendChild(tag);
    }

    const title = document.createElement("h3");
    const link = document.createElement("a");
    link.href = signalUrl(rel);
    link.textContent = rel.title;
    title.appendChild(link);

    const meta = document.createElement("p");
    meta.className = "meta";
    meta.textContent = `${rel.outlet} · ${rel.published_utc}`;

    item.append(top, title, meta);
    el.appendChild(item);
  }
}

// ── wiring ──────────────────────────────────────────────

function renderNotFound() {
  document.title = "CivicPulse — Signal not found";
  document.getElementById("signalTitle").textContent = "Signal not found";
  document.getElementById("signalMeta").textContent =
    "This signal isn't in the current data — it may have come from an older scrape.";
  document.getElementById("signalBadges").innerHTML = "";
  document.getElementById("openOriginal").hidden = true;
  for (const panelId of ["fromPanel", "issuePanel", "locationPanel", "relatedPanel"]) {
    document.getElementById(panelId).hidden = true;
  }
}

function render() {
  const record = findRecord();
  if (!record) {
    renderNotFound();
    return;
  }
  renderHead(record);
  renderFrom(record);
  renderIssue(record);
  renderLocation(record);
  renderRelated(record);
}

async function init() {
  signals = buildSignals(await fetchLiveSignals());
  render();
}

signals = buildSignals([]);
render();
init();
