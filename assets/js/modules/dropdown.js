export function initDropdowns() {
  const items = [...document.querySelectorAll("[data-dropdown]")];

  if (!items.length) {
    return;
  }

  const desktopQuery = window.matchMedia("(min-width: 64rem)");

  const setOpen = (item, open) => {
    item.classList.toggle("is-open", open);
    const button = item.querySelector("[data-dropdown-toggle]");

    if (button) {
      button.setAttribute("aria-expanded", String(open));
    }
  };

  const closeAll = (except) => {
    items.forEach((item) => {
      if (item !== except) {
        setOpen(item, false);
      }
    });
  };

  items.forEach((item) => {
    const button = item.querySelector("[data-dropdown-toggle]");
    let closeTimer = 0;

    if (!button) {
      return;
    }

    const openItem = () => {
      window.clearTimeout(closeTimer);
      closeAll(item);
      setOpen(item, true);
    };

    const scheduleClose = () => {
      window.clearTimeout(closeTimer);
      closeTimer = window.setTimeout(() => {
        setOpen(item, false);
      }, 220);
    };

    button.addEventListener("click", () => {
      const willOpen = !item.classList.contains("is-open");
      closeAll(item);
      setOpen(item, willOpen);
    });

    item.addEventListener("mouseenter", () => {
      if (!desktopQuery.matches) {
        return;
      }

      openItem();
    });

    item.addEventListener("mouseleave", () => {
      if (!desktopQuery.matches) {
        return;
      }

      scheduleClose();
    });

    item.addEventListener("focusout", (event) => {
      if (!desktopQuery.matches) {
        return;
      }

      if (!item.contains(event.relatedTarget)) {
        setOpen(item, false);
      }
    });
  });

  document.addEventListener("keydown", (event) => {
    if (event.key !== "Escape") {
      return;
    }

    closeAll();
  });

  document.addEventListener("click", (event) => {
    if (event.target.closest("[data-dropdown]")) {
      return;
    }

    closeAll();
  });
}
