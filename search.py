from config import load_library_path
from database import getStoredPath, searchOCR
from index import index_folder
from library import search_library_index
from ocr import createEngine


def search(library_index, search_pattern):
    if search_pattern:
        matches = search_library_index(
            library_index,
            search_pattern,
    )
        
        ocr_matches = searchOCR(search_pattern)
        
        for file_id in ocr_matches:
             matching_path = getStoredPath(file_id)
             
             for file in library_index:
                 if str(file["path"]) == matching_path and file not in matches:
                     matches.append(file)
                     
        return matches
                     
            
        
            
    
if __name__ == "__main__":
    engine = createEngine()
    library_path = load_library_path()
    library_index = index_folder(library_path, engine)

    print(search(library_index, "福"))
    print(search(library_index, "福"))
    print(search(library_index, "福"))