const SCRAPERS = [
  { id: "tiktok", source: "tiktok", name: "TikTok scraper", desc: "Selenium scraper for Irvine tags & comments", signalSource: "tiktok" },
  { id: "irvine-news", source: "news", name: "Irvine news scraper", desc: "Local outlets: Voice of OC, Irvine Standard, Irvine Weekly", signalSource: "news" },
  { id: "reddit", source: "reddit", name: "Reddit import", desc: "Paste or upload a Reddit scrape JSON export", signalSource: "reddit" },
  { id: "twitter", source: "twitter", name: "Twitter import", desc: "Paste or upload a Twitter/X scrape JSON export", signalSource: "twitter" },
];

const state = {
  config: {
    tiktok_defaults: { tag_urls: ["https://www.tiktok.com/tag/irvine"], max_videos: 10, max_comments: 25 },
    news_defaults: { outlets: ["irvine-standard", "irvine-weekly", "voice-of-oc"], max_articles: 50, require_category_match: true },
    news_outlets: [],
  },
  scrapeRunning: false,
};

function logLine(text) {
  const el = document.getElementById("scraperLog");
  el.hidden = false;
  el.textContent += `[${new Date().toLocaleTimeString()}] ${text}\n`;
  el.scrollTop = el.scrollHeight;
}

function setRunButtonsDisabled(disabled) {
  state.scrapeRunning = disabled;
  document.querySelectorAll("[data-scraper-run]").forEach((btn) => { btn.disabled = disabled; });
}

