from rapidocr import RapidOCR


def createEngine():
    engine = RapidOCR()
    
    return engine


def extractText(engine, image_path):
    result = engine(image_path)
    
    if result.txts is not None:
        extracted_text = " ".join(result.txts)
        
    else:
        extracted_text = ""
    
    return extracted_text
    
