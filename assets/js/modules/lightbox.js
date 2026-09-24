export function initLightbox() {
  const root = document.querySelector("[data-lightbox]");

  if (!root) {
    return;
  }

  const dialog = root.querySelector("[data-lightbox-dialog]");
  const image = root.querySelector("[data-lightbox-image]");
  const caption = root.querySelector("[data-lightbox-caption]");
  const closeButton = root.querySelector("[data-lightbox-close]");
  const triggers = Array.from(document.querySelectorAll("[data-lightbox-open]"));

  if (!dialog || !image || !closeButton || !triggers.length) {
    return;
  }

  let lastTrigger = null;

  function openLightbox(trigger) {
    const src = trigger.getAttribute("data-lightbox-src");
    const alt = trigger.getAttribute("data-lightbox-alt") || "";
    const title = trigger.getAttribute("data-lightbox-caption") || "";

    if (!src) {
      return;
    }

    lastTrigger = trigger;
    image.src = src;
    image.alt = alt;

    if (caption) {
      caption.textContent = title;
      caption.hidden = !title;
    }

    root.hidden = false;
    document.body.classList.add("lightbox-open");
    closeButton.focus();
  }

  function closeLightbox() {
    root.hidden = true;
    image.removeAttribute("src");
    image.alt = "";

    if (caption) {
      caption.textContent = "";
      caption.hidden = true;
    }

    document.body.classList.remove("lightbox-open");

    if (lastTrigger) {
      lastTrigger.focus();
      lastTrigger = null;
    }
  }

  triggers.forEach((trigger) => {
    trigger.addEventListener("click", () => {
      openLightbox(trigger);
    });
  });

  closeButton.addEventListener("click", closeLightbox);

  root.addEventListener("click", (event) => {
    if (event.target === root) {
      closeLightbox();
    }
  });

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && !root.hidden) {
      closeLightbox();
    }
  });
}
