console.log("viewer.js loaded");

const viewer = document.querySelector(".image-viewer");
const backdrop = document.querySelector(".viewer-backdrop");
const images = document.querySelectorAll('a[data-lightbox="gallery"]');
const imgTag = viewer.querySelector("img");
const closeButton = viewer.querySelector(".close-viewer");
const previousButton = viewer.querySelector(".previous-image");
const nextButton = viewer.querySelector(".next-image");
const content = viewer.querySelector(".viewer-content")
const details = viewer.querySelector(".details-area")

let currentIndex = 0;
let metadataRequestId = 0;

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
    if (event.key === "Tab") {
        event.preventDefault();
        toggleDetails();
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
    loadImageDetails();
}

function toggleDetails() {
    const list = content.classList;
    const toggle = list.toggle("details-mode");
    details.hidden = !toggle;   
}

async function loadImageDetails() {
    const currentImg = images[currentIndex];
    const filename = currentImg.dataset.caption;
    const url = "/image_metadata/" + encodeURIComponent(filename);
    const requestId = ++metadataRequestId;
    details.replaceChildren();

    try {
        const response = await fetch(url);

        if (!response.ok) {
            throw new Error(`Response status: ${response.status}`);
        }

        const data = await response.json();

        if (requestId !== metadataRequestId) {
            return
        }

        details.replaceChildren();

        const heading = document.createElement("h3");
        heading.textContent = "IMAGE INFORMATION";
        heading.classList.add("metadata-heading");
        details.append(heading);

        createMetadataRow("Filename", data.metadata.filename);
        createMetadataRow("Dimensions", data.metadata.dimensions);
        createMetadataRow("File size", data.metadata.filesize);
        createMetadataRow("Extension", data.metadata.extension);
        createMetadataRow("Created", data.metadata.created);
        createMetadataRow("Modified", data.metadata.modified);
        createMetadataRow("MIME type", data.metadata.mime_type);
        createMetadataRow("Mode", data.metadata.mode);
        createMetadataRow("Animated", data.metadata.animated ? "Yes" : "No");

        const captionHeading = document.createElement("h3");
        captionHeading.textContent = "CAPTIONS";
        captionHeading.classList.add("metadata-heading");
        details.append(captionHeading);
        const captionElement = document.createElement("p");
        captionElement.classList.add("metadata-description");
        captionElement.textContent = data.caption ?? "No caption generated";
        details.append(captionElement);

        const ocrHeading = document.createElement("h3");
        ocrHeading.textContent = "OCR";
        ocrHeading.classList.add("metadata-heading");
        details.append(ocrHeading);
        const ocrElement = document.createElement("p");
        ocrElement.classList.add("metadata-description");
        ocrElement.textContent = data.ocr_text ?? "No ocr generated";
        details.append(ocrElement);

        const duplicateHeading = document.createElement("h3");
        duplicateHeading.textContent = "DUPLICATES";
        duplicateHeading.classList.add("metadata-heading");
        details.append(duplicateHeading);

        if (data.duplicate_preview.length === 0) {
            const paragraph = document.createElement("p");
            paragraph.textContent = "No duplicates found";
            paragraph.classList.add("duplicates-empty");
            details.appendChild(paragraph);
        } else {
            for (const duplicate of data.duplicate_preview) {
                if (duplicate.thumbnail_exists) {
                    const duplicateImage = document.createElement("img");
                    duplicateImage.classList.add("duplicate-thumbnail");
                    duplicateImage.src = "/thumbnail/" + duplicate.thumbnail;
                    duplicateImage.alt = duplicate.filename;
                    details.appendChild(duplicateImage);

                    duplicateImage.addEventListener("click", () => {
                        const index = Array.from(images).findIndex(image =>
                            image.dataset.caption === duplicate.relative_path
                        );

                        if (index !== -1) {
                            currentIndex = index;
                            displayImage()
                        }
                    });
                }
            }
        }
    } catch (error) {
        console.error("🚨", error.message);
    }
}

function createMetadataRow(label, value) {
    const paragraph = document.createElement("p");
    const newLabel = document.createElement("span");
    const newValue = document.createElement("span");
    newLabel.textContent = label;
    newValue.textContent = value;
    paragraph.append(newLabel, newValue);
    details.appendChild(paragraph);
    paragraph.classList.add("metadata-row");
    newLabel.classList.add("metadata-label");
    newValue.classList.add("metadata-value");
}