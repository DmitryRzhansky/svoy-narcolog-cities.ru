export function initDropdowns() {
  const items = [...document.querySelectorAll("[data-dropdown]")];

  if (!items.length) {
    return;
  }

  const desktopQuery = window.matchMedia("(min-width: 64rem)");
  const viewportGap = 12;

  const getToggle = (item) => item.querySelector(":scope > [data-dropdown-toggle]");

  const getMenu = (item) =>
    item.querySelector(":scope > .nav__dropdown, :scope > .nav__subdropdown");

  const clearMenuPosition = (menu) => {
    if (!menu) {
      return;
    }

    menu.style.position = "";
    menu.style.top = "";
    menu.style.bottom = "";
    menu.style.left = "";
    menu.style.right = "";
  };

  const fitMenuToViewport = (item) => {
    const menu = getMenu(item);

    if (!menu || !desktopQuery.matches) {
      return;
    }

    clearMenuPosition(menu);

    const isSubmenu = menu.classList.contains("nav__subdropdown");
    const viewportHeight = window.innerHeight;
    const viewportWidth = window.innerWidth;
    const rect = menu.getBoundingClientRect();

    if (isSubmenu) {
      const itemRect = item.getBoundingClientRect();
      const submenuGap = 6;
      let top = itemRect.top;
      let left = itemRect.right + submenuGap;

      if (top + rect.height > viewportHeight - viewportGap) {
        top = Math.max(viewportGap, viewportHeight - viewportGap - rect.height);
      }

      if (left + rect.width > viewportWidth - viewportGap) {
        left = Math.max(viewportGap, itemRect.left - rect.width - submenuGap);
      }

      menu.style.position = "fixed";
      menu.style.top = `${top}px`;
      menu.style.left = `${left}px`;
      menu.style.right = "auto";
      menu.style.bottom = "auto";
      return;
    }

    const overflowBottom = rect.bottom - (viewportHeight - viewportGap);

    if (overflowBottom > 0) {
      menu.style.top = `calc(100% + 0.85rem - ${overflowBottom}px)`;
    }
  };

  const setOpen = (item, open) => {
    item.classList.toggle("is-open", open);

    const button = getToggle(item);

    if (button) {
      button.setAttribute("aria-expanded", String(open));
    }

    if (!open) {
      clearMenuPosition(getMenu(item));

      item.querySelectorAll("[data-dropdown].is-open").forEach((nested) => {
        nested.classList.remove("is-open");

        const nestedButton = getToggle(nested);

        if (nestedButton) {
          nestedButton.setAttribute("aria-expanded", "false");
        }

        clearMenuPosition(getMenu(nested));
      });

      return;
    }

    window.requestAnimationFrame(() => {
      fitMenuToViewport(item);
    });
  };

  const closeConflicting = (except) => {
    items.forEach((item) => {
      if (item === except || item.contains(except)) {
        return;
      }

      setOpen(item, false);
    });
  };

  const closeAll = () => {
    items.forEach((item) => {
      setOpen(item, false);
    });
  };

  items.forEach((item) => {
    const button = getToggle(item);
    let closeTimer = 0;

    if (!button) {
      return;
    }

    const openItem = () => {
      window.clearTimeout(closeTimer);
      closeConflicting(item);
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
      closeConflicting(item);
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

  window.addEventListener(
    "resize",
    () => {
      if (!desktopQuery.matches) {
        items.forEach((item) => clearMenuPosition(getMenu(item)));
        return;
      }

      items.forEach((item) => {
        if (item.classList.contains("is-open")) {
          fitMenuToViewport(item);
        }
      });
    },
    { passive: true },
  );
}
