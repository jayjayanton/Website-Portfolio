import test from 'node:test';
import assert from 'node:assert/strict';
import {
  buildFilterUrl,
  filterProjects,
  normalizeFilterState,
  normalizeText,
  readFilterState,
} from '../assets/js/filtering.mjs';

const records = [
  {
    slug: 'predio-ai', title: 'PredioAI', summary: 'Plans and property analysis.',
    categories: ['geospatial', 'engineering', 'web'], topics: [],
    status_key: 'published', role: 'Creator & sole developer', context: 'Quito, Ecuador',
    technologies: ['Python', 'FastAPI', 'React'],
  },
  {
    slug: 'quito-urban-expansion', title: 'Quito Urban Expansion',
    summary: 'Satellite imagery research for Nayón and Tumbaco.',
    categories: ['geospatial', 'data-science', 'engineering'], topics: ['vision'],
    status_key: 'development', role: 'Researcher', context: 'Quito valleys',
    technologies: ['Sentinel-2', 'Python'],
  },
  {
    slug: 'traffic-camera-pipeline', title: 'Traffic Camera Image Extraction',
    summary: 'Still images and video frames for future model development.',
    categories: ['engineering'], topics: ['vision'], status_key: 'delivered',
    role: 'Data-pipeline developer', context: 'Austin and Jackson Hole',
    technologies: ['OpenCV', 'FFmpeg'],
  },
  {
    slug: 'yuyay-analytics', title: 'Yuyay Analytics', summary: 'A bilingual consulting website.',
    categories: ['web'], topics: [], status_key: 'published',
    role: 'Frontend developer', context: 'Environmental evaluation',
    technologies: ['HTML', 'CSS', 'JavaScript'], category_labels: ['Website design'],
  },
];
const slugs = result => result.map(record => record.slug);

test('the unfiltered catalogue preserves records and source order', () => {
  const result = filterProjects(records);
  assert.deepEqual(result, records);
  assert.notEqual(result, records);
});

test('query terms are conjunctive across title, context, role and tools', () => {
  assert.deepEqual(slugs(filterProjects(records, { q: '  QUITO  FastAPI  creator ' })), ['predio-ai']);
  assert.deepEqual(filterProjects(records, { q: 'FastAPI Sentinel' }), []);
  assert.deepEqual(slugs(filterProjects(records, { q: 'developer opencv' })), ['traffic-camera-pipeline']);
});

test('case, diacritics and irregular Unicode whitespace normalize for matching', () => {
  assert.equal(normalizeText('  NAYO\u0301N\t\n Quito\u00a0 '), 'nayon quito');
  assert.deepEqual(slugs(filterProjects(records, { q: 'NAYON\u00a0satellite' })), ['quito-urban-expansion']);
});

test('capability filtering includes declared topics without inferring capabilities from prose', () => {
  assert.deepEqual(slugs(filterProjects(records, { category: 'vision' })), [
    'quito-urban-expansion', 'traffic-camera-pipeline',
  ]);
  assert.deepEqual(slugs(filterProjects(records, { q: 'computer vision' })), [
    'quito-urban-expansion', 'traffic-camera-pipeline',
  ]);
  assert.deepEqual(slugs(filterProjects(records, { category: 'web' })), ['predio-ai', 'yuyay-analytics']);
});

test('query, capability and work stage apply together', () => {
  assert.deepEqual(slugs(filterProjects(records, {
    q: 'Python Quito', category: 'vision', stage: 'development',
  })), ['quito-urban-expansion']);
  assert.deepEqual(slugs(filterProjects(records, { category: 'vision', stage: 'delivered' })), [
    'traffic-camera-pipeline',
  ]);
  assert.deepEqual(filterProjects(records, { q: 'Python', category: 'vision', stage: 'published' }), []);
});

test('optional display labels are searchable', () => {
  assert.deepEqual(slugs(filterProjects(records, { q: 'website design' })), ['yuyay-analytics']);
  assert.deepEqual(slugs(filterProjects(records, { q: 'data science' })), ['quito-urban-expansion']);
});

test('the same English or Spanish query matches both localized records through aliases', () => {
  const english = [{
    ...records[0],
    search_aliases: ['Planos y análisis de predios', 'Creador y único desarrollador'],
  }];
  const spanish = [{
    ...records[0], summary: 'Planos y análisis de predios', role: 'Creador y único desarrollador',
    search_aliases: ['Plans and property analysis', 'Creator & sole developer'],
  }];
  for (const q of ['property sole', 'PREDIOS único', 'planos Python']) {
    const state = { q, category: 'geospatial', stage: 'published' };
    assert.deepEqual(slugs(filterProjects(english, state)), ['predio-ai']);
    assert.deepEqual(slugs(filterProjects(spanish, state)), ['predio-ai']);
  }
});

