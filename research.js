/* research.js — compose UI + list researches */

(function () {
  var API = "/api/researches";
  var allItems = [];
  var activeFilter = "all";
  var configData = null;
  var expansionTimer = null;
  var customKeywords = [];
  var selectedExpansions = new Set();
  var expansionMeta = [];

  var LISTEN_SOURCES = [
    { id: "news311", title: "Local news + 311 logs", blurb: "Outlets and service requests", on: true, ready: true },
    { id: "tiktok", title: "TikTok comments", blurb: "Short-form city talk (desktop only)", on: true, ready: true },
    { id: "twitter", title: "X / Twitter", blurb: "Public posts and civic hashtags", on: true, ready: false },
    { id: "reddit", title: "Reddit", blurb: "Local subs and housing threads", on: true, ready: false },
    { id: "youtube", title: "YouTube comments", blurb: "Council streams and news clips", on: true, ready: false },
    { id: "facebook", title: "Facebook public groups", blurb: "Public groups only — no DMs", on: false, ready: false },
  ];

  var EXTRACT_OPTIONS = [
    { id: "sentiment", title: "Sentiment & emotion", blurb: "Supportive / mixed / critical — joy, fear, anger, resignation", on: true },
    { id: "clustering", title: "Narrative clustering", blurb: "Group thousands of posts into the 5–20 stories people tell", on: true },
    { id: "demographics", title: "Voice demographics", blurb: "Renter / owner, parent / non-parent, age band — inferred + flagged", on: true },
    { id: "policy", title: "Policy asks extraction", blurb: "Auto-extract concrete things residents want done", on: true },
    { id: "misinfo", title: "Misinformation flags", blurb: "Claims rebuttable by city data or news fact-checks", on: false },
    { id: "bots", title: "Bot & brigading detection", blurb: "Filter coordinated inauthentic activity from real voices", on: false },
  ];

  var VOICE_EXTRAS = {
    housing: ["can't afford rent", "priced out", "airbnb listings", "landlord issues"],
    potholes: ["car bottomed out", "street never fixed", "detour forever"],
    noise: ["can't sleep", "leaf blowers at 7am", "party next door"],
    sanitation: ["missed pickup", "rats in the alley", "overflowing bins"],
    public_safety: ["streetlight out", "don't walk at night", "more patrols"],
    violent_crime: ["shots fired", "unsafe after dark"],
    property_crime: ["package theft", "catalytic converter"],
    traffic_safety: ["speeding on my street", "need a crosswalk"],
    emergencies: ["flooded garage", "evacuation route"],
    immigration: ["ice rumor", "know your rights"],
  };

  var TEMPLATES = [
    { id: "housing", title: "Housing pulse", blurb: "Rent, zoning, evictions", fill: "Affordable housing supply and rent burden — what residents, landlords, and prospective buyers are actually saying." },
    { id: "transit", title: "Transit & mobility", blurb: "Bus, bike lanes, parking", fill: "Transit and mobility — bus reliability, bike lanes, parking, and how people actually get around Irvine." },
    { id: "climate", title: "Climate & parks", blurb: "Trees, flooding, green space", fill: "Climate and parks — trees, flooding, heat, and whether green space feels usable and safe." },
    { id: "safety", title: "Public safety", blurb: "Crime, policing, lighting", fill: "Public safety — crime, policing, lighting, and whether neighborhoods feel walkable after dark." },
  ];

  var listEl = document.getElementById("researchList");
  var emptyMsg = document.getElementById("emptyMsg");
  var listCount = document.getElementById("listCount");
  var formMsg = document.getElementById("formMsg");
  var filterBar = document.getElementById("filterBar");
  var titleEl = document.getElementById("fieldTitle");
  var pillsEl = document.getElementById("expansionPills");
  var expansionsHint = document.getElementById("expansionsHint");
  var customKwRow = document.getElementById("customKwRow");
  var customKwInput = document.getElementById("customKwInput");

  function esc(s) {
    var el = document.createElement("span");
    el.textContent = s;
    return el.innerHTML;
  }

  function sourceState() {
    return LISTEN_SOURCES.filter(function (s) { return s.on; }).map(function (s) { return s.id; });
  }

  function extractState() {
    return EXTRACT_OPTIONS.filter(function (s) { return s.on; }).map(function (s) { return s.id; });
  }

  function selectedKeywordList() {
    var kws = expansionMeta
      .filter(function (item) { return selectedExpansions.has(item.key); })
      .map(function (item) { return item.label; });
    customKeywords.forEach(function (k) {
      if (kws.indexOf(k) === -1) kws.push(k);
    });
    return kws;
  }

  function inferredCategories() {
    var cats = {};
    expansionMeta.forEach(function (item) {
      if (selectedExpansions.has(item.key) && item.category) cats[item.category] = true;
    });
    return Object.keys(cats);
  }

  function topicClarity(text) {
    var t = (text || "").trim();
    if (!t) return 0;
    var score = Math.min(40, Math.round(t.length / 2.2));
    if (t.length >= 40) score += 18;
    if (t.length >= 80) score += 10;
    if (/[?]/.test(t) || /\b(what|how|why|who)\b/i.test(t)) score += 8;
    if (inferredCategories().length || expansionMeta.length) score += 16;
    if (/\b(irvine|zip|east|west|north|south|district|neighborhood)\b/i.test(t)) score += 8;
    return Math.max(0, Math.min(99, score));
  }

  function updateClarity() {
    var pct = topicClarity(titleEl.value);
    document.getElementById("clarityBadge").textContent = "Topic clarity score — " + pct + "%";
  }

  function updateMetrics() {
    var totalSignals = (configData && configData.signal_count) || 0;
    var bySource = (configData && configData.signals_by_source) || {};
    var enabledSources = sourceState();

    var sourceMap = { news311: ["irvine-news", "news"], tiktok: ["tiktok"], twitter: ["twitter"], reddit: ["reddit"], youtube: ["youtube"], facebook: ["facebook"] };
    var archiveHits = 0;
    enabledSources.forEach(function (src) {
      (sourceMap[src] || [src]).forEach(function (key) {
        archiveHits += bySource[key] || 0;
      });
    });

    var windowMul = { "7d": 0.35, "30d": 1, "90d": 2.4, ytd: 3.1 };
    var mul = windowMul[document.getElementById("fieldTimeWindow").value] || 1;
    var voices = Math.round(archiveHits * mul);
    var coverage = totalSignals > 0
      ? Math.min(99, Math.round((archiveHits / totalSignals) * 100))
      : 0;
    var readySources = enabledSources.filter(function (s) {
      return LISTEN_SOURCES.some(function (ls) { return ls.id === s && ls.ready; });
    });
    var insight = readySources.length >= 2 ? "~6 min after launch" : readySources.length ? "~12 min after launch" : "Archive only";
    var refresh = document.getElementById("fieldTimeWindow").value === "7d"
      ? "Every 30 min + spike alerts"
      : "Hourly + live spike alerts";

    document.getElementById("metricVoices").textContent =
      voices.toLocaleString() + " signals in archive for selected sources";
    document.getElementById("metricCoverage").textContent = coverage + "% of " + totalSignals.toLocaleString() + " total signals";
    document.getElementById("metricInsight").textContent = insight;
    document.getElementById("metricCost").textContent = readySources.length + " of " + enabledSources.length + " sources live";
    document.getElementById("metricRefresh").textContent = refresh;
  }

  function matchCategories(text) {
    var hits = [];
    if (!configData || !configData.category_keywords) return hits;
    var lower = text.toLowerCase();
    Object.keys(configData.category_keywords).forEach(function (cat) {
      var terms = configData.category_keywords[cat] || [];
      var matched = terms.some(function (term) { return lower.indexOf(term.toLowerCase()) !== -1; });
      if (!matched && lower.indexOf(cat.replace(/_/g, " ")) !== -1) matched = true;
      if (matched) hits.push(cat);
    });
    if (!hits.length) {
      Object.keys(VOICE_EXTRAS).forEach(function (cat) {
        if (lower.indexOf(cat.replace(/_/g, " ")) !== -1) hits.push(cat);
      });
    }
    return hits;
  }

  function buildExpansions(title) {
    var text = (title || "").trim();
    var items = [];
    var seen = {};

    function add(label, kind, category) {
      var key = label.toLowerCase();
      if (!label || seen[key]) return;
      seen[key] = true;
      items.push({ key: key, label: label, kind: kind, category: category || "" });
    }

    if (text.length < 12) return items;

    var cats = matchCategories(text);
    cats.forEach(function (cat) {
      (VOICE_EXTRAS[cat] || []).forEach(function (phrase) { add(phrase, "voice", cat); });
      var terms = (configData && configData.category_keywords[cat]) || [];
      terms.slice(0, 4).forEach(function (term) { add(term, "civic", cat); });
    });

    text.toLowerCase().split(/[^a-z0-9'+]+/).forEach(function (word) {
      if (word.length >= 5 && items.length < 12) add(word, "civic", cats[0] || "");
    });

    return items.slice(0, 12);
  }

  function renderExpansions() {
    pillsEl.innerHTML = "";
    if (!expansionMeta.length && !customKeywords.length) {
      expansionsHint.textContent = "Finish the title, then pause — we’ll suggest extra topics and keywords.";
      return;
    }
    expansionsHint.textContent = "Tap to include extra topics and keywords in this research.";

    expansionMeta.forEach(function (item) {
      var btn = document.createElement("button");
      btn.type = "button";
      btn.className = "expansion-pill kind-" + item.kind +
        (selectedExpansions.has(item.key) ? " selected" : "");
      btn.textContent = item.label;
      btn.addEventListener("click", function () {
        if (selectedExpansions.has(item.key)) selectedExpansions.delete(item.key);
        else selectedExpansions.add(item.key);
        renderExpansions();
        updateClarity();
      });
      pillsEl.appendChild(btn);
    });

    customKeywords.forEach(function (label, idx) {
      var btn = document.createElement("button");
      btn.type = "button";
      btn.className = "expansion-pill kind-custom selected";
      btn.textContent = label + " ×";
      btn.addEventListener("click", function () {
        customKeywords.splice(idx, 1);
        renderExpansions();
      });
      pillsEl.appendChild(btn);
    });

    var addBtn = document.createElement("button");
    addBtn.type = "button";
    addBtn.className = "expansion-pill add-custom";
    addBtn.textContent = "+ add custom";
    addBtn.addEventListener("click", function () {
      customKwRow.hidden = false;
      customKwInput.focus();
    });
    pillsEl.appendChild(addBtn);
  }

  function refreshExpansionsFromTitle() {
    var next = buildExpansions(titleEl.value);
    var nextKeys = {};
    next.forEach(function (item) { nextKeys[item.key] = true; });
    selectedExpansions.forEach(function (key) {
      if (!nextKeys[key]) selectedExpansions.delete(key);
    });
    next.forEach(function (item) {
      if (item.kind === "voice") selectedExpansions.add(item.key);
    });
    expansionMeta = next;
    renderExpansions();
    updateClarity();
  }

  function renderListenGrid() {
    var grid = document.getElementById("listenGrid");
    grid.innerHTML = "";
    LISTEN_SOURCES.forEach(function (src) {
      var card = document.createElement("button");
      card.type = "button";
      card.className = "listen-card" + (src.on ? " on" : "") + (src.ready ? "" : " coming-soon");
      card.setAttribute("aria-pressed", src.on ? "true" : "false");
      var badge = src.ready ? "" : '<span class="listen-badge">Archive only</span>';
      card.innerHTML =
        '<div class="listen-copy"><strong>' + esc(src.title) + "</strong>" + badge +
        "<span>" + esc(src.blurb) + '</span></div><span class="switch" aria-hidden="true"></span>';
      card.addEventListener("click", function () {
        src.on = !src.on;
        renderListenGrid();
        updateMetrics();
      });
      grid.appendChild(card);
    });
  }

  function renderExtractGrid() {
    var grid = document.getElementById("extractGrid");
    grid.innerHTML = "";
    EXTRACT_OPTIONS.forEach(function (opt) {
      var label = document.createElement("label");
      label.className = "extract-card" + (opt.on ? " on" : "");
      label.innerHTML =
        '<input type="checkbox"' + (opt.on ? " checked" : "") + ">" +
        "<span><strong>" + esc(opt.title) + "</strong><small>" + esc(opt.blurb) + "</small></span>";
      label.querySelector("input").addEventListener("change", function (e) {
        opt.on = e.target.checked;
        label.classList.toggle("on", opt.on);
      });
      grid.appendChild(label);
    });
  }

  function renderTemplates() {
    var list = document.getElementById("templateList");
    list.innerHTML = "";
    TEMPLATES.forEach(function (tpl) {
      var btn = document.createElement("button");
      btn.type = "button";
      btn.className = "template-btn";
      btn.innerHTML = "<strong>" + esc(tpl.title) + "</strong><span>" + esc(tpl.blurb) + "</span>";
      btn.addEventListener("click", function () {
        titleEl.value = tpl.fill;
        customKeywords = [];
        refreshExpansionsFromTitle();
        updateMetrics();
        titleEl.focus();
      });
      list.appendChild(btn);
    });
  }

  function composeNotes() {
    var timeLabels = {
      "7d": "Last 7 days",
      "30d": "Last 30 days + rolling",
      "90d": "Last 90 days",
      ytd: "Year to date",
    };
    var geoEl = document.getElementById("fieldGeo");
    var langEl = document.getElementById("fieldLanguage");
    return [
      "Time window: " + (timeLabels[document.getElementById("fieldTimeWindow").value] || ""),
      "Geo: " + geoEl.options[geoEl.selectedIndex].text,
      "Language: " + langEl.options[langEl.selectedIndex].text,
      "Listen: " + sourceState().join(", "),
      "Extract: " + extractState().join(", "),
    ].join("\n");
  }

  function buildPayload() {
    var title = titleEl.value.trim();
    var keywords = selectedKeywordList();
    var categories = inferredCategories();
    return {
      title: title,
      topic: title,
      keywords: keywords,
      categories: categories,
      notes: composeNotes(),
    };
  }

  async function submitResearch(mode) {
    formMsg.textContent = "";
    var payload = buildPayload();
    if (!payload.title) {
      formMsg.textContent = "Title is required.";
      return;
    }

    try {
      var res = await fetch(API, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      var data = await res.json();
      if (!res.ok) {
        formMsg.textContent = data.error || "Failed to create research.";
        return;
      }
      var research = data.research;
      if (mode === "launch") {
        formMsg.textContent = "Launching — running archive + queuing jobs…";
        var enabledSources = sourceState();
        try {
          await fetch(API + "/" + research.id + "/launch", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ sources: enabledSources }),
          });
        } catch (err) { /* launch is best-effort */ }
        window.location.href = "research-detail.html?id=" + research.id;
        return;
      }
      titleEl.value = "";
      customKeywords = [];
      selectedExpansions.clear();
      expansionMeta = [];
      renderExpansions();
      updateClarity();
      formMsg.textContent = "Draft saved.";
      setTimeout(function () { formMsg.textContent = ""; }, 2000);
      loadList();
    } catch (err) {
      formMsg.textContent = "Network error.";
    }
  }

  function renderFilters(items) {
    var counts = { all: items.length };
    items.forEach(function (r) {
      counts[r.status] = (counts[r.status] || 0) + 1;
    });
    var statuses = ["all", "draft", "active", "gathering", "ready", "stale"];
    filterBar.innerHTML = statuses
      .filter(function (s) { return counts[s]; })
      .map(function (s) {
        return '<button class="filter-btn' + (s === activeFilter ? " active" : "") +
          '" data-filter="' + s + '">' +
          esc(s === "all" ? "All" : s) +
          " <span>" + counts[s] + "</span></button>";
      }).join("");

    filterBar.querySelectorAll(".filter-btn").forEach(function (btn) {
      btn.addEventListener("click", function () {
        activeFilter = this.dataset.filter;
        renderFilters(allItems);
        renderList(allItems);
      });
    });
  }

  function renderList(items) {
    var filtered = activeFilter === "all"
      ? items
      : items.filter(function (r) { return r.status === activeFilter; });

    listEl.innerHTML = "";
    listCount.textContent = filtered.length + " of " + items.length;

    if (!filtered.length) {
      emptyMsg.hidden = false;
      emptyMsg.textContent = items.length === 0
        ? "No researches yet. Create one above to get started."
        : 'No researches with status "' + activeFilter + '".';
      return;
    }
    emptyMsg.hidden = true;

    filtered.forEach(function (r) {
      var card = document.createElement("a");
      card.className = "research-card";
      card.href = "research-detail.html?id=" + r.id;

      var cats = (r.categories || []).map(function (c) {
        return '<span class="cat-tag">' + esc(c) + "</span>";
      }).join("");

      var kws = (r.keywords || []).map(function (k) {
        return '<span class="kw-tag">' + esc(k) + "</span>";
      }).join("");

      var hitCount = r.hit_count || 0;

      card.innerHTML =
        '<div class="rc-top">' +
        '<h3 class="rc-title">' + esc(r.title) + "</h3>" +
        '<div class="rc-top-right">' +
        (hitCount ? '<span class="rc-hits">' + hitCount + " hit" + (hitCount !== 1 ? "s" : "") + "</span>" : "") +
        '<span class="rc-status status-' + esc(r.status) + '">' + esc(r.status) + "</span>" +
        "</div></div>" +
        (r.topic ? '<p class="rc-topic">' + esc(r.topic) + "</p>" : "") +
        '<div class="rc-tags">' + cats + kws + "</div>" +
        '<time class="rc-time">' + new Date(r.created_at).toLocaleDateString() + "</time>";

      listEl.appendChild(card);
    });
  }

  async function loadList() {
    try {
      var res = await fetch(API);
      var data = await res.json();
      allItems = data.researches || [];
      renderFilters(allItems);
      renderList(allItems);
    } catch (e) {
      listEl.innerHTML = '<p class="error-msg">Could not load researches.</p>';
    }
  }

  async function loadConfig() {
    try {
      var res = await fetch("/api/config");
      configData = await res.json();
    } catch (e) { /* config optional */ }
  }

  titleEl.addEventListener("input", function () {
    updateClarity();
    clearTimeout(expansionTimer);
    expansionTimer = setTimeout(refreshExpansionsFromTitle, 650);
  });
  titleEl.addEventListener("blur", function () {
    clearTimeout(expansionTimer);
    refreshExpansionsFromTitle();
  });

  ["fieldTimeWindow", "fieldGeo", "fieldLanguage"].forEach(function (id) {
    document.getElementById(id).addEventListener("change", updateMetrics);
  });

  var launchBtn = document.getElementById("btnLaunch");
  var draftBtn = document.getElementById("btnSaveDraft");

  draftBtn.addEventListener("click", function () {
    draftBtn.disabled = true;
    draftBtn.textContent = "Saving…";
    submitResearch("draft").finally(function () {
      draftBtn.disabled = false;
      draftBtn.textContent = "Save draft";
    });
  });
  launchBtn.addEventListener("click", function () {
    launchBtn.disabled = true;
    launchBtn.textContent = "Launching…";
    submitResearch("launch").finally(function () {
      launchBtn.disabled = false;
      launchBtn.textContent = "Launch scrape";
    });
  });
  document.getElementById("createForm").addEventListener("submit", function (e) {
    e.preventDefault();
    launchBtn.disabled = true;
    launchBtn.textContent = "Launching…";
    submitResearch("launch").finally(function () {
      launchBtn.disabled = false;
      launchBtn.textContent = "Launch scrape";
    });
  });

  document.getElementById("customKwAdd").addEventListener("click", function () {
    var val = customKwInput.value.trim();
    if (!val) return;
    if (customKeywords.indexOf(val) === -1) customKeywords.push(val);
    customKwInput.value = "";
    customKwRow.hidden = true;
    renderExpansions();
  });
  document.getElementById("customKwCancel").addEventListener("click", function () {
    customKwInput.value = "";
    customKwRow.hidden = true;
  });

  renderListenGrid();
  renderExtractGrid();
  renderTemplates();
  updateClarity();
  updateMetrics();
  loadConfig().then(loadList);
})();
