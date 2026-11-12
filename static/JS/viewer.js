console.log("viewer.js loaded");

const viewer = document.querySelector(".image-viewer");
const backdrop = document.querySelector(".viewer-backdrop");
const images = document.querySelectorAll('a[data-lightbox="gallery"]');
const imgTag = viewer.querySelector("img");
const closeButton = viewer.querySelector(".close-viewer");
const previousButton = viewer.querySelector(".previous-image");
const nextButton = viewer.querySelector(".next-image");

let currentIndex = 0;

document.addEventListener("keydown", handleKeydown);
closeButton.addEventListener("click", closeViewer);
images.forEach((image, index) => {
    image.addEventListener("click", (event) => {
        currentIndex = index;
        openViewer(event);
    });
});
previousButton.addEventListener("click", () => navigateImage(-1));
nextButton.addEventListener("click", () => navigateImage(1));


function openViewer(event) {
    event.preventDefault();
    backdrop.hidden = false;
    viewer.hidden = false;
    displayImage();
}

function closeViewer() {
    viewer.hidden = true;
    backdrop.hidden = true;
}

function handleKeydown(event) {
    if (viewer.hidden) return;

    if (event.key === "Escape") {
        closeViewer();
    }
    if (event.key === "ArrowLeft") {
        navigateImage(-1);
    }
    if (event.key === "ArrowRight") {
        navigateImage(1);
    }
}

function updateNavigation() {
    previousButton.hidden = (currentIndex === 0);
    nextButton.hidden = (currentIndex === images.length - 1);
}

function navigateImage(direction) {
    const newIndex = currentIndex + direction;

    if (newIndex >= 0 && newIndex < images.length) {
        currentIndex = newIndex;
        displayImage();
    }
}

function displayImage() {
    imgTag.src = images[currentIndex].href;
    updateNavigation();
}