// GCSE Revise - Main Application

let subjectsData = [];
let searchIndex = null;
let searchIndexLoading = false;
let searchIndexLoaded = false;
const SEARCH_TOPIC_LIMIT = 30;

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function escapeHtml(value) {
  return String(value).replace(/[&<>"']/g, functionMap);
}

function functionMap(c) {
  switch (c) {
    case '&': return '&#38;';
    case '<': return '&#60;';
    case '>': return '&#62;';
    case '"': return '&#34;';
    case "'": return '&#39;';
    default: return c;
  }
}

// ---------------------------------------------------------------------------
// Data loading
// ---------------------------------------------------------------------------

// Load subjects data (only useful on the home page where the subjects grid lives)
async function loadSubjects() {
  try {
    const response = await fetch('subjects.json');
    if (!response.ok) throw new Error('HTTP ' + response.status);
    const data = await response.json();
    subjectsData = data.subjects || [];
    renderSubjects('all');
  } catch (e) {
    console.error('Failed to load subjects:', e);
  }
}

// Lazy-load the combined subject + topic search index the first time the search
// box is used.  Loaded once and cached for the lifetime of the page.
async function ensureSearchIndex() {
  if (searchIndexLoaded) return true;
  if (searchIndexLoading) return false;
  searchIndexLoading = true;
  try {
    const response = await fetch('search-index.json');
    if (!response.ok) throw new Error('HTTP ' + response.status);
    searchIndex = await response.json();
    searchIndexLoaded = true;
  } catch (e) {
    console.error('Failed to load search index:', e);
  } finally {
    searchIndexLoading = false;
  }
  return searchIndexLoaded;
}

// ---------------------------------------------------------------------------
// Grid rendering
// ---------------------------------------------------------------------------

function subjectCard(subject) {
  return `
    <a href="${escapeHtml(subject.url || subject.id + '.html')}" class="subject-card">
      <div class="subject-category">${escapeHtml(subject.category)}</div>
      <h3>${escapeHtml(subject.name)}</h3>
      <div class="paper-count">${subject.papers || 0} paper${(subject.papers || 0) > 1 ? 's' : ''}</div>
      <div class="board-badges">
        ${(subject.boards || []).map(b => `<span class="board-badge">${escapeHtml(b)}</span>`).join('')}
      </div>
    </a>`;
}

function topicCard(topic) {
  const context = topic.strandName
    ? `${escapeHtml(topic.subjectName)} · ${escapeHtml(topic.strandName)}`
    : escapeHtml(topic.subjectName);
  const idLabel = topic.id ? `<span class="topic-id-mini">${escapeHtml(topic.id)}</span>` : '';
  return `
    <a href="${escapeHtml(topic.url)}" class="subject-card topic-result">
      <div class="subject-category">${context}</div>
      <h3>${idLabel}${escapeHtml(topic.name)}</h3>
      <div class="paper-count">Topic</div>
    </a>`;
}

// Render subjects grid grouped by the requested category tab.
function renderSubjects(category) {
  const grid = document.getElementById('subjects-grid');
  if (!grid) return;
  const filtered = category === 'all'
    ? subjectsData
    : subjectsData.filter(s => s.category === category);

  if (filtered.length === 0) {
    grid.innerHTML = '<p style="grid-column: 1/-1; text-align:center;color:var(--text-secondary);">No subjects in this category.</p>';
    return;
  }
  grid.innerHTML = filtered.map(subjectCard).join('');
}

// ---------------------------------------------------------------------------
// Search
// ---------------------------------------------------------------------------

function tokens(query) {
  // Split on whitespace AND "&" so "voltage & resistance" becomes
  // ["voltage", "resistance"] (single "&" is treated as a divider, not a token).
  return String(query)
    .toLowerCase()
    .split(/[\s&]+/)
    .map(t => t.trim())
    .filter(t => t.length > 0);
}

function containsAll(text, tokens) {
  if (tokens.length === 0) return false;
  return tokens.every(tok => text.indexOf(tok) >= 0);
}

function matchesSubject(subject, q) {
  const toks = tokens(q);
  if (toks.length === 0) return false;
  const haystacks = [
    (subject.name || ''),
    (subject.category || ''),
    (subject.id || ''),
    ...(subject.aliases || [])
  ].map(s => s.toLowerCase());
  return toks.every(tok => haystacks.some(h => h.indexOf(tok) >= 0));
}

function matchesTopic(topic, q) {
  const toks = tokens(q);
  if (toks.length === 0) return false;
  return containsAll((topic.searchText || ''), toks);
}

// Live search across the cached subjects + topics index.  Falls back to the
// default grid when the query is empty.
function runSearch(query) {
  const grid = document.getElementById('subjects-grid');
  if (!grid) return;
  const q = (query || '').toLowerCase().trim();

  // Empty input -> restore the default subjects grid.
  if (!q) {
    renderSubjects('all');
    return;
  }

  // Index not ready yet -> load it, then re-run.
  if (!searchIndexLoaded) {
    grid.innerHTML = '<p style="grid-column:1/-1;text-align:center;color:var(--text-secondary);">Loading search index…</p>';
    ensureSearchIndex().then(() => runSearch(query));
    return;
  }

  const subjects = (searchIndex.subjects || []).filter(s => matchesSubject(s, q));
  const topics = (searchIndex.topics || []).filter(t => matchesTopic(t, q));
  const topicSubset = topics.slice(0, SEARCH_TOPIC_LIMIT);

  if (subjects.length === 0 && topics.length === 0) {
    grid.innerHTML =
      `<p style="grid-column:1/-1;text-align:center;color:var(--text-secondary);">
         No results for &ldquo;${escapeHtml(query)}&rdquo;.  Try a subject name or topic keyword.
       </p>`;
    return;
  }

  let html = '';
  if (subjects.length > 0) {
    html += `<h3 class="search-section-header">Subjects (${subjects.length})</h3>`;
    html += subjects.map(subjectCard).join('');
  }
  if (topicSubset.length > 0) {
    const extraCount = topics.length - topicSubset.length;
    const header = extraCount > 0
      ? `Topics (${topics.length} — showing first ${topicSubset.length})`
      : `Topics (${topics.length})`;
    html += `<h3 class="search-section-header">${escapeHtml(header)}</h3>`;
    html += topicSubset.map(topicCard).join('');
  }
  grid.innerHTML = html;
}

// Backwards-compatible button handler.
function handleSearch() {
  const input = document.getElementById('search');
  if (input) runSearch(input.value);
}

// ---------------------------------------------------------------------------
// Misc UI handlers
// ---------------------------------------------------------------------------

function closeMobileMenu() {
  const nav = document.getElementById('mobile-nav');
  const overlay = document.getElementById('overlay');
  if (nav) nav.classList.remove('open');
  if (overlay) overlay.classList.remove('active');
}

function filterByBoard(board) {
  const grid = document.getElementById('subjects-grid');
  if (!grid) return;
  const filtered = subjectsData.filter(s => (s.boards || []).includes(board));

  grid.innerHTML = filtered.map(s => `
    <a href="${s.id}.html" class="subject-card">
      <div class="subject-category">${s.category}</div>
      <h3>${escapeHtml(s.name)}</h3>
      <div class="paper-count">${s.papers || 0} paper${(s.papers || 0) > 1 ? 's' : ''}</div>
    </a>`).join('');

  // Clear any active search query so the user sees what they filtered by.
  const searchInput = document.getElementById('search');
  if (searchInput) searchInput.value = '';

  document.querySelectorAll('.category-tab').forEach(t => t.classList.remove('active'));
  const subjectsSection = document.getElementById('subjects');
  if (subjectsSection) subjectsSection.scrollIntoView({ behavior: 'smooth' });
}

function openSubject(subjectId) {
  const landingPages = ['mathematics', 'english-language', 'english-literature', 'combined-science', 'biology', 'chemistry', 'physics', 'geography', 'history', 'pe', 'computer-science', 'religious-studies', 'french', 'german', 'spanish', 'art-and-design', 'music', 'drama', 'design-and-technology', 'business', 'economics', 'psychology', 'sociology', 'citizenship-studies', 'media-studies', 'food-preparation-nutrition', 'latin', 'astronomy', 'geology', 'ancient-history', 'classical-civilisation', 'law', 'dance', 'film-studies', 'electronics', 'engineering', 'statistics'];
  if (landingPages.includes(subjectId)) {
    window.location.href = `${subjectId}.html`;
  } else {
    const subject = subjectsData.find(s => s.id === subjectId);
    if (subject) {
      alert(`${subject.name} revision notes coming soon!\n\nCheck back later for full topic coverage.`);
    }
  }
}

// ---------------------------------------------------------------------------
// Theme handling
// ---------------------------------------------------------------------------

function toggleTheme() {
  const root = document.documentElement;
  const icon = document.getElementById('theme-toggle');
  if (root.classList.contains('light-mode')) {
    root.classList.remove('light-mode');
    if (icon) icon.textContent = '🌙';
    localStorage.setItem('gcserevise-theme', 'dark');
  } else {
    root.classList.add('light-mode');
    if (icon) icon.textContent = '☀️';
    localStorage.setItem('gcserevise-theme', 'light');
  }
}

function loadTheme() {
  const savedTheme = localStorage.getItem('gcserevise-theme');
  const icon = document.getElementById('theme-toggle');
  if (savedTheme === 'light') {
    document.documentElement.classList.add('light-mode');
    if (icon) icon.textContent = '☀️';
  }
}

// ---------------------------------------------------------------------------
// Bootstrap
// ---------------------------------------------------------------------------

document.addEventListener('DOMContentLoaded', function () {
  loadTheme();

  // Theme button is present on every page that loads this script.
  const themeToggle = document.getElementById('theme-toggle');
  if (themeToggle) themeToggle.addEventListener('click', toggleTheme);

  // Home page only: subjects grid, category tabs, search box, mobile menu.
  if (document.getElementById('subjects-grid')) {
    loadSubjects();
  }

  const tabs = document.querySelectorAll('.category-tab');
  tabs.forEach(tab => {
    tab.addEventListener('click', function () {
      tabs.forEach(t => t.classList.remove('active'));
      this.classList.add('active');
      const searchInput = document.getElementById('search');
      if (searchInput) searchInput.value = '';
      renderSubjects(this.dataset.category);
    });
  });

  document.querySelectorAll('.board-card').forEach(card => {
    card.addEventListener('click', () => filterByBoard(card.dataset.board));
  });

  const mobileMenuBtn = document.getElementById('mobile-menu-btn');
  if (mobileMenuBtn) {
    mobileMenuBtn.addEventListener('click', () => {
      const nav = document.getElementById('mobile-nav');
      const overlay = document.getElementById('overlay');
      if (nav) nav.classList.add('open');
      if (overlay) overlay.classList.add('active');
    });
  }
  const closeMobile = document.getElementById('close-mobile');
  if (closeMobile) closeMobile.addEventListener('click', closeMobileMenu);
  const overlay = document.getElementById('overlay');
  if (overlay) overlay.addEventListener('click', closeMobileMenu);

  // Search box (home page only).
  const searchInput = document.getElementById('search');
  if (searchInput) {
    // Start pre-fetching the search index as soon as the user focuses the
    // box so it is ready by the time they type the first character.
    searchInput.addEventListener('focus', () => { ensureSearchIndex(); });

    searchInput.addEventListener('input', () => {
      runSearch(searchInput.value);
    });

    // Enter: make sure the search renders (live filtering already does, but
    // Enter also shouldn't accidentally navigate the page).
    searchInput.addEventListener('keydown', e => {
      if (e.key === 'Enter') {
        e.preventDefault();
        ensureSearchIndex().then(() => runSearch(searchInput.value));
      }
    });
  }
});
