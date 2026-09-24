export function initReviewsScroll() {
  const track = document.querySelector(".reviews__track");

  if (!track) {
    return;
  }

  let isDragging = false;
  let startX = 0;
  let scrollLeft = 0;

  const onPointerDown = (event) => {
    if (event.pointerType === "touch") {
      return;
    }

    isDragging = true;
    startX = event.clientX;
    scrollLeft = track.scrollLeft;
    track.setPointerCapture(event.pointerId);
  };

  const onPointerMove = (event) => {
    if (!isDragging) {
      return;
    }

    const delta = event.clientX - startX;
    track.scrollLeft = scrollLeft - delta;
  };

  const onPointerUp = () => {
    isDragging = false;
  };

  track.addEventListener("pointerdown", onPointerDown);
  track.addEventListener("pointermove", onPointerMove);
  track.addEventListener("pointerup", onPointerUp);
  track.addEventListener("pointercancel", onPointerUp);
}
