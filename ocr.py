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
    

if __name__ == "__main__":
    image_path = r"F:\User Files\Pictures\Spicy Memes\gjvBTUd.jpg"
    engine = createEngine()
    
    extracted_text = extractText(engine, image_path)
    print(extracted_text)