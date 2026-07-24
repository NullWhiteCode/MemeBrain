"""Index, search, and describe the contents of an image library."""

from pathlib import Path

from thumbnails import get_thumbnail_cache_path


SUPPORTED_EXTENSIONS = {
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".webp",
    ".bmp",
}


def get_folder_contents(folder_path):
    """Return supported image filenames and immediate subdirectory names."""
    folder_path = Path(folder_path)
    files = []
    directories = []

    if folder_path.is_dir():
        for child in sorted(folder_path.iterdir()):
            if child.is_file() and child.suffix.lower() in SUPPORTED_EXTENSIONS:
                files.append(child.name)
            elif child.is_dir():
                directories.append(child.name)

    return files, directories


def index_library(library_path):
    """Return index entries for every supported image beneath a library."""
    library_path = Path(library_path)
    indexed_files = []

    for path in library_path.rglob("*"):
        if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS:
            indexed_files.append(
                {
                    "filename": path.name,
                    "path": path,
                    "relative_path": path.relative_to(library_path),
                    "folder": path.parent.relative_to(library_path),
                }
            )

    return indexed_files


def get_indexed_folder_items(library_index, folder_path):
    """Return indexed images located directly inside the selected folder."""
    folder_path = Path(folder_path)

    return [
        item
        for item in library_index
        if item["path"].parent == folder_path
    ]


def search_library_index(library_index, search_pattern):
    """Return index entries whose filenames contain the search text."""
    search_pattern = search_pattern.lower()

    return [
        item
        for item in library_index
        if search_pattern in item["filename"].lower()
    ]


def split_path_parts(current_folder):
    """Build breadcrumb labels and cumulative links for a relative path."""
    cumulative_path = []
    breadcrumbs = []

    for part in Path(current_folder).parts:
        cumulative_path.append(part)
        breadcrumbs.append(
            {
                "display": part,
                "link": Path(*cumulative_path).as_posix(),
            }
        )

    return breadcrumbs


def build_gallery(library_path, indexed_files):
    """Build template-ready gallery entries without generating thumbnails."""
    gallery = []

    for item in indexed_files:
        thumbnail_path = get_thumbnail_cache_path(
            item["path"],
            library_path,
        )

        gallery.append(
            {
                "filename": item["filename"],
                "relative_path": item["relative_path"].as_posix(),
                "thumbnail": thumbnail_path.name,
                "thumbnail_exists": thumbnail_path.exists()
            }
        )

    return gallery