from builtins import str
import sqlite3, time

from library import index_library
from database import getStoredFiles, markFileMissing, markFileIndexed, fileLookup, insertFile, updateFile
from hashing import calculate_file_hash


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


def file_changed(path, row):
    stats = path.stat()
    modified_time = stats.st_mtime
    file_size = stats.st_size

    if modified_time != row[2] or file_size != row[3]:
        return True
    return False


def store_library_index(library_index):
    
    for item in library_index:
        path = item["path"]
        row = fileLookup(path)

        if row is None:
            file_data = prepare_file_data(path)
            insertFile(file_data)

        else:
            if file_changed(path, row):
                file_data = prepare_file_data(path)
                updateFile(file_data)

            if row[5] == "missing":
                markFileIndexed(path)


def getDuplicateGroups():
    stored_files = getStoredFiles()
    dict_groups = {}
    duplicate_groups = {}

    for file in stored_files:
        file_hash = file[6]
        file_path = file[1]

        if file_hash not in dict_groups:
            dict_groups[file_hash] = []

        dict_groups[file_hash].append(file_path)

        if len(dict_groups[file_hash]) > 1:
            duplicate_groups[file_hash] = dict_groups[file_hash]

    return duplicate_groups

    
def index_folder(library_path):
    library_index = index_library(library_path)
    store_library_index(library_index)









