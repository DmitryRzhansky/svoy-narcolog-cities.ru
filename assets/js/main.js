import { initConsultModal } from "./modules/consult-modal.js";
import { initDropdowns } from "./modules/dropdown.js";
import { initFaq } from "./modules/faq.js";
import { initFloatBar } from "./modules/float-bar.js";
import { initHeaderScroll } from "./modules/header-scroll.js";
import { initLightbox } from "./modules/lightbox.js";
import { initMenu } from "./modules/menu.js";
import { initPricesTabs } from "./modules/prices-tabs.js";
import { initCasesSlider } from "./modules/cases-slider.js";
import { initReviewsSlider } from "./modules/reviews-slider.js";
import { initSlider } from "./modules/slider.js";

function initApp() {
  initMenu();
  initHeaderScroll();
  initDropdowns();
  initSlider();
  initPricesTabs();
  initReviewsSlider();
  initCasesSlider();
  initLightbox();
  initConsultModal();
  initFaq();
  initFloatBar();
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", initApp);
} else {
  initApp();
}
