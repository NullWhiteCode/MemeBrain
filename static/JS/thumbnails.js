console.log("thumbnails.js loaded");

const placeholder = document.querySelectorAll(".thumbnail-placeholder");

async function checkThumbnail(placeholder) {
  const placeholderURL = placeholder.dataset.url;
  const placeholderName = placeholder.dataset.filename;

  try {
    const response = await fetch(placeholderURL);

    if (!response.ok) {
      console.log(
        "❌",
        " ",
        placeholderName,
        " ",
        response.status,
        " ",
        "Thumbnail missing",
      );
    } else {
      console.log(
        "✅",
        " ",
        placeholderName,
        " ",
        response.status,
        " ",
        "Thumbnail exists",
      );
    }
  } catch (error) {
    console.error("🚨", placeholderName, error.message);
  }
}
