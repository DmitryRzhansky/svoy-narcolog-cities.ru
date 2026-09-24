export function initReviewsSlider() {
  const root = document.querySelector("[data-reviews]");

  if (!root) {
    return;
  }

  const track = root.querySelector("[data-reviews-track]");
  const prevButton = root.querySelector("[data-reviews-prev]");
  const nextButton = root.querySelector("[data-reviews-next]");
  const items = track ? [...track.querySelectorAll(".reviews__item")] : [];

  if (!track || !prevButton || !nextButton || items.length < 2) {
    return;
  }

  function getStep() {
    const item = items[0];
    const styles = getComputedStyle(track);
    const gap = Number.parseFloat(styles.columnGap || styles.gap) || 0;

    return item.getBoundingClientRect().width + gap;
  }

  function updateButtons() {
    const maxScroll = Math.max(0, track.scrollWidth - track.clientWidth);
    const atStart = track.scrollLeft <= 4;
    const atEnd = track.scrollLeft >= maxScroll - 4;

    prevButton.disabled = atStart;
    nextButton.disabled = atEnd;
  }

  function scrollByStep(direction) {
    track.scrollBy({
      left: direction * getStep(),
      behavior: "smooth",
    });
  }

  prevButton.addEventListener("click", () => {
    scrollByStep(-1);
  });

  nextButton.addEventListener("click", () => {
    scrollByStep(1);
  });

  track.addEventListener("scroll", updateButtons, { passive: true });
  window.addEventListener("resize", updateButtons);
  updateButtons();
}
