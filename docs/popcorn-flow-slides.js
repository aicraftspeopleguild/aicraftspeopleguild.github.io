const deck = document.getElementById("deck");
const slides = [...document.querySelectorAll(".slide")];
const progress = document.getElementById("deck-progress");
const currentSlide = document.getElementById("current-slide");
const totalSlides = document.getElementById("total-slides");
const fullscreenToggle = document.getElementById("fullscreen-toggle");

let activeIndex = 0;

totalSlides.textContent = String(slides.length);

slides.forEach((slide, index) => {
  slide.id = `slide-${index + 1}`;

  const dot = document.createElement("button");
  dot.type = "button";
  dot.className = "progress-dot";
  dot.setAttribute("aria-label", `Go to slide ${index + 1}: ${slide.dataset.title || "Untitled"}`);
  dot.addEventListener("click", () => goToSlide(index));
  progress.append(dot);
});

const dots = [...progress.querySelectorAll(".progress-dot")];

const setActive = (index) => {
  activeIndex = index;
  currentSlide.textContent = String(index + 1);

  slides.forEach((slide, slideIndex) => {
    slide.classList.toggle("is-active", slideIndex === index);
  });

  dots.forEach((dot, dotIndex) => {
    dot.classList.toggle("is-active", dotIndex === index);
  });

  const targetHash = `#${slides[index].id}`;
  if (window.location.hash !== targetHash) {
    history.replaceState(null, "", targetHash);
  }
};

const goToSlide = (index) => {
  const safeIndex = Math.max(0, Math.min(index, slides.length - 1));

  slides[safeIndex].scrollIntoView({
    behavior: "smooth",
    block: "start"
  });

  setActive(safeIndex);
};

const observer = new IntersectionObserver(
  (entries) => {
    const visible = entries
      .filter((entry) => entry.isIntersecting)
      .sort((a, b) => b.intersectionRatio - a.intersectionRatio)[0];

    if (!visible) {
      return;
    }

    const index = slides.indexOf(visible.target);
    if (index >= 0) {
      setActive(index);
    }
  },
  {
    root: deck,
    threshold: [0.45, 0.65, 0.85]
  }
);

slides.forEach((slide) => observer.observe(slide));

const slideParam = Number(new URLSearchParams(window.location.search).get("slide"));
const paramIndex = Number.isInteger(slideParam) && slideParam >= 1 && slideParam <= slides.length
  ? slideParam - 1
  : -1;
const hashIndex = slides.findIndex((slide) => `#${slide.id}` === window.location.hash);
const initialIndex = paramIndex >= 0 ? paramIndex : hashIndex;

setActive(initialIndex >= 0 ? initialIndex : 0);

if (initialIndex >= 0) {
  requestAnimationFrame(() => {
    slides[initialIndex].scrollIntoView({
      behavior: "auto",
      block: "start"
    });
  });
}

document.addEventListener("keydown", (event) => {
  const tagName = document.activeElement?.tagName;
  const typing = tagName === "INPUT" || tagName === "TEXTAREA";

  if (typing) {
    return;
  }

  if (["ArrowDown", "ArrowRight", "PageDown", " "].includes(event.key)) {
    event.preventDefault();
    goToSlide(activeIndex + 1);
  }

  if (["ArrowUp", "ArrowLeft", "PageUp"].includes(event.key)) {
    event.preventDefault();
    goToSlide(activeIndex - 1);
  }

  if (event.key === "Home") {
    event.preventDefault();
    goToSlide(0);
  }

  if (event.key === "End") {
    event.preventDefault();
    goToSlide(slides.length - 1);
  }

  if (event.key.toLowerCase() === "f") {
    event.preventDefault();
    toggleFullscreen();
  }
});

const toggleFullscreen = async () => {
  if (!document.fullscreenElement) {
    await document.documentElement.requestFullscreen();
    return;
  }

  await document.exitFullscreen();
};

fullscreenToggle.addEventListener("click", () => {
  toggleFullscreen().catch(() => {
    // Ignore browsers that block the request.
  });
});

document.addEventListener("fullscreenchange", () => {
  fullscreenToggle.textContent = document.fullscreenElement ? "Exit Full Screen" : "Full Screen";
});
