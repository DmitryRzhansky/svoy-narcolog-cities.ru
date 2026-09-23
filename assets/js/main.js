import { initDropdowns } from "./modules/dropdown.js";
import { initMenu } from "./modules/menu.js";

function initApp() {
  initMenu();
  initDropdowns();
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", initApp);
} else {
  initApp();
}
