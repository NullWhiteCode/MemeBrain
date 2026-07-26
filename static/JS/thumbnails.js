console.log("thumbnails.js loaded");

const placeholders = document.querySelectorAll(".thumbnail-placeholder");

async function checkThumbnail(placeholder) {
  const placeholderURL = placeholder.dataset.url;
  const placeholderName = placeholder.dataset.filename;

  try {
    const response = await fetch(placeholderURL);

    if (!response.ok) {
      console.log("❌", placeholderName, response.status, "Thumbnail missing");

      setTimeout(() => {
        checkThumbnail(placeholder);
      }, 1000);
    } else {
      console.log("✅", placeholderName, response.status, "Thumbnail exists");

      replacePlaceholder(placeholder);
    }
  } catch (error) {
    console.error("🚨", placeholderName, error.message);
  }
}

function replacePlaceholder(placeholder) {
  const newImg = document.createElement("img");

  newImg.src = placeholder.dataset.url;
  newImg.alt = placeholder.dataset.filename;

  placeholder.replaceWith(newImg);
}

for (const placeholder of placeholders) {
  checkThumbnail(placeholder);
}
