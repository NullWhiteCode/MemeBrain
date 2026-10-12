from database import getStoredPath, searchOCR, searchCaptions
from library import search_library_index



def search(library_index, search_pattern):
    if search_pattern:
        matches = search_library_index(
            library_index,
            search_pattern,
    )
        
        ocr_matches = searchOCR(search_pattern)
        caption_matches = searchCaptions(search_pattern)
        all_matches = set(ocr_matches) | set(caption_matches)
        
        for file_id in all_matches:
             matching_path = getStoredPath(file_id)
             
             for file in library_index:
                 if str(file["path"]) == matching_path and file not in matches:
                     matches.append(file)
                     
        return matches
                     
            