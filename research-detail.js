/* research-detail.js — research workspace: archive/summary tabs, edit, status, delete */

(function () {
  var params = new URLSearchParams(window.location.search);
  var id = params.get("id");
  var container = document.getElementById("detailContent");
  var currentResearch = null;
  var activeTab = "archive";
  var configData = null;

  function esc(s) {
    var el = document.createElement("span");
    el.textContent = s;
    return el.innerHTML;
  }

  function splitCsv(val) {
    return (val || "").split(",").map(function (s) { return s.trim(); }).filter(Boolean);
  }

  // ── API helpers ──────────────────────────────────────

  async function apiGet() {
    var res = await fetch("/api/researches/" + id);
    if (!res.ok) return null;
    return (await res.json()).research;
  }

  async function apiPatch(fields) {
    var res = await fetch("/api/researches/" + id, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(fields),
    });
    return res.json();
  }

  async function apiDelete() {
    return fetch("/api/researches/" + id, { method: "DELETE" });
  }

  async function apiRunArchive() {
    return fetch("/api/researches/" + id + "/archive", { method: "POST" });
  }

  async function loadConfig() {
    try {
      var res = await fetch("/api/config");
      configData = await res.json();
    } catch (e) { /* optional */ }
  }

  // ── Render helpers ───────────────────────────────────

  function renderTags(arr, cls) {
    return (arr || []).map(function (t) {
      return '<span class="' + cls + '">' + esc(t) + "</span>";
    }).join("");
  }

  function renderHits(hits) {
    if (!hits || !hits.length) {
      return '<p class="empty-msg">No matching signals yet. Click "Run Archive" to scan existing signals.</p>';
    }
    return '<div class="hits-list">' + hits.map(function (h) {
      var s = h.signal || {};
      var cats = renderTags(s.categories, "cat-tag");
      return '<div class="hit-card">' +
        '<div class="hit-top">' +
        '<a class="hit-title" href="signal.html?id=' + encodeURIComponent(s.id || "") + '">' +
        esc(s.title || "(no title)") + "</a>" +
        '<span class="hit-score">' + (h.score || 0).toFixed(1) + "</span></div>" +
        (s.body && s.body !== s.title
          ? '<p class="hit-body">' + esc(s.body.slice(0, 200)) + (s.body.length > 200 ? "..." : "") + "</p>"
          : "") +
        '<div class="hit-meta">' +
        '<span class="hit-source">' + esc(s.source || "") + "</span>" +
        cats +
        '<span class="hit-reason">' + esc(h.match_reason) + "</span></div></div>";
    }).join("") + "</div>";
  }

  function renderStatusOptions(current) {
    return ["draft", "active", "gathering", "ready", "stale"].map(function (s) {
      return "<option" + (s === current ? " selected" : "") + ">" + esc(s) + "</option>";
    }).join("");
  }

  // ── Main render ──────────────────────────────────────

  function render(r) {
    currentResearch = r;
    var cats = renderTags(r.categories, "cat-tag");
    var kws = renderTags(r.keywords, "kw-tag");
    var hitCount = r.hit_count != null ? r.hit_count : r.hits ? r.hits.length : 0;

    container.innerHTML =
      // Header
      '<div class="dash-head workspace-head"><div>' +
      '<h1 class="workspace-title">' + esc(r.title) + "</h1>" +
      (r.topic ? '<p class="dash-sub">' + esc(r.topic) + "</p>" : "") +
      '</div><div class="workspace-actions">' +
      '<select class="status-select" id="statusSelect">' + renderStatusOptions(r.status) + "</select>" +
      '<button class="btn btn-sm btn-danger" id="deleteBtn" title="Delete this research">Delete</button>' +
      "</div></div>" +
      // Info panel
      '<div class="panel detail-panel">' +
      // Categories row (display)
      '<div class="detail-row" id="catDisplayRow">' +
      '<span class="detail-label">Categories</span>' +
      '<div class="detail-value">' +
      '<div class="rc-tags">' + (cats || '<span class="field-hint">none</span>') + "</div>" +
      '<button class="edit-btn" id="editCats">Edit</button>' +
      "</div></div>" +
      // Categories row (edit — picker)
      '<div class="detail-row" id="catEditRow" hidden>' +
      '<span class="detail-label">Categories</span>' +
      '<div class="detail-value detail-value-col">' +
      '<div class="cat-picker" id="detailCatPicker"></div>' +
      '<div class="inline-actions">' +
      '<button class="btn btn-xs" id="catSave">Save</button>' +
      '<button class="btn btn-xs btn-ghost" id="catCancel">Cancel</button>' +
      "</div></div></div>" +
      // Keywords row (display)
      '<div class="detail-row" id="kwDisplayRow">' +
      '<span class="detail-label">Keywords</span>' +
      '<div class="detail-value">' +
      '<div class="rc-tags">' + (kws || '<span class="field-hint">none</span>') + "</div>" +
      '<button class="edit-btn" id="editKws">Edit</button>' +
      "</div></div>" +
      // Keywords row (edit)
      '<div class="detail-row" id="kwEditRow" hidden>' +
      '<span class="detail-label">Keywords</span>' +
      '<div class="detail-value detail-value-col">' +
      '<div class="kw-suggestions" id="detailKwSuggestions" hidden>' +
      '<span class="field-hint">Suggested:</span>' +
      '<div class="kw-chips" id="detailKwChips"></div></div>' +
      '<div class="inline-row">' +
      '<input type="text" class="inline-edit" id="kwInput" value="' +
      esc((r.keywords || []).join(", ")) + '" placeholder="comma-separated">' +
      '<button class="btn btn-xs" id="kwSave">Save</button>' +
      '<button class="btn btn-xs btn-ghost" id="kwCancel">Cancel</button>' +
      "</div></div></div>" +
      // Notes
      (r.notes ? '<div class="detail-row"><span class="detail-label">Notes</span>' +
        '<p class="detail-notes">' + esc(r.notes) + "</p></div>" : "") +
      // Created
      '<div class="detail-row"><span class="detail-label">Created</span>' +
      "<time>" + new Date(r.created_at).toLocaleString() + "</time></div>" +
      "</div>" +
      // Tabs
      '<div class="workspace-tabs">' +
      '<button class="tab-btn' + (activeTab === "archive" ? " active" : "") +
      '" data-tab="archive">Archive <span class="tab-count">' + hitCount + "</span></button>" +
      '<button class="tab-btn' + (activeTab === "new" ? " active" : "") +
      '" data-tab="new">Summary</button></div>' +
      // Archive panel
      '<div class="tab-panel" id="archivePanel"' + (activeTab !== "archive" ? " hidden" : "") + ">" +
      '<div class="panel-toolbar">' +
      '<button class="btn btn-sm" id="archiveBtn">Run Archive</button>' +
      '<span class="panel-hint" id="archiveHint">' + hitCount +
      " signal" + (hitCount !== 1 ? "s" : "") + " matched</span></div>" +
      renderHits(r.hits) + "</div>" +
      // Summary panel
      '<div class="tab-panel" id="newPanel"' + (activeTab !== "new" ? " hidden" : "") + ">" +
      '<div class="panel-toolbar"><button class="btn btn-sm" id="loadSummaryBtn">Load Summary</button>' +
      '<span class="panel-hint" id="summaryHint">Select extract options when creating research.</span></div>' +
      '<div id="summaryContent"></div></div>';

    bindEvents();
  }

  // ── Event bindings ───────────────────────────────────

  function bindEvents() {
    document.getElementById("statusSelect").addEventListener("change", async function () {
      var res = await apiPatch({ status: this.value });
      if (res.research) render(res.research);
    });

    document.getElementById("deleteBtn").addEventListener("click", async function () {
      if (!confirm('Delete "' + currentResearch.title + '"? This cannot be undone.')) return;
      var res = await apiDelete();
      if (res.ok) window.location.href = "research.html";
      else alert("Failed to delete.");
    });

    // Tabs
    document.querySelectorAll(".tab-btn").forEach(function (btn) {
      btn.addEventListener("click", function () {
        activeTab = this.dataset.tab;
        document.querySelectorAll(".tab-btn").forEach(function (b) {
          b.classList.toggle("active", b.dataset.tab === activeTab);
        });
        document.getElementById("archivePanel").hidden = activeTab !== "archive";
        document.getElementById("newPanel").hidden = activeTab !== "new";
      });
    });

    // Archive
    document.getElementById("archiveBtn").addEventListener("click", async function () {
      this.disabled = true;
      this.textContent = "Running...";
      try {
        var res = await apiRunArchive();
        var data = await res.json();
        if (!res.ok) {
          alert(data.error || "Archive failed.");
          this.disabled = false;
          this.textContent = "Run Archive";
          return;
        }
        render(data.research);
      } catch (e) {
        alert("Network error.");
        this.disabled = false;
        this.textContent = "Run Archive";
      }
    });

    // Summary panel
    var summaryBtn = document.getElementById("loadSummaryBtn");
    if (summaryBtn) {
      summaryBtn.addEventListener("click", async function () {
        summaryBtn.disabled = true;
        summaryBtn.textContent = "Loading...";
        try {
          var res = await fetch("/api/researches/" + id + "/summary");
          var data = await res.json();
          if (!res.ok) {
            document.getElementById("summaryContent").innerHTML =
              '<p class="empty-msg">' + esc(data.error || "Failed to load summary.") + "</p>";
            summaryBtn.disabled = false;
            summaryBtn.textContent = "Load Summary";
            return;
          }
          var html = '<div class="summary-results">';
          html += "<p><strong>" + data.hit_count + " signals</strong> matched";
          if (data.sources_used && data.sources_used.length) {
            html += " from " + data.sources_used.map(esc).join(", ");
          }
          html += ".</p>";
          var sectionKeys = Object.keys(data.sections || {});
          if (!sectionKeys.length) {
            html += '<p class="empty-msg">No extract options selected for this research.</p>';
          }
          sectionKeys.forEach(function (key) {
            var sec = data.sections[key];
            html += '<div class="summary-section"><h4>' + esc(sec.label) + "</h4>";
            if (sec.positive !== undefined) {
              html += "<p>Positive: " + sec.positive + " · Negative: " + sec.negative + " · Neutral: " + sec.neutral + "</p>";
            }
            if (sec.clusters) {
              var cats = Object.keys(sec.clusters);
              html += "<ul>" + cats.map(function (c) { return "<li>" + esc(c) + ": " + sec.clusters[c] + "</li>"; }).join("") + "</ul>";
            }
            if (sec.by_source) {
              var srcs = Object.keys(sec.by_source);
              html += "<ul>" + srcs.map(function (s) { return "<li>" + esc(s) + ": " + sec.by_source[s] + "</li>"; }).join("") + "</ul>";
            }
            if (sec.asks && sec.asks.length) {
              html += "<ul>" + sec.asks.slice(0, 10).map(function (a) { return "<li>" + esc(a) + "</li>"; }).join("") + "</ul>";
              if (sec.total_detected > 10) html += "<p>… and " + (sec.total_detected - 10) + " more</p>";
            }
            if (sec.flagged_count !== undefined) {
              html += "<p>" + sec.flagged_count + " of " + sec.total_signals + " signals flagged.</p>";
            }
            if (sec.suspected_count !== undefined) {
              html += "<p>" + sec.suspected_count + " of " + sec.total_signals + " signals suspected.</p>";
            }
            if (sec.note) html += '<p class="panel-hint">' + esc(sec.note) + "</p>";
            html += "</div>";
          });
          html += "</div>";
          document.getElementById("summaryContent").innerHTML = html;
          document.getElementById("summaryHint").textContent = sectionKeys.length + " extract section" + (sectionKeys.length !== 1 ? "s" : "");
          summaryBtn.textContent = "Refresh";
          summaryBtn.disabled = false;
        } catch (e) {
          document.getElementById("summaryContent").innerHTML = '<p class="empty-msg">Network error.</p>';
          summaryBtn.disabled = false;
          summaryBtn.textContent = "Load Summary";
        }
      });
    }

    // Category edit (picker-based)
    bindCatEdit();
    // Keyword edit
    bindKwEdit();
  }

  // ── Category picker edit ─────────────────────────────

  function bindCatEdit() {
    var editBtn = document.getElementById("editCats");
    var displayRow = document.getElementById("catDisplayRow");
    var editRow = document.getElementById("catEditRow");
    var picker = document.getElementById("detailCatPicker");
    var saveBtn = document.getElementById("catSave");
    var cancelBtn = document.getElementById("catCancel");
    var editCats = new Set(currentResearch.categories || []);

    function renderPicker() {
      picker.innerHTML = "";
      var allCats = (configData && configData.categories) || [];
      if (!allCats.length) {
        allCats = Array.from(editCats);
      }
      allCats.forEach(function (cat) {
        var btn = document.createElement("button");
        btn.type = "button";
        btn.className = "cat-pick-btn" + (editCats.has(cat) ? " selected" : "");
        btn.textContent = cat.replace(/_/g, " ");
        btn.addEventListener("click", function () {
          if (editCats.has(cat)) { editCats.delete(cat); btn.classList.remove("selected"); }
          else { editCats.add(cat); btn.classList.add("selected"); }
          updateDetailKwSuggestions(editCats);
        });
        picker.appendChild(btn);
      });
    }

    editBtn.addEventListener("click", function () {
      editCats = new Set(currentResearch.categories || []);
      renderPicker();
      displayRow.hidden = true;
      editRow.hidden = false;
      updateDetailKwSuggestions(editCats);
    });

    cancelBtn.addEventListener("click", function () {
      editRow.hidden = true;
      displayRow.hidden = false;
      document.getElementById("detailKwSuggestions").hidden = true;
    });

    saveBtn.addEventListener("click", async function () {
      saveBtn.disabled = true;
      var res = await apiPatch({ categories: Array.from(editCats) });
      saveBtn.disabled = false;
      if (res.research) render(res.research);
    });
  }

  function updateDetailKwSuggestions(cats) {
    var sugEl = document.getElementById("detailKwSuggestions");
    var chipsEl = document.getElementById("detailKwChips");
    if (!configData || !configData.category_keywords || !cats.size) {
      sugEl.hidden = true;
      return;
    }
    var kwInput = document.getElementById("kwInput");
    var existing = new Set((currentResearch.keywords || []).map(function (k) { return k.toLowerCase(); }));
    if (kwInput) {
      splitCsv(kwInput.value).forEach(function (k) { existing.add(k.toLowerCase()); });
    }
    var suggestions = [];
    cats.forEach(function (cat) {
      (configData.category_keywords[cat] || []).forEach(function (t) {
        if (!existing.has(t.toLowerCase()) && suggestions.indexOf(t) === -1) suggestions.push(t);
      });
    });
    if (!suggestions.length) { sugEl.hidden = true; return; }
    sugEl.hidden = false;
    chipsEl.innerHTML = "";
    suggestions.forEach(function (kw) {
      var chip = document.createElement("button");
      chip.type = "button";
      chip.className = "kw-chip";
      chip.textContent = kw;
      chip.addEventListener("click", function () {
        var inp = document.getElementById("kwInput");
        if (inp) {
          var current = splitCsv(inp.value);
          current.push(kw);
          inp.value = current.join(", ");
        }
        chip.remove();
        if (!chipsEl.children.length) sugEl.hidden = true;
      });
      chipsEl.appendChild(chip);
    });
  }

  // ── Keyword edit ─────────────────────────────────────

  function bindKwEdit() {
    var editBtn = document.getElementById("editKws");
    var displayRow = document.getElementById("kwDisplayRow");
    var editRow = document.getElementById("kwEditRow");
    var input = document.getElementById("kwInput");
    var saveBtn = document.getElementById("kwSave");
    var cancelBtn = document.getElementById("kwCancel");

    editBtn.addEventListener("click", function () {
      displayRow.hidden = true;
      editRow.hidden = false;
      input.focus();
    });

    cancelBtn.addEventListener("click", function () {
      editRow.hidden = true;
      displayRow.hidden = false;
      input.value = (currentResearch.keywords || []).join(", ");
      document.getElementById("detailKwSuggestions").hidden = true;
    });

    saveBtn.addEventListener("click", async function () {
      saveBtn.disabled = true;
      var res = await apiPatch({ keywords: splitCsv(input.value) });
      saveBtn.disabled = false;
      if (res.research) render(res.research);
    });
  }

  // ── Init ─────────────────────────────────────────────

  async function load() {
    if (!id) {
      container.innerHTML = '<p class="error-msg">No research ID provided.</p>';
      return;
    }
    await loadConfig();
    try {
      var r = await apiGet();
      if (!r) {
        container.innerHTML = '<p class="error-msg">Research not found.</p>';
        return;
      }
      render(r);
    } catch (e) {
      container.innerHTML = '<p class="error-msg">Could not load research.</p>';
    }
  }

  load();
})();
