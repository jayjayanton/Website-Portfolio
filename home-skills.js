(() => {
  const chips = [...document.querySelectorAll("[data-skill]")];
  const cards = [...document.querySelectorAll("[data-skills]")];
  const status = document.querySelector("[data-skill-status]");
  if (!chips.length || !cards.length) return;
  const selected = new Set();
  const render = () => {
    const all = selected.size === 0;
    let matches = 0;
    cards.forEach(card => {
      const skills = new Set(card.dataset.skills.split(/\s+/));
      const match = all || [...selected].every(skill => skills.has(skill));
      card.classList.toggle("is-muted", !match);
      card.classList.toggle("is-highlighted", !all && match);
      card.hidden = !match;
      if (match) matches++;
    });
    chips.forEach(chip => {
      const active = chip.dataset.skill === "all" ? all : selected.has(chip.dataset.skill);
      chip.classList.toggle("is-active", active);
      chip.setAttribute("aria-pressed", String(active));
    });
    const names = [...selected].map(key => chips.find(c => c.dataset.skill === key)?.textContent.trim()).filter(Boolean);
    status.textContent = all ? "Showing all projects" : `${matches} matching project${matches === 1 ? "" : "s"} · ${names.join(" + ")}`;
  };
  chips.forEach(chip => chip.addEventListener("click", () => {
    const key = chip.dataset.skill;
    if (key === "all") selected.clear();
    else if (selected.has(key)) selected.delete(key);
    else selected.add(key);
    render();
  }));
  render();
})();