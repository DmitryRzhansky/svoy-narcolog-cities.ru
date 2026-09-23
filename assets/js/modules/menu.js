export function initMenu() {
  const header = document.querySelector("[data-header]");
  const toggle = document.querySelector("[data-menu-toggle]");
  const menu = document.querySelector("[data-menu]");

  if (!header || !toggle || !menu) {
    return;
  }

  const desktopQuery = window.matchMedia("(min-width: 64rem)");

  const setOpen = (open) => {
    const isDesktop = desktopQuery.matches;

    header.classList.toggle("header--open", open && !isDesktop);
    toggle.setAttribute("aria-expanded", String(open && !isDesktop));
    toggle.setAttribute("aria-label", open && !isDesktop ? "Закрыть меню" : "Открыть меню");
    document.body.classList.toggle("body--lock", open && !isDesktop);

    if (open && !isDesktop) {
      menu.setAttribute("role", "dialog");
      menu.setAttribute("aria-modal", "true");
      menu.setAttribute("aria-label", "Меню");
      return;
    }

    menu.removeAttribute("role");
    menu.removeAttribute("aria-modal");
    menu.removeAttribute("aria-label");
  };

  toggle.addEventListener("click", () => {
    const isOpen = header.classList.contains("header--open");
    setOpen(!isOpen);

    if (!isOpen) {
      const firstLink = menu.querySelector("a, button");
      if (firstLink) {
        firstLink.focus();
      }
    }
  });

  menu.addEventListener("click", (event) => {
    const link = event.target.closest("a");

    if (!link || desktopQuery.matches) {
      return;
    }

    setOpen(false);
  });

  document.addEventListener("keydown", (event) => {
    const isOpen = header.classList.contains("header--open");

    if (!isOpen || desktopQuery.matches) {
      return;
    }

    if (event.key === "Escape") {
      setOpen(false);
      toggle.focus();
      return;
    }

    if (event.key !== "Tab") {
      return;
    }

    const focusable = [toggle, ...menu.querySelectorAll("a, button")];
    const currentIndex = focusable.indexOf(document.activeElement);
    const lastIndex = focusable.length - 1;

    if (event.shiftKey && currentIndex <= 0) {
      event.preventDefault();
      focusable[lastIndex].focus();
    } else if (!event.shiftKey && currentIndex === lastIndex) {
      event.preventDefault();
      focusable[0].focus();
    }
  });

  desktopQuery.addEventListener("change", () => {
    setOpen(false);
  });
}
