export function initPricesTabs() {
  const root = document.querySelector("[data-prices]");

  if (!root) {
    return;
  }

  const tabs = Array.from(root.querySelectorAll("[data-prices-tab]"));
  const panels = Array.from(root.querySelectorAll("[data-prices-panel]"));

  if (!tabs.length || !panels.length) {
    return;
  }

  function activateTab(nextTab) {
    tabs.forEach((tab) => {
      const isActive = tab === nextTab;
      const panelId = tab.getAttribute("aria-controls");
      const panel = panelId ? root.querySelector(`#${CSS.escape(panelId)}`) : null;

      tab.classList.toggle("prices__tab--active", isActive);
      tab.setAttribute("aria-selected", String(isActive));
      tab.tabIndex = isActive ? 0 : -1;

      if (panel) {
        panel.hidden = !isActive;
      }
    });
  }

  tabs.forEach((tab, index) => {
    tab.addEventListener("click", () => {
      activateTab(tab);
    });

    tab.addEventListener("keydown", (event) => {
      let nextIndex = index;

      if (event.key === "ArrowRight" || event.key === "ArrowDown") {
        nextIndex = (index + 1) % tabs.length;
      } else if (event.key === "ArrowLeft" || event.key === "ArrowUp") {
        nextIndex = (index - 1 + tabs.length) % tabs.length;
      } else if (event.key === "Home") {
        nextIndex = 0;
      } else if (event.key === "End") {
        nextIndex = tabs.length - 1;
      } else {
        return;
      }

      event.preventDefault();
      tabs[nextIndex].focus();
      activateTab(tabs[nextIndex]);
    });
  });
}
