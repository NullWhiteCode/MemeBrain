"""MemeBrain Flask application and HTTP routes."""

from pathlib import Path

from flask import Flask, render_template, request, send_from_directory

from config import (
    load_current_folder,
    load_library_path,
    save_current_folder,
    save_library_path,
)
from folder_picker import select_folder
from library import (
    SUPPORTED_EXTENSIONS,
    build_gallery,
    get_folder_contents,
    get_indexed_folder_items,
    index_library,
    search_library_index,
    split_path_parts,
)
from metadata import get_image_metadata, ImageMetadata
from thumbnails import (
    THUMBNAIL_CACHE_DIR,
    start_thumbnail_worker,
)

app = Flask(__name__)


def _render_library_page(
    folder_path: Path | None,
    library_path: Path | None,
    current_folder: str,
    search_pattern: str = "",
    metadata: ImageMetadata | None = None,
    files: list[str] | None = None,
    directories: list[str] | None = None,
    gallery: list[dict] | None = None,
) -> str:
    """Build a template context and render the index page."""
    if files is None:
        files = []
    if directories is None:
        directories = []
    if gallery is None:
        gallery = []

    if folder_path and folder_path.is_dir():
        if not files and not search_pattern:
            files, directories = get_folder_contents(folder_path)

        if library_path:
            if search_pattern:
                matches = search_library_index(
                    index_library(library_path),
                    search_pattern,
                )
                gallery = build_gallery(library_path, matches)
            else:
                folder_items = get_indexed_folder_items(
                    index_library(library_path),
                    folder_path,
                )
                gallery = build_gallery(library_path, folder_items)

    return render_template(
        "index.html",
        folder_path=folder_path,
        files=files,
        directories=directories,
        search_pattern=search_pattern,
        folder_name=folder_path.name if folder_path else None,
        breadcrumbs=split_path_parts(current_folder) if current_folder else [],
        current_folder=current_folder,
        library_name=Path(library_path).name if library_path else None,
        metadata=metadata,
        gallery=gallery,
    )


def _load_and_render(
    current_folder: str,
    search_pattern: str = "",
    metadata: ImageMetadata | None = None,
) -> str:
    """Load library state and render the page with the given folder context."""
    library_path = load_library_path()
    folder_path = Path(library_path) / current_folder if library_path else None
    return _render_library_page(
        folder_path=folder_path,
        library_path=library_path,
        current_folder=current_folder,
        search_pattern=search_pattern,
        metadata=metadata,
    )


@app.route("/", methods=["GET", "POST"])
def home() -> str:
    """Display the current folder or filename search results."""
    current_folder = load_current_folder() or ""
    search_pattern = ""

    if request.method == "POST":
        search_pattern = request.form.get("search_pattern", "").strip()
        submitted_folder = request.form.get("folder_path")
        if submitted_folder:
            current_folder = ""
            folder_path = Path(submitted_folder)
            if folder_path.is_dir():
                save_library_path(str(folder_path))
                save_current_folder("")

    return _load_and_render(
        current_folder=current_folder,
        search_pattern=search_pattern,
    )


@app.route("/file/<path:filename>")
def serve_image(filename: str) -> str | tuple[str, int]:
    """Serve an image from the selected library."""
    library_path = load_library_path()
    if not library_path:
        return "No library selected.", 400

    library_path = Path(library_path)
    file_path = library_path / filename

    if file_path.is_file() and file_path.suffix.lower() in SUPPORTED_EXTENSIONS:
        return send_from_directory(library_path, filename)

    return "File not found or unsupported file type.", 404


@app.route("/folder_browser")
def folder_browser() -> str:
    """Select a new image library and display its root folder."""
    folder_path = select_folder()
    if not folder_path:
        return _load_and_render(current_folder="")

    save_library_path(str(folder_path))
    save_current_folder("")

    library_path = load_library_path()
    library_index = index_library(library_path)
    start_thumbnail_worker(library_index, library_path)

    return _load_and_render(current_folder="")


@app.route("/path/<path:subpath>")
def navigate_folder(subpath: str) -> str | tuple[str, int]:
    """Display a subfolder within the selected image library."""
    root_folder = load_library_path()
    if not root_folder:
        return "No library selected.", 400

    folder_path = Path(root_folder) / subpath
    if not folder_path.is_dir():
        return "Folder not found.", 404

    save_current_folder(subpath)
    return _load_and_render(current_folder=subpath)


@app.route("/library_root")
def root_navigation_route() -> str | tuple[str, int]:
    """Return to the root of the selected image library."""
    root_folder = load_library_path()
    if not root_folder:
        return "No library selected.", 400

    save_current_folder("")
    return _load_and_render(current_folder="")


@app.route("/image_metadata/<path:filename>")
def image_metadata(filename: str) -> str | tuple[str, int]:
    """Display metadata for an image in the selected library."""
    root_folder = load_library_path()
    if not root_folder:
        return "No library selected.", 400

    root_folder = Path(root_folder)
    image_path = root_folder / filename

    if not image_path.is_file() or image_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        return "File not found or unsupported file type.", 404

    metadata = get_image_metadata(image_path)
    current_folder = load_current_folder() or ""

    return _load_and_render(
        current_folder=current_folder,
        metadata=metadata,
    )


@app.route("/thumbnail/<path:filename>")
def serve_thumbnail(filename: str) -> str | tuple[str, int]:
    """Serve a generated thumbnail from the local cache."""
    thumbnail_path = THUMBNAIL_CACHE_DIR / filename
    if thumbnail_path.is_file():
        return send_from_directory(THUMBNAIL_CACHE_DIR, filename)
    return "Thumbnail not found.", 404


if __name__ == "__main__":
    app.run(debug=True)
