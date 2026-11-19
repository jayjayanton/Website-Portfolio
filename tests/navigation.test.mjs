import test from 'node:test';
import assert from 'node:assert/strict';
import {
  buildLanguageUrl,
  initializeLanguageSwitcher,
} from '../assets/js/navigation.mjs';

test('language links retain query values and the fragment under a hosted subpath', () => {
  const current = new URL('https://example.test/portfolio/projects.html?q=Nay%C3%B3n+%2B+C%2B%2B&category=vision&stage=development&ref=home#project-grid');
  const destination = buildLanguageUrl(current, 'es/projects.html');
  assert.equal(destination.pathname, '/portfolio/es/projects.html');
  assert.equal(destination.search, current.search);
  assert.equal(destination.hash, '#project-grid');
  assert.equal(destination.searchParams.get('q'), 'Nayón + C++');
  assert.equal(current.pathname, '/portfolio/projects.html');
});

test('nested case studies follow their supplied counterpart rather than guessing a route', () => {
  const destination = buildLanguageUrl(
    'https://example.test/portfolio/es/projects/predio-ai.html?ref=cv#evidence',
    '../../projects/predio-ai.html',
  );
  assert.equal(destination.href, 'https://example.test/portfolio/projects/predio-ai.html?ref=cv#evidence');
});

test('CV counterpart filenames also preserve location state', () => {
  const current = new URL('https://example.test/portfolio/cv/geospatial-data-engineer-es.html?ref=contact#experience');
  const counterpart = new URL('https://example.test/portfolio/cv/geospatial-data-engineer-en.html');
  assert.equal(
    buildLanguageUrl(current, counterpart).href,
    'https://example.test/portfolio/cv/geospatial-data-engineer-en.html?ref=contact#experience',
  );
  assert.equal(counterpart.search, '');
  assert.equal(counterpart.hash, '');
});

test('clearing filters and anchors removes stale counterpart state', () => {
  const destination = buildLanguageUrl(
    'https://example.test/portfolio/projects.html',
    'es/projects.html?q=old&category=web#old-anchor',
  );
  assert.equal(destination.href, 'https://example.test/portfolio/es/projects.html');
});

class Link extends EventTarget {
  constructor(href) { super(); this.href = href; }
}

class BrowserWindow extends EventTarget {
  constructor(href) { super(); this.location = { href }; }
}

function switcher(href = 'https://example.test/portfolio/projects.html?q=Python#work') {
  const browser = new BrowserWindow(href);
  const links = [
    new Link('https://example.test/portfolio/projects.html'),
    new Link('https://example.test/portfolio/es/projects.html'),
  ];
  initializeLanguageSwitcher(links, browser);
  return { browser, links };
}

function assertCurrentState(browser, links) {
  const current = new URL(browser.location.href);
  assert.deepEqual(links.map(link => new URL(link.href).pathname), [
    '/portfolio/projects.html', '/portfolio/es/projects.html',
  ]);
  for (const link of links) {
    assert.equal(new URL(link.href).search, current.search);
    assert.equal(new URL(link.href).hash, current.hash);
  }
}

test('initial enhancement updates both language links without redirecting', () => {
  const { browser, links } = switcher();
  assertCurrentState(browser, links);
  assert.equal(browser.location.href, 'https://example.test/portfolio/projects.html?q=Python#work');
});

test('live project-filter updates refresh hrefs and remove reset filters', () => {
  const { browser, links } = switcher();
  for (const query of ['?q=planos&category=web&stage=published', '?q=FastAPI', '']) {
    browser.location.href = `https://example.test/portfolio/projects.html${query}#work`;
    browser.dispatchEvent(new Event('portfolio:locationchange'));
    assertCurrentState(browser, links);
  }
});

test('back, forward, fragment changes and restored pages keep counterpart paths intact', () => {
  const { browser, links } = switcher();
  const locations = [
    ['popstate', '?q=previous#work'],
    ['popstate', '?q=forward&category=engineering#work'],
    ['hashchange', '?q=forward&category=engineering#main'],
    ['pageshow', '?q=restored#project-grid'],
  ];
  for (const [event, state] of locations) {
    browser.location.href = `https://example.test/portfolio/projects.html${state}`;
    browser.dispatchEvent(new Event(event));
    assertCurrentState(browser, links);
  }
});

test('activation refreshes late URL changes without preventing native link behavior', () => {
  const { browser, links } = switcher();
  for (const eventName of ['pointerdown', 'click', 'contextmenu']) {
    browser.location.href = `https://example.test/portfolio/projects.html?q=${eventName}#main`;
    const event = new Event(eventName, { cancelable: true });
    links[1].dispatchEvent(event);
    assertCurrentState(browser, links);
    assert.equal(event.defaultPrevented, false);
  }
});
