/* research.js — create + list researches with category picker + keyword assist */

(function () {
  var API = "/api/researches";
  var allItems = [];
  var activeFilter = "all";
  var configData = null;
  var selectedCats = new Set();

  var form = document.getElementById("createForm");
  var listEl = document.getElementById("researchList");
  var emptyMsg = document.getElementById("emptyMsg");
  var listCount = document.getElementById("listCount");
  var formMsg = document.getElementById("formMsg");
  var filterBar = document.getElementById("filterBar");
  var catPicker = document.getElementById("catPicker");
  var kwSuggestions = document.getElementById("kwSuggestions");
  var kwChips = document.getElementById("kwChips");
  var kwInput = document.getElementById("fieldKeywords");

  function splitCsv(val) {
    return (val || "").split(",").map(function (s) { return s.trim(); }).filter(Boolean);
  }

  function esc(s) {
    var el = document.createElement("span");
    el.textContent = s;
    return el.innerHTML;
  }

  // ── Config + category picker ─────────────────────────

  async function loadConfig() {
    try {
      var res = await fetch("/api/config");
      configData = await res.json();
      renderCatPicker();
    } catch (e) { /* config optional */ }
  }

  function renderCatPicker() {
    if (!configData || !configData.categories) return;
    catPicker.innerHTML = "";
    configData.categories.forEach(function (cat) {
      var btn = document.createElement("button");
      btn.type = "button";
      btn.className = "cat-pick-btn";
      btn.textContent = cat.replace(/_/g, " ");
      btn.dataset.cat = cat;
      if (selectedCats.has(cat)) btn.classList.add("selected");
      btn.addEventListener("click", function () {
        if (selectedCats.has(cat)) {
          selectedCats.delete(cat);
          btn.classList.remove("selected");
        } else {
          selectedCats.add(cat);
          btn.classList.add("selected");
        }
        updateKwSuggestions();
      });
      catPicker.appendChild(btn);
    });
  }

  function updateKwSuggestions() {
    if (!configData || !configData.category_keywords || selectedCats.size === 0) {
      kwSuggestions.hidden = true;
      return;
    }
    var existing = new Set(splitCsv(kwInput.value).map(function (k) { return k.toLowerCase(); }));
    var suggestions = [];
    selectedCats.forEach(function (cat) {
      var terms = configData.category_keywords[cat] || [];
      terms.forEach(function (t) {
        if (!existing.has(t.toLowerCase()) && suggestions.indexOf(t) === -1) {
          suggestions.push(t);
        }
      });
    });

    if (!suggestions.length) {
      kwSuggestions.hidden = true;
      return;
    }
    kwSuggestions.hidden = false;
    kwChips.innerHTML = "";
    suggestions.forEach(function (kw) {
      var chip = document.createElement("button");
      chip.type = "button";
      chip.className = "kw-chip";
      chip.textContent = kw;
      chip.addEventListener("click", function () {
        var current = splitCsv(kwInput.value);
        current.push(kw);
        kwInput.value = current.join(", ");
        chip.remove();
        if (!kwChips.children.length) kwSuggestions.hidden = true;
      });
      kwChips.appendChild(chip);
    });
  }

  // ── Filter bar ───────────────────────────────────────

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

  // ── List ─────────────────────────────────────────────

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

  // ── Create ───────────────────────────────────────────

  form.addEventListener("submit", async function (e) {
    e.preventDefault();
    formMsg.textContent = "";

    var title = document.getElementById("fieldTitle").value.trim();
    if (!title) {
      formMsg.textContent = "Title is required.";
      return;
    }

    var payload = {
      title: title,
      topic: document.getElementById("fieldTopic").value.trim(),
      keywords: splitCsv(kwInput.value),
      categories: Array.from(selectedCats),
      notes: document.getElementById("fieldNotes").value.trim(),
    };

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
      form.reset();
      selectedCats.clear();
      renderCatPicker();
      kwSuggestions.hidden = true;
      formMsg.textContent = "Created!";
      setTimeout(function () { formMsg.textContent = ""; }, 2000);
      loadList();
    } catch (err) {
      formMsg.textContent = "Network error.";
    }
  });

  // ── Init ─────────────────────────────────────────────

  loadConfig();
  loadList();
})();
