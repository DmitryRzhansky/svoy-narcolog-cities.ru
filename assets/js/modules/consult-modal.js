import { initPhoneMask, isValidPhone } from "./phone-mask.js";

const SEND_URL = "/send.php";

function setStatus(statusNode, type, text) {
  if (!statusNode) {
    return;
  }

  statusNode.hidden = !text;
  statusNode.textContent = text || "";
  statusNode.classList.remove(
    "consult-form__status--success",
    "consult-form__status--error"
  );

  if (type) {
    statusNode.classList.add(`consult-form__status--${type}`);
  }
}

export function initConsultModal() {
  const modal = document.querySelector('[data-modal="consult"]');

  if (!modal) {
    return;
  }

  const dialog = modal.querySelector("[data-modal-dialog]");
  const openButtons = Array.from(
    document.querySelectorAll('[data-modal-open="consult"]')
  );
  const closeButtons = Array.from(modal.querySelectorAll("[data-modal-close]"));
  const form = modal.querySelector("[data-consult-form]");
  const firstField = modal.querySelector("#consult-name");
  const submitButton = form ? form.querySelector('[type="submit"]') : null;
  let statusNode = form ? form.querySelector("[data-consult-status]") : null;

  if (!dialog || !openButtons.length) {
    return;
  }

  if (form && !statusNode) {
    statusNode = document.createElement("p");
    statusNode.className = "consult-form__status";
    statusNode.setAttribute("data-consult-status", "");
    statusNode.setAttribute("role", "status");
    statusNode.setAttribute("aria-live", "polite");
    statusNode.hidden = true;

    const disclaimer = form.querySelector(".consult-form__disclaimer");

    if (disclaimer) {
      form.insertBefore(statusNode, disclaimer);
    } else {
      form.appendChild(statusNode);
    }
  }

  initPhoneMask(modal);

  let lastTrigger = null;
  let isSubmitting = false;

  function openModal(trigger) {
    lastTrigger = trigger || null;
    modal.hidden = false;
    document.body.classList.add("modal-open");
    setStatus(statusNode, null, "");

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

  if (!form) {
    return;
  }

  form.addEventListener("submit", async (event) => {
    event.preventDefault();

    if (isSubmitting) {
      return;
    }

    const formData = new FormData(form);
    const name = String(formData.get("name") || "").trim();
    const phone = String(formData.get("phone") || "").trim();
    const message = String(formData.get("message") || "").trim();

    if (name.length < 2) {
      setStatus(statusNode, "error", "Укажите имя");
      return;
    }

    if (!isValidPhone(phone)) {
      setStatus(statusNode, "error", "Укажите корректный телефон");
      return;
    }

    formData.set("name", name);
    formData.set("phone", phone);
    formData.set("message", message);
    formData.set("page", window.location.href);

    isSubmitting = true;
    setStatus(statusNode, null, "");

    if (submitButton) {
      submitButton.disabled = true;
    }

    try {
      const response = await fetch(SEND_URL, {
        method: "POST",
        body: formData,
        headers: {
          Accept: "application/json",
        },
      });

      let payload = null;

      try {
        payload = await response.json();
      } catch (error) {
        payload = null;
      }

      if (!response.ok || !payload || !payload.ok) {
        const errorText =
          (payload && payload.error) ||
          "Не удалось отправить заявку. Позвоните нам или напишите в мессенджер.";
        setStatus(statusNode, "error", errorText);
        return;
      }

      form.reset();
      setStatus(
        statusNode,
        "success",
        "Заявка отправлена. Мы свяжемся с вами в ближайшее время."
      );
    } catch (error) {
      setStatus(
        statusNode,
        "error",
        "Не удалось отправить заявку. Проверьте соединение и попробуйте ещё раз."
      );
    } finally {
      isSubmitting = false;

      if (submitButton) {
        submitButton.disabled = false;
      }
    }
  });
}
