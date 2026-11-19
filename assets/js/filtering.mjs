/** Pure catalogue filtering and URL state shared by the browser and Node tests. */
export const CATEGORIES = Object.freeze([
  'all', 'geospatial', 'data-science', 'engineering', 'web', 'vision',
]);
export const STAGES = Object.freeze(['all', 'published', 'delivered', 'development']);

const CATEGORY_LABELS = Object.freeze({
  geospatial: 'Geospatial analytics',
  'data-science': 'Data science',
  engineering: 'Data engineering',
  web: 'Web development',
  vision: 'Computer vision',
});
const STAGE_LABELS = Object.freeze({
  published: 'Published live',
  delivered: 'Applied work',
  development: 'In development',
});

export function normalizeText(value) {
  return (typeof value === 'string' ? value : '')
    .normalize('NFKD')
    .replace(/\p{M}+/gu, '')
    .toLowerCase()
    .replace(/\s+/gu, ' ')
    .trim();
}

export function normalizeFilterState(state = {}) {
  const source = state && typeof state === 'object' ? state : {};
  return {
    q: typeof source.q === 'string' ? source.q.replace(/\s+/gu, ' ').trim() : '',
    category: CATEGORIES.includes(source.category) ? source.category : 'all',
    stage: STAGES.includes(source.stage) ? source.stage : 'all',
  };
}

function strings(value) {
  if (typeof value === 'string') return [value];
  if (Array.isArray(value)) return value.flatMap(strings);
  return [];
}

function searchableText(project) {
  const capabilities = [...strings(project.categories), ...strings(project.topics)];
  return normalizeText([
    project.slug,
    project.title,
    project.summary,
    project.role,
    project.context,
    project.status,
    project.status_key,
    ...strings(project.technologies),
    ...capabilities,
    ...capabilities.map(value => CATEGORY_LABELS[value] || ''),
    ...strings(project.category_labels),
    ...strings(project.categoryLabels),
    ...strings(project.search_aliases),
    STAGE_LABELS[project.status_key] || '',
  ].filter(value => typeof value === 'string').join(' '));
}

/** AND-match query terms, capability and stage; retain the original record order. */
export function filterProjects(projects, filters = {}) {
  if (!Array.isArray(projects)) return [];
  const { q, category, stage } = normalizeFilterState(filters);
  const terms = normalizeText(q).split(' ').filter(Boolean);
  return projects.filter(project => {
    if (!project || typeof project !== 'object') return false;
    const capabilities = [...strings(project.categories), ...strings(project.topics)];
    if (category !== 'all' && !capabilities.includes(category)) return false;
    if (stage !== 'all' && project.status_key !== stage) return false;
    if (terms.length === 0) return true;
    const text = searchableText(project);
    return terms.every(term => text.includes(term));
  });
}

/** Accept a URL, URLSearchParams or a query string such as location.search. */
export function readFilterState(search = '') {
  const params = search instanceof URL
    ? search.searchParams
    : search instanceof URLSearchParams
      ? search
      : new URLSearchParams(typeof search === 'string' ? search : '');
  return normalizeFilterState({
    q: params.get('q'),
    category: params.get('category'),
    stage: params.get('stage'),
  });
}

/** Return a new URL; retain unrelated parameters and the fragment without mutation. */
export function buildFilterUrl(currentUrl, filters = {}) {
  const url = new URL(currentUrl instanceof URL ? currentUrl.href : currentUrl);
  const { q, category, stage } = normalizeFilterState(filters);
  for (const key of ['q', 'category', 'stage']) url.searchParams.delete(key);
  if (q) url.searchParams.set('q', q);
  if (category !== 'all') url.searchParams.set('category', category);
  if (stage !== 'all') url.searchParams.set('stage', stage);
  return url;
}
