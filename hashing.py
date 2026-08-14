import hashlib


def calculate_file_hash(path):
    
    with path.open("rb") as file:
        hash_result = hashlib.file_digest(
            file, 
            hashlib.sha256,
        ).hexdigest()

    return hash_result