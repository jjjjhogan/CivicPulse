/* research.js — create + list researches */

(function () {
  const API = '/api/researches';

  const form = document.getElementById('createForm');
  const listEl = document.getElementById('researchList');
  const emptyMsg = document.getElementById('emptyMsg');
  const listCount = document.getElementById('listCount');
  const formMsg = document.getElementById('formMsg');

  function splitCsv(val) {
    return (val || '').split(',').map(s => s.trim()).filter(Boolean);
  }

  function renderList(items) {
    listEl.innerHTML = '';
    listCount.textContent = items.length + ' total';
    if (!items.length) {
      emptyMsg.hidden = false;
      return;
    }
    emptyMsg.hidden = true;
    items.forEach(r => {
      const card = document.createElement('a');
      card.className = 'research-card';
      card.href = 'research-detail.html?id=' + r.id;

      const cats = (r.categories || []).map(c =>
        '<span class="cat-tag">' + esc(c) + '</span>'
      ).join('');

      const kws = (r.keywords || []).map(k =>
        '<span class="kw-tag">' + esc(k) + '</span>'
      ).join('');

      card.innerHTML =
        '<div class="rc-top">' +
          '<h3 class="rc-title">' + esc(r.title) + '</h3>' +
          '<span class="rc-status status-' + esc(r.status) + '">' + esc(r.status) + '</span>' +
        '</div>' +
        (r.topic ? '<p class="rc-topic">' + esc(r.topic) + '</p>' : '') +
        '<div class="rc-tags">' + cats + kws + '</div>' +
        '<time class="rc-time">' + new Date(r.created_at).toLocaleDateString() + '</time>';

      listEl.appendChild(card);
    });
  }

  function esc(s) {
    const el = document.createElement('span');
    el.textContent = s;
    return el.innerHTML;
  }

  async function loadList() {
    try {
      const res = await fetch(API);
      const data = await res.json();
      renderList(data.researches || []);
    } catch (e) {
      listEl.innerHTML = '<p class="error-msg">Could not load researches.</p>';
    }
  }

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    formMsg.textContent = '';

    const title = document.getElementById('fieldTitle').value.trim();
    if (!title) {
      formMsg.textContent = 'Title is required.';
      return;
    }

    const payload = {
      title,
      topic: document.getElementById('fieldTopic').value.trim(),
      keywords: splitCsv(document.getElementById('fieldKeywords').value),
      categories: splitCsv(document.getElementById('fieldCategories').value),
      notes: document.getElementById('fieldNotes').value.trim(),
    };

    try {
      const res = await fetch(API, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      const data = await res.json();
      if (!res.ok) {
        formMsg.textContent = data.error || 'Failed to create research.';
        return;
      }
      form.reset();
      formMsg.textContent = 'Created!';
      setTimeout(() => { formMsg.textContent = ''; }, 2000);
      loadList();
    } catch (err) {
      formMsg.textContent = 'Network error.';
    }
  });

  loadList();
})();
