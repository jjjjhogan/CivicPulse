/* research-detail.js — show single research + archive hits */

(function () {
  const params = new URLSearchParams(window.location.search);
  const id = params.get('id');
  const container = document.getElementById('detailContent');

  function esc(s) {
    const el = document.createElement('span');
    el.textContent = s;
    return el.innerHTML;
  }

  async function load() {
    if (!id) {
      container.innerHTML = '<p class="error-msg">No research ID provided.</p>';
      return;
    }
    try {
      const res = await fetch('/api/researches/' + id);
      if (!res.ok) {
        container.innerHTML = '<p class="error-msg">Research not found.</p>';
        return;
      }
      const data = await res.json();
      render(data.research);
    } catch (e) {
      container.innerHTML = '<p class="error-msg">Could not load research.</p>';
    }
  }

  function renderHits(hits) {
    if (!hits || !hits.length) {
      return '<p class="empty-msg">No matching signals found. Try broadening your keywords or categories.</p>';
    }
    return '<div class="hits-list">' + hits.map(function (h) {
      var s = h.signal || {};
      var cats = (s.categories || []).map(function (c) {
        return '<span class="cat-tag">' + esc(c) + '</span>';
      }).join('');
      return '<div class="hit-card">' +
        '<div class="hit-top">' +
          '<a class="hit-title" href="signal.html?id=' + s.id + '">' + esc(s.title || '(no title)') + '</a>' +
          '<span class="hit-score">' + h.score.toFixed(1) + '</span>' +
        '</div>' +
        (s.body && s.body !== s.title
          ? '<p class="hit-body">' + esc(s.body.slice(0, 200)) + (s.body.length > 200 ? '...' : '') + '</p>'
          : '') +
        '<div class="hit-meta">' +
          '<span class="hit-source">' + esc(s.source || '') + '</span>' +
          cats +
          '<span class="hit-reason">' + esc(h.match_reason) + '</span>' +
        '</div>' +
      '</div>';
    }).join('') + '</div>';
  }

  async function runArchive(btn) {
    btn.disabled = true;
    btn.textContent = 'Running...';
    try {
      var res = await fetch('/api/researches/' + id + '/archive', { method: 'POST' });
      var data = await res.json();
      if (!res.ok) {
        btn.textContent = 'Run Archive';
        btn.disabled = false;
        alert(data.error || 'Archive failed.');
        return;
      }
      render(data.research);
    } catch (e) {
      btn.textContent = 'Run Archive';
      btn.disabled = false;
      alert('Network error.');
    }
  }

  function render(r) {
    var cats = (r.categories || []).map(function (c) {
      return '<span class="cat-tag">' + esc(c) + '</span>';
    }).join('');
    var kws = (r.keywords || []).map(function (k) {
      return '<span class="kw-tag">' + esc(k) + '</span>';
    }).join('');

    var hitCount = r.hit_count != null ? r.hit_count : (r.hits ? r.hits.length : null);
    var hitLabel = hitCount != null ? hitCount + ' hit' + (hitCount !== 1 ? 's' : '') : '';

    container.innerHTML =
      '<div class="dash-head">' +
        '<div>' +
          '<h1>' + esc(r.title) + '</h1>' +
          (r.topic ? '<p class="dash-sub">' + esc(r.topic) + '</p>' : '') +
        '</div>' +
        '<span class="rc-status status-' + esc(r.status) + '">' + esc(r.status) + '</span>' +
      '</div>' +
      '<div class="panel detail-panel">' +
        '<div class="detail-row">' +
          '<span class="detail-label">Categories</span>' +
          '<div class="rc-tags">' + (cats || '<span class="field-hint">none</span>') + '</div>' +
        '</div>' +
        '<div class="detail-row">' +
          '<span class="detail-label">Keywords</span>' +
          '<div class="rc-tags">' + (kws || '<span class="field-hint">none</span>') + '</div>' +
        '</div>' +
        (r.notes ? '<div class="detail-row"><span class="detail-label">Notes</span><p class="detail-notes">' + esc(r.notes) + '</p></div>' : '') +
        '<div class="detail-row">' +
          '<span class="detail-label">Created</span>' +
          '<time>' + new Date(r.created_at).toLocaleString() + '</time>' +
        '</div>' +
      '</div>' +
      '<div class="panel detail-panel" id="archivePanel">' +
        '<div class="panel-head">' +
          '<h2>Archive Hits</h2>' +
          '<div class="panel-head-right">' +
            (hitLabel ? '<span class="panel-hint">' + hitLabel + '</span>' : '') +
            '<button class="btn btn-sm" id="archiveBtn">Run Archive</button>' +
          '</div>' +
        '</div>' +
        (r.hits ? renderHits(r.hits) : '<p class="empty-msg">Click "Run Archive" to match signals.</p>') +
      '</div>';

    document.getElementById('archiveBtn').addEventListener('click', function () {
      runArchive(this);
    });
  }

  load();
})();
