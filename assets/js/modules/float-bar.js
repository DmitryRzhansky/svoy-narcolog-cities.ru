const TIP_DELAY_MS = 5000;
const TOP_SHOW_OFFSET = 400;
const FOOTER_GAP = 16;
const DEFAULT_OFFSET = 16;

export function initFloatBar() {
  const root = document.querySelector("[data-float-bar]");

  if (!root) {
    return;
  }

  const footer = document.querySelector("[data-footer]");
  const chat = root.querySelector("[data-float-chat]");
  const toggle = root.querySelector("[data-float-chat-toggle]");
  const channels = root.querySelector("[data-float-channels]");
  const topButton = root.querySelector("[data-float-top]");
  const tip = root.querySelector("[data-float-tip]");
  const tipClose = root.querySelector("[data-float-tip-close]");

  if (!chat || !toggle || !channels || !topButton) {
    return;
  }

  let tipDismissed = false;
  let tipTimerId = null;
  let isOpen = false;

  function setOpen(nextOpen) {
    isOpen = nextOpen;
    chat.classList.toggle("float-bar__chat--open", isOpen);
    toggle.setAttribute("aria-expanded", String(isOpen));
    toggle.setAttribute("aria-label", isOpen ? "Закрыть чат" : "Открыть чат");
    channels.hidden = !isOpen;

    if (isOpen) {
      hideTip(true);
    }
  }

  function hideTip(permanent) {
    if (!tip) {
      return;
    }

    if (permanent) {
      tipDismissed = true;
    }

    if (tipTimerId !== null) {
      window.clearTimeout(tipTimerId);
      tipTimerId = null;
    }

    tip.hidden = true;
  }

  function showTip() {
    if (!tip || tipDismissed || isOpen) {
      return;
    }

    tip.hidden = false;
  }

  function updateTopVisibility() {
    topButton.hidden = window.scrollY < TOP_SHOW_OFFSET;
  }

  function updateFooterOffset() {
    if (!footer) {
      root.style.setProperty("--float-bottom", `${DEFAULT_OFFSET}px`);
      return;
    }

    const footerTop = footer.getBoundingClientRect().top;
    const overlap = window.innerHeight - footerTop;
    const bottom = overlap > 0 ? overlap + FOOTER_GAP : DEFAULT_OFFSET;

    root.style.setProperty("--float-bottom", `${bottom}px`);
  }

  function onScrollOrResize() {
    updateTopVisibility();
    updateFooterOffset();
  }

  toggle.addEventListener("click", () => {
    setOpen(!isOpen);
  });

  topButton.addEventListener("click", () => {
    const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    window.scrollTo({
      top: 0,
      behavior: reduceMotion ? "auto" : "smooth",
    });
  });

  if (tipClose) {
    tipClose.addEventListener("click", () => {
      hideTip(true);
    });
  }

  if (tip) {
    tip.addEventListener("click", (event) => {
      if (event.target.closest("[data-float-tip-close]")) {
        return;
      }

      hideTip(true);
      setOpen(true);
    });

    tip.style.cursor = "pointer";
  }

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && isOpen) {
      setOpen(false);
    }
  });

  document.addEventListener("click", (event) => {
    if (!isOpen) {
      return;
    }

    if (!root.contains(event.target)) {
      setOpen(false);
    }
  });

  window.addEventListener("scroll", onScrollOrResize, { passive: true });
  window.addEventListener("resize", onScrollOrResize);

  onScrollOrResize();

  tipTimerId = window.setTimeout(() => {
    tipTimerId = null;
    showTip();
  }, TIP_DELAY_MS);
}
