import { initDropdowns } from "./modules/dropdown.js";
import { initMenu } from "./modules/menu.js";
import { initSlider } from "./modules/slider.js";

function initApp() {
  initMenu();
  initDropdowns();
  initSlider();
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", initApp);
} else {
  initApp();
}