test('search aliases never change declared capabilities or delivery stage', () => {
  const projects = [{ ...records[3], search_aliases: ['Computer vision and data science research'] }];
  assert.deepEqual(slugs(filterProjects(projects, { q: 'computer vision' })), ['yuyay-analytics']);
  assert.deepEqual(filterProjects(projects, { q: 'computer vision', category: 'vision' }), []);
  assert.deepEqual(filterProjects(projects, { q: 'research', stage: 'development' }), []);
});

test('optional alias strings and arrays normalize accents while ignoring non-text values', () => {
  const projects = [
    { ...records[0], search_aliases: 'Análisis de geometría' },
    { ...records[1], search_aliases: [['Investigación urbana'], null, 12, { text: 'not searchable' }] },
    { ...records[2], search_aliases: null },
  ];
  assert.deepEqual(slugs(filterProjects(projects, { q: 'analisis GEOMETRIA' })), ['predio-ai']);
  assert.deepEqual(slugs(filterProjects(projects, { q: 'investigacion urbana' })), ['quito-urban-expansion']);
  assert.deepEqual(filterProjects(projects, { q: 'not searchable' }), []);
});

test('regex syntax is treated as literal user text', () => {
  assert.deepEqual(filterProjects(records, { q: '.*' }), []);
  assert.deepEqual(filterProjects(records, { q: '[' }), []);
  const literal = [{ slug: 'literal', title: 'Literal [example] + details', categories: [] }];
  assert.equal(filterProjects(literal, { q: '[example] +' }).length, 1);
});

test('filtering does not modify source records or the input state', () => {
  const copy = structuredClone(records);
  for (const record of copy) {
    for (const value of Object.values(record)) if (Array.isArray(value)) Object.freeze(value);
    Object.freeze(record);
  }
  Object.freeze(copy);
  const state = Object.freeze({ q: '  FastAPI  ', category: 'web', stage: 'published' });
  assert.deepEqual(slugs(filterProjects(copy, state)), ['predio-ai']);
  assert.deepEqual(copy, records);
  assert.equal(state.q, '  FastAPI  ');
});

test('unknown filter values fall back to explicit all defaults', () => {
  assert.deepEqual(normalizeFilterState({ q: ' a\n b ', category: 'malicious', stage: 'draft' }), {
    q: 'a b', category: 'all', stage: 'all',
  });
  assert.deepEqual(normalizeFilterState(null), { q: '', category: 'all', stage: 'all' });
  assert.deepEqual(filterProjects(records, { category: '__proto__', stage: 'anything' }), records);
});

test('empty or malformed searchable fields are safe', () => {
  assert.deepEqual(filterProjects(null, { q: 'test' }), []);
  assert.deepEqual(filterProjects([null, { slug: 'minimal' }], { q: 'minimal' }), [{ slug: 'minimal' }]);
  assert.equal(normalizeText({}), '');
});

test('URL state parses all supported controls and validates category and stage', () => {
  assert.deepEqual(readFilterState('?q=Nay%C3%B3n++Python&category=vision&stage=development'), {
    q: 'Nayón Python', category: 'vision', stage: 'development',
  });
  assert.deepEqual(readFilterState('?category=../web&stage=unknown'), {
    q: '', category: 'all', stage: 'all',
  });
  assert.deepEqual(readFilterState(new URLSearchParams('q=FastAPI')), {
    q: 'FastAPI', category: 'all', stage: 'all',
  });
});

test('URL round trips preserve accents, punctuation, unrelated parameters and fragments', () => {
  const original = new URL('https://example.test/portfolio/projects.html?utm_source=mail#catalogue');
  const state = { q: 'Nayón + C++ & Python', category: 'engineering', stage: 'delivered' };
  const url = buildFilterUrl(original, state);
  assert.deepEqual(readFilterState(url), state);
  assert.equal(url.searchParams.get('utm_source'), 'mail');
  assert.equal(url.hash, '#catalogue');
  assert.equal(url.pathname, '/portfolio/projects.html');
  assert.equal(original.search, '?utm_source=mail');
});

test('reset removes only catalogue parameters and default controls are omitted', () => {
  const url = buildFilterUrl('https://example.test/projects.html?q=old&category=web&stage=published&ref=home#work');
  assert.equal(url.href, 'https://example.test/projects.html?ref=home#work');
  assert.deepEqual(readFilterState(url), { q: '', category: 'all', stage: 'all' });
});

test('duplicate URL controls become a single canonical value', () => {
  const input = new URL('https://example.test/projects.html?q=first&q=second&category=vision&category=web');
  const state = readFilterState(input);
  assert.equal(state.q, 'first');
  assert.equal(state.category, 'vision');
  const output = buildFilterUrl(input, state);
  assert.deepEqual(output.searchParams.getAll('q'), ['first']);
  assert.deepEqual(output.searchParams.getAll('category'), ['vision']);
});

test('URL values remain data rather than markup or executable patterns', () => {
  const q = '<script>alert(1)</script> .*';
  const url = buildFilterUrl('https://example.test/projects.html', { q });
  assert.equal(readFilterState(url).q, q);
  assert.deepEqual(filterProjects(records, readFilterState(url)), []);
});
