(() => {
  const carousel = document.querySelector("[data-research-carousel]");
  if (!carousel) return;
  const slides = Array.from(carousel.querySelectorAll("[data-slide]"));
  const dots = Array.from(carousel.querySelectorAll("[data-go]"));
  const counter = carousel.querySelector(".research-carousel__counter");
  let current = 0;

  function show(index) {
    current = (index + slides.length) % slides.length;
    slides.forEach((slide, i) => {
      slide.hidden = i !== current;
      slide.setAttribute("aria-hidden", String(i !== current));
    });
    dots.forEach((dot, i) => {
      if (i === current) dot.setAttribute("aria-current", "true");
      else dot.removeAttribute("aria-current");
    });
    counter.textContent = `${current + 1} / ${slides.length}`;
  }

  carousel.querySelector("[data-prev]").addEventListener("click", () => show(current - 1));
  carousel.querySelector("[data-next]").addEventListener("click", () => show(current + 1));
  dots.forEach((dot, i) => dot.addEventListener("click", () => show(i)));
  carousel.addEventListener("keydown", (event) => {
    if (event.key === "ArrowLeft") { event.preventDefault(); show(current - 1); }
    if (event.key === "ArrowRight") { event.preventDefault(); show(current + 1); }
  });
  show(0);
})();