function stripAnsi(text) {
  return (text || "").replace(/\u001b\[[0-9;]*m/g, "");
}

function readableJobFailure(job) {
  const lines = stripAnsi(job.log).split(/\r?\n/).map((line) => line.trim()).filter(Boolean);
  const detail = [...lines].reverse().find((line) => /error|exception|failed|traceback|invalid|not found/i.test(line)) || lines.at(-1) || "";
  return detail && !String(job.error || "").includes(detail) ? `${job.error || "Scrape failed."} — ${detail}` : (job.error || "Scrape failed.");
}

async function pollJobStatus(jobId, statusEl) {
  while (true) {
    const res = await fetch(`/api/jobs/${jobId}`, { credentials: "same-origin" });
    if (res.status === 401) return window.location.assign("login.html");
    if (!res.ok) throw new Error(`API returned ${res.status}`);
    const job = await res.json();
    if (job.log) {
      const log = document.getElementById("scraperLog");
      log.hidden = false;
      log.textContent = stripAnsi(job.log);
    }
    if (job.status === "completed") {
      statusEl.textContent = "Done";
      statusEl.className = "scraper-status done";
      return;
    }
    if (job.status === "failed") {
      const reason = readableJobFailure(job);
      statusEl.textContent = "Failed";
      statusEl.className = "scraper-status failed";
      statusEl.title = reason;
      logLine(`Job #${jobId} failed: ${reason}`);
      return;
    }
    await new Promise((resolve) => setTimeout(resolve, 1500));
  }
}

function buildField(labelText, input) {
  const field = document.createElement("label");
  field.className = "scraper-field";
  const label = document.createElement("span");
  label.className = "scraper-field-label";
  label.textContent = labelText;
  field.append(label, input);
  return field;
}

function renderTikTokSettings(card) {
  const defaults = state.config.tiktok_defaults;
  const settings = document.createElement("div");
  settings.className = "scraper-settings";
  const maxVideos = document.createElement("input");
  maxVideos.type = "number"; maxVideos.min = "1"; maxVideos.max = "50";
  maxVideos.value = String(defaults.max_videos ?? 10); maxVideos.dataset.field = "max_videos";
  const maxComments = document.createElement("input");
  maxComments.type = "number"; maxComments.min = "1"; maxComments.max = "200";
  maxComments.value = String(defaults.max_comments ?? 25); maxComments.dataset.field = "max_comments";
  const tags = document.createElement("textarea");
  tags.rows = 3; tags.dataset.field = "tag_urls"; tags.placeholder = "One TikTok tag URL per line";
  tags.value = (defaults.tag_urls || []).join("\n");
  const row = document.createElement("div");
  row.className = "scraper-fields-row";
  row.append(buildField("Max videos", maxVideos), buildField("Max comments", maxComments));
  settings.append(row, buildField("Tag URLs", tags));
  card.appendChild(settings);
}

function renderNewsSettings(card) {
  const defaults = state.config.news_defaults;
  const settings = document.createElement("div");
  settings.className = "scraper-settings";
  const outlets = document.createElement("div");
  outlets.className = "scraper-outlet-list";
  const selected = new Set(defaults.outlets || []);
  for (const outlet of state.config.news_outlets || []) {
    const row = document.createElement("label");
    row.className = "scraper-check";
    const input = document.createElement("input");
    input.type = "checkbox"; input.value = outlet.id; input.dataset.outlet = outlet.id;
    input.checked = selected.size === 0 || selected.has(outlet.id);
    row.append(input, document.createTextNode(outlet.name));
    outlets.appendChild(row);
  }
  const maxArticles = document.createElement("input");
  maxArticles.type = "number"; maxArticles.min = "1"; maxArticles.max = "200";
  maxArticles.value = String(defaults.max_articles ?? 50); maxArticles.dataset.field = "max_articles";
  const category = document.createElement("input");
  category.type = "checkbox"; category.dataset.field = "require_category";
  category.checked = defaults.require_category_match !== false;
  const categoryRow = document.createElement("label");
  categoryRow.className = "scraper-check";
  categoryRow.append(category, document.createTextNode(" Require civic category match"));
  settings.append(buildField("Outlets", outlets), buildField("Max articles", maxArticles), categoryRow);
  card.appendChild(settings);
}

function renderImportSettings(card, scraper) {
  const settings = document.createElement("div");
  settings.className = "scraper-settings";
  const paste = document.createElement("textarea");
  paste.rows = 5; paste.dataset.field = "paste";
  paste.placeholder = scraper.id === "reddit" ? 'Paste Reddit JSON or DevTools dump ({ "items": [...] })' : 'Paste Twitter JSON or DevTools dump ({ "tweets": [...] })';
  const file = document.createElement("input");
  file.type = "file"; file.accept = "application/json,.json"; file.dataset.field = "file";
  settings.append(buildField("Paste JSON", paste), buildField("Or upload .json", file));
  card.appendChild(settings);
}

function buildJobRequest(scraper, card) {
  if (scraper.id === "tiktok") {
    const defaults = state.config.tiktok_defaults;
    const tags = card.querySelector("[data-field=tag_urls]").value.split("\n").map((tag) => tag.trim()).filter(Boolean);
    return { body: JSON.stringify({ source: "tiktok", settings: { mode: "tags", tag_urls: tags, max_videos: Number(card.querySelector("[data-field=max_videos]").value) || defaults.max_videos, max_comments: Number(card.querySelector("[data-field=max_comments]").value) || defaults.max_comments } }), headers: { "Content-Type": "application/json" } };
  }
  if (scraper.id === "irvine-news") {
    return { body: JSON.stringify({ source: "irvine-news", settings: { outlets: [...card.querySelectorAll("[data-outlet]:checked")].map((input) => input.value), max_articles: Number(card.querySelector("[data-field=max_articles]").value) || state.config.news_defaults.max_articles, require_category_match: card.querySelector("[data-field=require_category]").checked } }), headers: { "Content-Type": "application/json" } };
  }
  const file = card.querySelector("[data-field=file]");
  const paste = card.querySelector("[data-field=paste]").value.trim();
  if (file.files.length) {
    const form = new FormData();
    form.append("source", scraper.id);
    form.append("file", file.files[0]);
    return { body: form };
  }
  if (!paste) throw new Error("Paste JSON (or a DevTools object dump) or choose a .json file first.");
  return { body: JSON.stringify({ source: scraper.id, settings: { payload: paste } }), headers: { "Content-Type": "application/json" } };
}

async function runScraper(scraper, card, status, button) {
  if (state.scrapeRunning) return;
  let request;
  try {
    request = buildJobRequest(scraper, card);
  } catch (error) {
    status.textContent = "Needs input";
    return logLine(error.message);
  }
  setRunButtonsDisabled(true);
  button.disabled = true;
  status.textContent = "Running…";
  status.className = "scraper-status running";
  try {
    const res = await fetch("/api/jobs", { method: "POST", credentials: "same-origin", body: request.body, headers: request.headers });
    if (res.status === 401) return window.location.assign("login.html");
    const body = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(body.error || `API returned ${res.status}`);
    logLine(`Job #${body.id} started.`);
    await pollJobStatus(body.id, status);
  } catch (error) {
    status.textContent = "Failed";
    status.className = "scraper-status failed";
    logLine(error.message || "Could not start scraper.");
  } finally {
    setRunButtonsDisabled(false);
  }
}

function renderScrapers() {
  const grid = document.getElementById("scraperGrid");
  for (const scraper of SCRAPERS) {
    const card = document.createElement("div");
    card.className = "scraper-card";
    card.dataset.scraper = scraper.id;
    const name = document.createElement("div");
    name.className = "scraper-name"; name.textContent = scraper.name;
    const desc = document.createElement("div");
    desc.className = "scraper-desc"; desc.textContent = scraper.desc;
    card.append(name, desc);
    if (scraper.id === "tiktok") renderTikTokSettings(card);
    else if (scraper.id === "irvine-news") renderNewsSettings(card);
    else renderImportSettings(card, scraper);
    const row = document.createElement("div");
    row.className = "scraper-row";
    const status = document.createElement("span");
    status.className = "scraper-status"; status.textContent = "Idle";
    const button = document.createElement("button");
    button.className = "btn btn-sm";
    button.textContent = ["reddit", "twitter"].includes(scraper.id) ? "Import" : "Run";
    button.dataset.scraperRun = scraper.id;
    button.addEventListener("click", () => runScraper(scraper, card, status, button));
    row.append(status, button);
    card.appendChild(row);
    grid.appendChild(card);
  }
}

async function start() {
  const sessionRes = await fetch("/api/auth/me", { credentials: "same-origin" });
  const session = await sessionRes.json();
  if (!session.authenticated) return window.location.assign("login.html");
  if (!session.scrapers_allowed) return window.location.assign("dashboard.html");
  const scrapersNav = document.getElementById("scrapersNav");
  if (scrapersNav) scrapersNav.hidden = false;
  document.getElementById("signedInUser").textContent = session.user.name || session.user.email;
  document.getElementById("signedInUser").hidden = false;
  document.getElementById("logoutBtn").addEventListener("click", async (event) => {
    event.preventDefault();
    await fetch("/api/auth/logout", { method: "POST", credentials: "same-origin" });
    window.location.assign("login.html");
  });
  const configRes = await fetch("/api/config");
  if (configRes.ok) {
    const config = await configRes.json();
    state.config = { ...state.config, ...config };
  }
  renderScrapers();
}

start().catch(() => window.location.assign("dashboard.html"));
