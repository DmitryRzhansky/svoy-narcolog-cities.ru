const SCROLL_THRESHOLD = 24;

export function initHeaderScroll() {
  const header = document.querySelector("[data-header]");

  if (!header) {
    return;
  }

  const updateScrolledState = () => {
    const isScrolled = window.scrollY > SCROLL_THRESHOLD;
    header.classList.toggle("header--scrolled", isScrolled);
  };

  updateScrolledState();
  window.addEventListener("scroll", updateScrolledState, { passive: true });
}
