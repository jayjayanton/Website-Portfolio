(() => {
  const carousel = document.querySelector("[data-research-carousel]");
  if (!carousel) return;
  const track = carousel.querySelector(".research-carousel__viewport");
  const slides = [...carousel.querySelectorAll("[data-slide]")];
  const dots = [...carousel.querySelectorAll("[data-go]")];
  const counter = carousel.querySelector(".research-carousel__counter");
  let index = 0;

  function update(i, scroll = true) {
    index = (i + slides.length) % slides.length;
    slides.forEach(slide => { slide.hidden = false; slide.removeAttribute("aria-hidden"); });
    dots.forEach((dot, n) => {
      if (n === index) dot.setAttribute("aria-current", "true");
      else dot.removeAttribute("aria-current");
    });
    counter.textContent = `${index + 1} / ${slides.length}`;
    if (scroll) track.scrollTo({ left: slides[index].offsetLeft - slides[0].offsetLeft, behavior: "smooth" });
  }

  carousel.querySelector("[data-prev]").addEventListener("click", () => update(index - 1));
  carousel.querySelector("[data-next]").addEventListener("click", () => update(index + 1));
  dots.forEach((dot, i) => dot.addEventListener("click", () => update(i)));
  let scrollTimer;
  track.addEventListener("scroll", () => {
    clearTimeout(scrollTimer);
    scrollTimer = setTimeout(() => {
      const nearest = Math.round(track.scrollLeft / Math.max(1, track.clientWidth));
      update(Math.min(slides.length - 1, Math.max(0, nearest)), false);
    }, 100);
  }, { passive: true });
  carousel.addEventListener("keydown", event => {
    if (event.target.tagName === "BUTTON" && ["ArrowLeft","ArrowRight"].includes(event.key)) {
      event.preventDefault();
      update(index + (event.key === "ArrowRight" ? 1 : -1));
    }
  });
  update(0, false);
})();