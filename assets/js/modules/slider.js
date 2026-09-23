export function initSlider() {
  const root = document.querySelector("[data-slider]");

  if (!root) {
    return;
  }

  const slides = [...root.querySelectorAll("[data-slider-slide]")];
  const prevButton = root.querySelector("[data-slider-prev]");
  const nextButton = root.querySelector("[data-slider-next]");
  const status = root.querySelector("[data-slider-status]");

  if (slides.length < 2 || !prevButton || !nextButton) {
    return;
  }

  let index = 0;

  const showSlide = (nextIndex) => {
    index = (nextIndex + slides.length) % slides.length;

    slides.forEach((slide, slideIndex) => {
      const isActive = slideIndex === index;

      slide.classList.toggle("about-slider__image--active", isActive);
      slide.toggleAttribute("aria-hidden", !isActive);
    });

    if (status) {
      status.textContent = `Фото ${index + 1} из ${slides.length}`;
    }
  };

  prevButton.addEventListener("click", () => {
    showSlide(index - 1);
  });

  nextButton.addEventListener("click", () => {
    showSlide(index + 1);
  });

  root.addEventListener("keydown", (event) => {
    if (event.key !== "ArrowLeft" && event.key !== "ArrowRight") {
      return;
    }

    event.preventDefault();
    showSlide(index + (event.key === "ArrowRight" ? 1 : -1));
  });
}
