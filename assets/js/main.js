import { initDropdowns } from "./modules/dropdown.js";
import { initLightbox } from "./modules/lightbox.js";
import { initMenu } from "./modules/menu.js";
import { initPricesTabs } from "./modules/prices-tabs.js";
import { initReviewsScroll } from "./modules/reviews-scroll.js";
import { initSlider } from "./modules/slider.js";

function initApp() {
  initMenu();
  initDropdowns();
  initSlider();
  initPricesTabs();
  initReviewsScroll();
  initLightbox();
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", initApp);
} else {
  initApp();
}
