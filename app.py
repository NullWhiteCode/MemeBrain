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
from metadata import get_image_metadata
from thumbnails import (
    THUMBNAIL_CACHE_DIR,
    start_thumbnail_worker,
)


app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def home():
    """Display the current folder or filename search results."""
    folder_path = None
    search_pattern = ""
    folder_name = ""

    files = []
    directories = []
    gallery = []

    library_path = load_library_path()
    library_index = index_library(library_path) if library_path else []

    if library_path:
        start_thumbnail_worker(library_index, library_path)

    library_name = None
    current_folder = load_current_folder() or ""
    breadcrumbs = split_path_parts(current_folder)
    metadata = None

    if library_path:
        library_name = Path(library_path).name
        folder_path = Path(library_path) / current_folder

        if folder_path.is_dir():
            files, directories = get_folder_contents(folder_path)

            current_folder_items = get_indexed_folder_items(
                library_index,
                folder_path,
            )

            gallery = build_gallery(
                library_path,
                current_folder_items,
            )

            folder_name = folder_path.name

    if request.method == "POST":
        submitted_folder = request.form.get("folder_path")

        if submitted_folder:
            folder_path = Path(submitted_folder)

        search_pattern = request.form.get(
            "search_pattern",
            "",
        ).strip()

        if folder_path is not None:
            folder_name = folder_path.name
            files, directories = get_folder_contents(folder_path)

            if search_pattern:
                matches = search_library_index(
                    library_index,
                    search_pattern,
                )

                gallery = build_gallery(
                    library_path,
                    matches,
                )

            else:
                current_folder_items = get_indexed_folder_items(
                    library_index,
                    folder_path,
                )

                gallery = build_gallery(
                    library_path,
                    current_folder_items,
                )

    return render_template(
        "index.html",
        folder_path=folder_path,
        files=files,
        directories=directories,
        search_pattern=search_pattern,
        folder_name=folder_name,
        breadcrumbs=breadcrumbs,
        current_folder=current_folder,
        library_name=library_name,
        metadata=metadata,
        gallery=gallery,
    )


@app.route("/file/<path:filename>")
def serve_image(filename):
    """Serve an image from the selected library."""
    library_path = load_library_path()

    if not library_path:
        return "No library selected.", 400

    library_path = Path(library_path)
    file_path = library_path / filename

    if (
        file_path.is_file()
        and file_path.suffix.lower() in SUPPORTED_EXTENSIONS
    ):
        return send_from_directory(
            library_path,
            filename,
        )

    return "File not found or unsupported file type.", 404


@app.route("/folder_browser")
def folder_browser():
    """Select a new image library and display its root folder."""
    folder_path = select_folder()

    if not folder_path:
        return render_template(
            "index.html",
            folder_path=None,
            files=[],
            directories=[],
            search_pattern="",
            folder_name=None,
            breadcrumbs=[],
            current_folder="",
            library_name=None,
            metadata=None,
            gallery=[],
        )

    save_library_path(folder_path)
    save_current_folder("")

    root_folder = load_library_path()
    library_index = index_library(root_folder)

    start_thumbnail_worker(
        library_index,
        root_folder,
    )

    folder_items = get_indexed_folder_items(
        library_index,
        folder_path,
    )

    files, directories = get_folder_contents(folder_path)

    gallery = build_gallery(
        root_folder,
        folder_items,
    )

    return render_template(
        "index.html",
        folder_path=folder_path,
        files=files,
        directories=directories,
        search_pattern="",
        folder_name=Path(folder_path).name,
        breadcrumbs=[],
        current_folder="",
        library_name=Path(folder_path).name,
        metadata=None,
        gallery=gallery,
    )


@app.route("/path/<path:subpath>")
def navigate_folder(subpath):
    """Display a subfolder within the selected image library."""
    root_folder = load_library_path()

    if not root_folder:
        return "No library selected.", 400

    current_folder = subpath
    folder_path = Path(root_folder) / current_folder

    if not folder_path.is_dir():
        return "Folder not found.", 404

    save_current_folder(current_folder)

    files, directories = get_folder_contents(folder_path)
    library_index = index_library(root_folder)

    folder_items = get_indexed_folder_items(
        library_index,
        folder_path,
    )

    gallery = build_gallery(
        root_folder,
        folder_items,
    )

    return render_template(
        "index.html",
        folder_path=folder_path,
        files=files,
        directories=directories,
        search_pattern="",
        folder_name=folder_path.name,
        breadcrumbs=split_path_parts(current_folder),
        current_folder=current_folder,
        library_name=Path(root_folder).name,
        metadata=None,
        gallery=gallery,
    )


@app.route("/library_root")
def root_navigation_route():
    """Return to the root of the selected image library."""
    root_folder = load_library_path()

    if not root_folder:
        return "No library selected.", 400

    folder_path = Path(root_folder)

    save_current_folder("")

    files, directories = get_folder_contents(folder_path)
    library_index = index_library(root_folder)

    folder_items = get_indexed_folder_items(
        library_index,
        folder_path,
    )

    gallery = build_gallery(
        root_folder,
        folder_items,
    )

    return render_template(
        "index.html",
        folder_path=folder_path,
        files=files,
        directories=directories,
        search_pattern="",
        folder_name=folder_path.name,
        breadcrumbs=[],
        current_folder="",
        library_name=folder_path.name,
        metadata=None,
        gallery=gallery,
    )


@app.route("/image_metadata/<path:filename>")
def image_metadata(filename):
    """Display metadata for an image in the selected library."""
    root_folder = load_library_path()

    if not root_folder:
        return "No library selected.", 400

    root_folder = Path(root_folder)
    image_path = root_folder / filename

    if (
        not image_path.is_file()
        or image_path.suffix.lower() not in SUPPORTED_EXTENSIONS
    ):
        return "File not found or unsupported file type.", 404

    metadata = get_image_metadata(image_path)

    current_folder = load_current_folder() or ""
    folder_path = root_folder / current_folder

    files, directories = get_folder_contents(folder_path)
    library_index = index_library(root_folder)

    folder_items = get_indexed_folder_items(
        library_index,
        folder_path,
    )

    gallery = build_gallery(
        root_folder,
        folder_items,
    )

    return render_template(
        "index.html",
        folder_path=folder_path,
        files=files,
        directories=directories,
        search_pattern="",
        folder_name=folder_path.name,
        breadcrumbs=split_path_parts(current_folder),
        current_folder=current_folder,
        library_name=root_folder.name,
        metadata=metadata,
        gallery=gallery,
    )


@app.route("/thumbnail/<path:filename>")
def serve_thumbnail(filename):
    """Serve a generated thumbnail from the local cache."""
    thumbnail_path = THUMBNAIL_CACHE_DIR / filename

    if thumbnail_path.is_file():
        return send_from_directory(
            THUMBNAIL_CACHE_DIR,
            filename,
        )

    return "Thumbnail not found.", 404


if __name__ == "__main__":
    app.run(debug=True)