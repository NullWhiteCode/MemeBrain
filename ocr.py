from importlib.metadata import version
from pathlib import Path
import threading
import time

import numpy as np
from rapidocr import RapidOCR

from config import automatic_ocr_enabled
from database import fileLookup, getPendingOCR, insertOCRData
from image_processing import extractGifFrame

_ocr_thread = None
_ocr_stop_event = threading.Event()
_ocr_auto_suppressed = False
_ocr_lock = threading.RLock()

_ocr_status = {
    "state": "idle",
    "total": 0,
    "processed": 0,
    "error": None,
    "failed": 0,
    "failed_files": []
}


def createEngine():
    engine = RapidOCR()
    
    return engine



def extractText(engine, image_path):
    if Path(image_path).suffix.lower() == ".gif":
        pil_image = extractGifFrame(image_path)
        ocr_input = np.array(pil_image)
    else:
        ocr_input = image_path
        
    result = engine(ocr_input)
    
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
    updateOCRStatus(
        state="running",
        total=0,
        processed=0,
        error=None,
        failed=0,
        failed_files=[]
    )
    try:
        pending = getPendingOCR()
        if not pending:
            updateOCRStatus(
                state="completed",
                total=len(pending),
                processed=0,
                error=None,
                failed=0,
                failed_files=[]
            )
            return
        
        updateOCRStatus(
            state="running",
            total=len(pending),
            processed=0,
            error=None,
            failed=0,
            failed_files=[]
        )
    
        engine = createEngine()
        
        for file in pending:
            if _ocr_stop_event.is_set():
                break

            try:
                extracted_text = extractText(engine, file[1])

            except Exception as error:
                with _ocr_lock:
                    _ocr_status["failed"] += 1
                    _ocr_status["failed_files"].append({
                        "path": file[1],
                        "error": str(error)
                    })
                continue

            ocr_data = prepare_ocr_data(file[1], extracted_text)
            insertOCRData(ocr_data)
            with _ocr_lock:
                _ocr_status["processed"] += 1
        
        with _ocr_lock:
            if _ocr_status["processed"] + _ocr_status["failed"] == _ocr_status["total"]:
                _ocr_status["state"] = "completed"
        
            elif _ocr_stop_event.is_set():
                _ocr_status["state"] = "stopped"
            
    except Exception as error:
        updateOCRStatus(
            state="failed",
            error=str(error)
        )
        
        
def startOCRWorker():
    global _ocr_thread

    with _ocr_lock:
        if _ocr_thread is not None and _ocr_thread.is_alive():
            if _ocr_stop_event.is_set():
                return None

            return _ocr_thread

        _ocr_stop_event.clear()

        _ocr_thread = threading.Thread(
            target=processPendingOCR,
            name="ocr-worker",
            daemon=True,
        )

        _ocr_thread.start()
        return _ocr_thread


def startAutomaticOCR():
    with _ocr_lock:
        if automatic_ocr_enabled() and not _ocr_auto_suppressed:
            return startOCRWorker()
      
        
def stopOCRWorker():
    global _ocr_auto_suppressed

    with _ocr_lock:
        if _ocr_thread and _ocr_thread.is_alive():
            if _ocr_status["state"] in ("running", "stopping"):
                _ocr_stop_event.set()
                updateOCRStatus(state="stopping")

        _ocr_auto_suppressed = True
    
    
def startManualOCR():
    global _ocr_auto_suppressed
    with _ocr_lock:
        worker = startOCRWorker()
        
        if worker is not None:
            _ocr_auto_suppressed = False
            
        return worker
    
    
def getOCRStatus():
    with _ocr_lock:
        status_copy = _ocr_status.copy()
        status_copy["failed_files"] = _ocr_status["failed_files"].copy()
        return status_copy
    
    
def updateOCRStatus(**changes):
    with _ocr_lock:
        _ocr_status.update(changes)