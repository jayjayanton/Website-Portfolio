/* Small progressive enhancements shared by all pages. Content works without JS. */
(() => {
  const toggle = document.querySelector('.nav-toggle');
  const navigation = document.getElementById('site-nav');

  if (toggle && navigation) {
    const mobile = window.matchMedia('(max-width: 48rem)');
    const setOpen = (open, returnFocus = false) => {
      navigation.classList.toggle('is-open', open);
      toggle.setAttribute('aria-expanded', String(open));
      toggle.textContent = open ? (toggle.dataset.labelClose || 'Close') : (toggle.dataset.labelOpen || 'Menu');
      if (returnFocus) toggle.focus();
    };

    toggle.hidden = false;
    document.documentElement.classList.add('js');
    toggle.addEventListener('click', () => {
      setOpen(toggle.getAttribute('aria-expanded') !== 'true');
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
  });
})();
