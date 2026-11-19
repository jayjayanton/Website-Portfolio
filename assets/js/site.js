/* Small progressive enhancements shared by all pages. Content works without JS. */
(() => {
  const languageLinks = document.querySelectorAll('[data-site-language], [data-cv-language]');
  if (languageLinks.length && document.currentScript?.src) {
    const scriptUrl = new URL(document.currentScript.src);
    const navigationUrl = new URL('./navigation.mjs', scriptUrl);
    navigationUrl.search = scriptUrl.search;
    import(navigationUrl.href)
      .then(({ initializeLanguageSwitcher }) => initializeLanguageSwitcher(languageLinks, window))
      .catch(() => {}); // Native counterpart links remain usable if enhancement fails.
  }

  const toggle = document.querySelector('.nav-toggle');
  const navigation = document.getElementById('site-nav');

  if (toggle && navigation) {
    const mobile = window.matchMedia('(max-width: 64rem)');
    const setOpen = (open, returnFocus = false) => {
      navigation.classList.toggle('is-open', open);
      toggle.setAttribute('aria-expanded', String(open));
      toggle.textContent = open ? (toggle.dataset.labelClose || 'Close') : (toggle.dataset.labelOpen || 'Menu');
      if (returnFocus) toggle.focus();
    };

    toggle.hidden = false;
    document.documentElement.classList.add('js');
    toggle.addEventListener('click', () => {
      const open = toggle.getAttribute('aria-expanded') !== 'true';
      setOpen(open);
      // The responsive menu precedes its trigger in the shared header markup.
      if (open && mobile.matches) navigation.querySelector('a')?.focus();
    });
    navigation.addEventListener('click', (event) => {
      if (mobile.matches && event.target.closest('a')) setOpen(false);
    });
    document.addEventListener('keydown', (event) => {
      if (event.key === 'Escape' && toggle.getAttribute('aria-expanded') === 'true') {
        setOpen(false, true);
      }
    });
    document.addEventListener('click', (event) => {
      if (mobile.matches && toggle.getAttribute('aria-expanded') === 'true'
          && !navigation.contains(event.target) && !toggle.contains(event.target)) {
        setOpen(false);
      }
    });
    mobile.addEventListener('change', () => setOpen(false));
  }

  document.querySelectorAll('[data-print]').forEach((button) => {
    button.addEventListener('click', () => window.print());
    button.hidden = false;
  });
})();
