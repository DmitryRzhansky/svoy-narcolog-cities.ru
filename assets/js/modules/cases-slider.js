export function initCasesSlider() {
  const root = document.querySelector("[data-cases]");

  if (!root) {
    return;
  }

  const track = root.querySelector("[data-cases-track]");
  const prevButtons = [...root.querySelectorAll("[data-cases-prev]")];
  const nextButtons = [...root.querySelectorAll("[data-cases-next]")];
  const items = track ? [...track.querySelectorAll(".cases__item")] : [];

  if (!track || prevButtons.length === 0 || nextButtons.length === 0 || items.length < 2) {
    return;
  }

  function getStep() {
    return track.clientWidth;
  }

  function updateButtons() {
    const maxScroll = Math.max(0, track.scrollWidth - track.clientWidth);
    const atStart = track.scrollLeft <= 4;
    const atEnd = track.scrollLeft >= maxScroll - 4;

    prevButtons.forEach((button) => {
      button.disabled = atStart;
    });

    nextButtons.forEach((button) => {
      button.disabled = atEnd;
    });
  }

  function scrollByStep(direction) {
    track.scrollBy({
      left: direction * getStep(),
      behavior: "smooth",
    });
  }

  prevButtons.forEach((button) => {
    button.addEventListener("click", () => {
      scrollByStep(-1);
    });
  });

  nextButtons.forEach((button) => {
    button.addEventListener("click", () => {
      scrollByStep(1);
    });
  });

  track.addEventListener("scroll", updateButtons, { passive: true });
  window.addEventListener("resize", updateButtons);
  updateButtons();
}
