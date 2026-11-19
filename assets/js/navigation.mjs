/** Preserve location state while using the counterpart path supplied by HTML. */
export function buildLanguageUrl(currentUrl, counterpartHref) {
  const current = new URL(currentUrl instanceof URL ? currentUrl.href : currentUrl);
  const counterpart = new URL(counterpartHref, current);
  counterpart.search = current.search;
  counterpart.hash = current.hash;
  return counterpart;
}

/** Enhance native language links; no locale redirects or history interception. */
export function initializeLanguageSwitcher(links, browserWindow) {
  const counterparts = Array.from(links, link => ({ link, href: link.href }));
  const sync = () => {
    for (const { link, href } of counterparts) {
      link.href = buildLanguageUrl(browserWindow.location.href, href).href;
    }
  };

  for (const event of ['popstate', 'hashchange', 'pageshow', 'portfolio:locationchange']) {
    browserWindow.addEventListener(event, sync);
  }
  for (const { link } of counterparts) {
    // Also cover opening a new tab, a context menu or keyboard activation.
    for (const event of ['pointerdown', 'click', 'contextmenu']) link.addEventListener(event, sync);
  }
  sync();
}
