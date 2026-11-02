(() => {
  document.querySelectorAll("[data-ow-carousel]").forEach(carousel => {
    const track = carousel.querySelector("[data-track]");
    const slides = [...carousel.querySelectorAll("[data-slide]")];
    const counter = carousel.querySelector("[data-count]");
    let current = 0;
    const update = (i, scroll = true) => {
      current = (i + slides.length) % slides.length;
      counter.textContent = `${current + 1} / ${slides.length}`;
      if (scroll) track.scrollTo({left: slides[current].offsetLeft - slides[0].offsetLeft, behavior: "smooth"});
    };
    carousel.querySelector("[data-prev]").addEventListener("click", () => update(current - 1));
    carousel.querySelector("[data-next]").addEventListener("click", () => update(current + 1));
    let pending;
    track.addEventListener("scroll", () => {
      clearTimeout(pending);
      pending = setTimeout(() => update(Math.round(track.scrollLeft / Math.max(1,track.clientWidth)), false), 90);
    }, {passive:true});
    carousel.addEventListener("keydown", e => {
      if (e.key === "ArrowLeft" || e.key === "ArrowRight") {
        e.preventDefault();
        update(current + (e.key === "ArrowRight" ? 1 : -1));
      }
    });
    update(0, false);
  });
})();