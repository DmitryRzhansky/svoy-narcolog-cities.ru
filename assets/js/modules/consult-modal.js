export function initConsultModal() {
  const modal = document.querySelector('[data-modal="consult"]');

  if (!modal) {
    return;
  }

  const dialog = modal.querySelector("[data-modal-dialog]");
  const openButtons = Array.from(document.querySelectorAll('[data-modal-open="consult"]'));
  const closeButtons = Array.from(modal.querySelectorAll("[data-modal-close]"));
  const form = modal.querySelector("[data-consult-form]");
  const firstField = modal.querySelector("#consult-name");

  if (!dialog || !openButtons.length) {
    return;
  }

  let lastTrigger = null;

  function openModal(trigger) {
    lastTrigger = trigger || null;
    modal.hidden = false;
    document.body.classList.add("modal-open");

    if (firstField) {
      firstField.focus();
    } else {
      const closeButton = modal.querySelector("[data-modal-close]");

      if (closeButton) {
        closeButton.focus();
      }
    }
  }

  function closeModal() {
    modal.hidden = true;
    document.body.classList.remove("modal-open");

    if (lastTrigger) {
      lastTrigger.focus();
      lastTrigger = null;
    }
  }

  openButtons.forEach((button) => {
    button.addEventListener("click", () => {
      openModal(button);
    });
  });

  closeButtons.forEach((button) => {
    button.addEventListener("click", closeModal);
  });

  modal.addEventListener("click", (event) => {
    if (event.target === modal) {
      closeModal();
    }
  });

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && !modal.hidden) {
      closeModal();
    }
  });

  if (form) {
    form.addEventListener("submit", (event) => {
      event.preventDefault();
    });
  }
}
