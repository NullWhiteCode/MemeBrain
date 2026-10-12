console.log("captions.js loaded");


async function checkCaptionProgress() {
    const url = "/caption_progress";
    const caption = document.querySelector(".captions-panel");
    const progress = caption.querySelector("#progress");
    const info = caption.querySelector("#info");
    const captionText = caption.querySelector("#caption");
    const button = caption.querySelector(".generate-caption-button");
    const spaces = `      `;

    try {
        const response = await fetch(url);

        if (!response.ok) {
            throw new Error(`Response status: ${response.status}`);
        }

        const result = await response.json();
        
        progress.value = result.percentage;
        info.textContent = result.completed + " of " + result.total + " images captioned . " + result.pending + " remaining";
        captionText.textContent = "Caption generation" + spaces + result.percentage.toFixed(2) + "%"
        
        if (result.running) {
            button.textContent = "Generating…";
            button.disabled = true;
        }
        else if (result.pending > 0) {
            button.textContent = "Generate";
            button.disabled = false;
        }
        else {
            button.textContent = "All captions generated";
            button.disabled = true;
        }

    } catch (error) {
        console.error("🚨", error.message);
    }
}


checkCaptionProgress();
setInterval(checkCaptionProgress, 2000)