from PIL import Image


def extractGifFrame(image_path):
    
    with Image.open(image_path) as im:
        frame = im.n_frames // 2
        im.seek(frame)
        image_frame = im.convert("RGB")
        
        return image_frame
    
    
    
