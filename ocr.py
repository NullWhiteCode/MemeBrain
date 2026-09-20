from importlib.metadata import version
import threading
import time

from rapidocr import RapidOCR

from database import fileLookup, getPendingOCR, insertOCRData

_ocr_thread = None


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


def prepare_ocr_data(image_path, extracted_text):
    file = fileLookup(image_path)
    file_id = file[0]
    ocr_time = time.time()
    rapidocr_version = version("rapidocr")
    
    return {
        "file_id": file_id,
        "text": extracted_text,
        "ocr_time": ocr_time,
        "engine": "RapidOCR",
        "engine_version": rapidocr_version,
    }
    
    
def processPendingOCR():
    pending = getPendingOCR()
    if not pending:
        return
    
    engine = createEngine()
    
    for file in pending:
        extracted_text = extractText(engine, file[1])
        ocr_data = prepare_ocr_data(file[1], extracted_text)
        insertOCRData(ocr_data)
        
        
def startOCRWorker():
    global _ocr_thread
    
    if _ocr_thread is not None and _ocr_thread.is_alive():
        return _ocr_thread

    _ocr_thread = threading.Thread(
        target=processPendingOCR,
        name="ocr-worker",
        daemon=True,
    )

    _ocr_thread.start()
    return _ocr_thread



