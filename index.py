import time

from library import index_library
from database import getStoredFiles, insertOCRData, markFileMissing, markFileIndexed, fileLookup, insertFile, ocrRowLookup, updateFile
from hashing import calculate_file_hash
from importlib.metadata import version

from ocr import extractText




def pathCompare(library_index):
    stored_files = getStoredFiles()
    stored_paths = []
    current_paths = []

    for row in stored_files:
        stored_paths.append(row[1])

    for item in library_index:
        current_paths.append(str(item["path"]))

    for path in stored_paths:
        if path not in current_paths:
            markFileMissing(path)


def prepare_file_data(path):
    stats = path.stat()
    modified_time = stats.st_mtime
    file_size = stats.st_size
    indexed_time = time.time()
    status = "indexed"
    file_hash = calculate_file_hash(path)

    return {
        "file_path": str(path),
        "modified_time": modified_time,
        "file_size": file_size,
        "indexed_time": indexed_time,
        "status": status,
        "file_hash": file_hash,
    }
    
    
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


def file_changed(path, row):
    stats = path.stat()
    modified_time = stats.st_mtime
    file_size = stats.st_size

    if modified_time != row[2] or file_size != row[3]:
        return True
    return False


def store_library_index(library_index, engine):
    
    for item in library_index:
        path = item["path"]
        row = fileLookup(path)
        
        if row is None:
            file_data = prepare_file_data(path)
            insertFile(file_data)
            extracted_text = extractText(engine, path)
            ocr_data = prepare_ocr_data(path, extracted_text)
            insertOCRData(ocr_data)

        else:
            if file_changed(path, row):
                file_data = prepare_file_data(path)
                updateFile(file_data)
                extracted_text = extractText(engine, path)
                ocr_data = prepare_ocr_data(path, extracted_text)
                insertOCRData(ocr_data)
                
            else:
                if ocrRowLookup(path) is None:
                    extracted_text = extractText(engine, path)
                    ocr_data = prepare_ocr_data(path, extracted_text)
                    insertOCRData(ocr_data)

            if row[5] == "missing":
                markFileIndexed(path)


def getDuplicateGroups():
    stored_files = getStoredFiles()
    dict_groups = {}
    duplicate_groups = {}

    for file in stored_files:
        file_hash = file[6]
        file_path = file[1]
        file_status = file[5]
        
        if file_status != "indexed":
            continue

        if file_hash not in dict_groups:
            dict_groups[file_hash] = []
            
        dict_groups[file_hash].append(file_path)

        if len(dict_groups[file_hash]) > 1:
            duplicate_groups[file_hash] = dict_groups[file_hash]

    return duplicate_groups


def getImageDuplicates(image_path):
    image_path = str(image_path)
    duplicate_groups = getDuplicateGroups()
    image_db_row = fileLookup(image_path)
    image_hash = image_db_row[6]
    duplicate_images = []
    
    for hash in duplicate_groups:
        if hash == image_hash:
            for path in duplicate_groups[hash]:
                if path != image_path:
                    duplicate_images.append(path)
            
    return duplicate_images
    
 
def index_folder(library_path, engine):
    library_index = index_library(library_path)
    
    pathCompare(library_index)
    
    store_library_index(library_index, engine)
    
    return library_index









