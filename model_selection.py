from pathlib import Path

caption_model_path = ""


def current_caption_model():
    return caption_model_path


def update_caption_model(model_path):
    global caption_model_path
    
    if model_path:
        model_path = Path(model_path)
        
        if model_path.is_dir():
            caption_model_path = model_path
        
        else:
            print("Invalid directory") 
            
    else:
        print("No directory selected")
