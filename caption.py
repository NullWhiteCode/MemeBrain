from pathlib import Path
import threading
import torch
from transformers import AutoProcessor, Qwen3VLForConditionalGeneration
from database import fileLookup, getPendingCaptions, insertCaptionData
import traceback

from image_processing import extractGifFrame
from model_selection import current_caption_model


_caption_thread = None
_caption_status = "idle"


def loadCaptionModel():
    
    model_path = current_caption_model()
    
    if not model_path:
        raise ValueError("No caption model selected.")
    
    model = Qwen3VLForConditionalGeneration.from_pretrained(
        model_path,
        dtype="auto",
        device_map="auto",
    )

    processor = AutoProcessor.from_pretrained(model_path)
    
    return model, processor


def isCaptionWorkerRunning():
    if _caption_thread:
        return _caption_thread.is_alive()
    return False
        

def generateCaption(image_path, model, processor):
    image_content = {"type": "image"}
    
    if Path(image_path).suffix.lower() == ".gif":
        pil_image = extractGifFrame(image_path)
        image_content["image"] = pil_image
    
    else:
        image_content["url"] = image_path  
   
    messages = [
        {
            "role": "user",
            "content": [
                image_content,
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
    
    with torch.inference_mode():
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
  
    
def processPendingCaptions(batch_size = 5):
    global _caption_status

    try:
        _caption_status = "running"
        pending = getPendingCaptions()
        
        if not pending:
            _caption_status = "completed"
            return
        
        model, processor = loadCaptionModel()
        
    except Exception:
        _caption_status = "failed"
        traceback.print_exc()
        return
        
    try:
        image_failed = False
        for file in pending[:batch_size]:
            try:
                extracted_caption = generateCaption(file[1], model, processor)
                caption_text = prepare_caption_data(file[1], extracted_caption)
                insertCaptionData(caption_text)
        
            except Exception as error:
                _caption_status = "failed"
                print(f"Caption failed for {file[1]}: {error}")
                image_failed = True
                traceback.print_exc()
                
        if image_failed is True:
            _caption_status = "failed"
            
        else:
            _caption_status = "completed"
            
    except Exception:
        traceback.print_exc()
        _caption_status = "failed"
    
    finally:
        try:
            del model
            del processor
            torch.cuda.empty_cache()
                
        except Exception:
            traceback.print_exc()
            _caption_status = "failed"
            
            
def startCaptionWorker():
    global _caption_thread
    
    if _caption_thread is not None and _caption_thread.is_alive():
        return _caption_thread
    
    _caption_thread = threading.Thread(
        target=processPendingCaptions,
        name="caption-worker",
        daemon=True,
    )

    _caption_thread.start()
    return _caption_thread


def captionWorkerStatus():
    return _caption_status