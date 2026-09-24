export function initFaq() {
  const root = document.querySelector("[data-faq]");

  if (!root) {
    return;
  }

  const items = Array.from(root.querySelectorAll("[data-faq-item]"));

  if (!items.length) {
    return;
  }

  function setOpen(item, isOpen) {
    const toggle = item.querySelector("[data-faq-toggle]");
    const panel = item.querySelector("[data-faq-panel]");

    if (!toggle || !panel) {
      return;
    }

    item.classList.toggle("faq-item--open", isOpen);
    toggle.setAttribute("aria-expanded", String(isOpen));
    panel.setAttribute("aria-hidden", String(!isOpen));
  }

  items.forEach((item) => {
    const toggle = item.querySelector("[data-faq-toggle]");

    if (!toggle) {
      return;
    }

    setOpen(item, false);

    toggle.addEventListener("click", () => {
      const isOpen = item.classList.contains("faq-item--open");

      if (isOpen) {
        setOpen(item, false);
        return;
      }

      items.forEach((other) => {
        if (other !== item) {
          setOpen(other, false);
        }
      });

      setOpen(item, true);
    });
  });
}
