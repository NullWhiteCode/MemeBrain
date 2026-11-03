console.log("ocr.js loaded");

let currentOCRState = "idle";
let ocrRequestPending = false;

const button = document.querySelector(".ocr-button");
button.addEventListener("click", handleOCRButtonClick);



async function checkOCRProgress() {
    const url = "/ocr_progress";
    const panel = document.querySelector(".ocr-panel");
    const progress = panel.querySelector("#ocr-progress");
    const info = panel.querySelector("#ocr-info");
    const status = panel.querySelector("#work-status")

    try {
        const response = await fetch(url);

        if (!response.ok) {
            throw new Error(`Response status: ${response.status}`);
        }

        const result = await response.json();
        currentOCRState = result.state;
        const handled = result.processed + result.failed;
        const percentage = result.total > 0
            ? (handled / result.total) * 100
            : 0;

        progress.value = percentage;
        info.textContent = `${handled} of ${result.total} images handled. (${result.failed} failed)`;
        status.textContent = "worker status: " + result.state;

        if (result.state === "running") {
            button.textContent = "Stop";
            button.disabled = false;
        }
        else if (result.state === "stopping") {
            button.textContent = "Stopping…";
            button.disabled = true;
        }
        else if (result.state === "failed") {
            button.textContent = "Retry";
            button.disabled = false;
            status.textContent = `Worker failed: ${result.error}`;
        }
        else {
            button.textContent = "Generate";
            button.disabled = false;
        }

    } catch (error) {
        console.error("🚨", error.message);
    }
}


async function startOCR() {
    
    try {
        const response = await fetch("/ocr_start", { method: "POST" });

        if (!response.ok) {
            throw new Error(`Response status: ${response.status}`);
        }

        await checkOCRProgress();

    } catch (error) {
        console.error("🚨", error.message);
    }
}


async function stopOCR() {

    try {
        const response = await fetch("/ocr_stop", { method: "POST" });

        if (!response.ok) {
            throw new Error(`Response status: ${response.status}`);
        }

        await checkOCRProgress();

    } catch (error) {
        console.error("🚨", error.message);
    }
}


async function handleOCRButtonClick() {

    if (ocrRequestPending) {
            return;
        }

    if (currentOCRState === "stopping") {
        return;
    }

    try {
        ocrRequestPending = true;

        if (currentOCRState === "running") {
            await stopOCR();
        }
        else {
            await startOCR();
        }

    } catch (error) {
        console.error("🚨", error.message);

    } finally {
        ocrRequestPending = false;
    }
}


checkOCRProgress();
setInterval(checkOCRProgress, 2000);