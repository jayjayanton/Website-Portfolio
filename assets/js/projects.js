// Keep the shared filter logic on the same generated cache version as this entry.
const filteringUrl = new URL('./filtering.mjs', import.meta.url);
filteringUrl.search = new URL(import.meta.url).search;
const {
  buildFilterUrl,
  filterProjects,
  normalizeFilterState,
  readFilterState,
} = await import(filteringUrl.href);

function initializeProjectFilters() {
  const form = document.getElementById('project-filters');
  const search = document.getElementById('project-search');
  const stage = document.getElementById('project-stage');
  const index = document.getElementById('project-index');
  const grid = document.getElementById('project-grid');
  const count = document.getElementById('project-count');
  const empty = document.getElementById('empty-state');
  if (!form || !search || !stage || !index || !grid || !count || !empty) return;

  let projects;
  try {
    projects = JSON.parse(index.textContent);
  } catch {
    return; // Keep the complete, server-rendered catalogue available.
  }
  if (!Array.isArray(projects)) return;
  const cards = [...grid.querySelectorAll('article.project-card[data-project-slug]')];
  const slugs = new Set(projects.map(project => project?.slug));
  if (slugs.has(undefined) || slugs.size !== projects.length || cards.length !== projects.length
      || cards.some(card => !slugs.has(card.dataset.projectSlug))) return;

  const categories = [...form.querySelectorAll('button[data-category]')];
  const resets = [...document.querySelectorAll('[data-reset-filters]')];
  let state = readFilterState(window.location.search);
  let editingQuery = false;

  function render(syncControls = true) {
    const matches = filterProjects(projects, state);
    const visibleSlugs = new Set(matches.map(project => project.slug));
    for (const card of cards) card.hidden = !visibleSlugs.has(card.dataset.projectSlug);
    const filtered = Boolean(state.q || state.category !== 'all' || state.stage !== 'all');
    count.textContent = filtered
      ? `${matches.length} of ${projects.length} projects`
      : `${projects.length} ${projects.length === 1 ? 'project' : 'projects'}`;
    empty.hidden = matches.length !== 0;
    for (const button of resets) button.hidden = !filtered;
    for (const button of categories) {
      button.setAttribute('aria-pressed', String(button.dataset.category === state.category));
    }
    if (syncControls) {
      search.value = state.q;
      stage.value = state.stage;
    }
  }

  function syncUrl(method) {
    const url = buildFilterUrl(window.location.href, state);
    if (url.href !== window.location.href) {
      window.history[method](window.history.state, '', url.href);
    }
  }

  search.addEventListener('input', () => {
    state = normalizeFilterState({ ...state, q: search.value });
    // Leave the raw input intact while typing, including spaces between terms.
    render(false);
    // One query-edit session creates one history entry, rather than one per key.
    syncUrl(editingQuery ? 'replaceState' : 'pushState');
    editingQuery = true;
  });
  search.addEventListener('blur', () => { editingQuery = false; });

  stage.addEventListener('change', () => {
    editingQuery = false;
    state = normalizeFilterState({ ...state, q: search.value, stage: stage.value });
    render();
    syncUrl('pushState');
  });

  for (const button of categories) {
    button.addEventListener('click', () => {
      editingQuery = false;
      state = normalizeFilterState({ ...state, q: search.value, category: button.dataset.category });
      render();
      syncUrl('pushState');
    });
  }

  form.addEventListener('submit', event => {
    event.preventDefault();
    editingQuery = false;
    state = normalizeFilterState({ ...state, q: search.value, stage: stage.value });
    render();
    syncUrl('pushState');
  });

  for (const button of resets) {
    button.addEventListener('click', () => {
      editingQuery = false;
      state = normalizeFilterState();
      render();
      syncUrl('pushState');
      search.focus();
    });
  }

  window.addEventListener('popstate', () => {
    editingQuery = false;
    state = readFilterState(window.location.search);
    render();
  });

  render();
  syncUrl('replaceState');
  form.hidden = false;
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initializeProjectFilters, { once: true });
} else {
  initializeProjectFilters();
}
