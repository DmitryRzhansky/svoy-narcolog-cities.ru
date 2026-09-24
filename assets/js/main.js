import { initDropdowns } from "./modules/dropdown.js";
import { initMenu } from "./modules/menu.js";
import { initPricesTabs } from "./modules/prices-tabs.js";
import { initSlider } from "./modules/slider.js";

function initApp() {
  initMenu();
  initDropdowns();
  initSlider();
  initPricesTabs();
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", initApp);
} else {
  initApp();
}
