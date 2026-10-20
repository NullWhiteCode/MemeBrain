console.log("models.js loaded");

const captionButton = document.querySelector("#caption-button");
captionButton.addEventListener("click", selectCaptionButton);

const captionCheckbox = document.querySelector("#remember-model");
captionCheckbox.addEventListener("change", updateModelCheckbox)


async function displayActiveModel() {
    const url = "/get_model_status";
    const model = document.querySelector(".models-panel");
    const model_name = model.querySelector("#model-name");

    try {
        const response = await fetch(url);

        if (!response.ok) {
            throw new Error(`Response status: ${response.status}`);
        }

        const result = await response.json();

        if (result.active_model_path == "") {
            model_name.textContent = "No model selected";
        } else {
            model_name.textContent = result.active_model_path.split("\\").pop();
        }

    } catch (error) {
        console.error("🚨", error.message);
    }
}


async function modelCheckbox() {
    const url = "/get_model_status";
    const checkbox = document.querySelector("#remember-model");

    try {
        const response = await fetch(url);

        if (!response.ok) {
            throw new Error(`Response status: ${response.status}`);
        }

        const result = await response.json();
        const remembered = result.remembered_status;
        checkbox.checked = remembered;

    } catch (error) {
        console.error("🚨", error.message);
    }
}


async function updateModelCheckbox() {
    const url = "/update_model_checkbox";
    const captionCheckbox = document.querySelector("#remember-model");
    const is_checked = captionCheckbox.checked;
    const remembered = {remembered_status: is_checked};

    try {
        const response = await fetch(url, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(remembered),
        });

        if (!response.ok) {
            throw new Error(`Response status: ${response.status}`);
        }

    } catch (error) {
        console.error("🚨", error.message);

    } finally {
        await modelCheckbox()
    }
}


async function selectCaptionButton() {
    const url = "/select_caption_model";

    try {
        const response = await fetch(url, {
            method: "POST"
        });

        if (!response.ok) {
            throw new Error(`Response status: ${response.status}`);
        }

        await displayActiveModel()
        await modelCheckbox()

    } catch (error) {
        console.error("🚨", error.message);
    }
}



displayActiveModel()
modelCheckbox()