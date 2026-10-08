from transformers import AutoProcessor, Qwen3VLForConditionalGeneration
from database import fileLookup

MODEL_PATH = r"C:\Tools\Models\Qwen3-VL-4B-Instruct"


def loadCaptionModel():
    model = Qwen3VLForConditionalGeneration.from_pretrained(
        MODEL_PATH,
        dtype="auto",
        device_map="auto",
    )

    processor = AutoProcessor.from_pretrained(MODEL_PATH)
    
    return model, processor


def generateCaption(image_path, model, processor):
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "url": image_path
                },
                {
                    "type": "text",
                    "text": "Describe this image for visual search indexing in 1-2 concise sentences. Identify the main subjects, their actions, distinctive visual details, setting, and art style where relevant. Describe only what is visibly present. Do not speculate about meaning, emotions, or backstory. Do not transcribe text visible in the image. Avoid introductions and unnecessary adjectives."
                }
            ]
        }
    ]

    inputs = processor.apply_chat_template(
        messages,
        tokenize=True,
        add_generation_prompt=True,
        return_dict=True,
        return_tensors="pt",
    )

    inputs.pop("token_type_ids", None)
    inputs = inputs.to("cuda")
    generated_ids = model.generate(**inputs, max_new_tokens=128)

    generated_ids_trimmed = [
                out_ids[len(in_ids) :] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
    ]

    output_text = processor.batch_decode(
        generated_ids_trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False
    )
    
    caption_text = output_text[0]
    
    return caption_text


def prepare_caption_data(image_path, caption_text):
    file = fileLookup(image_path)
    
    if file is None:
        return None
    
    file_id = file[0]
    
    return {
        "file_id": file_id,
        "caption": caption_text,
        "model_name": "Qwen3-VL-4B-Instruct",
    }


