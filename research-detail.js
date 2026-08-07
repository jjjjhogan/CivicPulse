/* research-detail.js — show single research */

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

  function render(r) {
    const cats = (r.categories || []).map(c =>
      '<span class="cat-tag">' + esc(c) + '</span>'
    ).join('');
    const kws = (r.keywords || []).map(k =>
      '<span class="kw-tag">' + esc(k) + '</span>'
    ).join('');

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
        '</div>' +
        '<p class="empty-msg">Archive matching not yet available. Coming in Session 8.</p>' +
      '</div>';
  }

  load();
})();
