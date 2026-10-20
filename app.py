"""MemeBrain Flask application and HTTP routes."""

from pathlib import Path
from caption import captionWorkerStatus, isCaptionWorkerRunning, startCaptionWorker
from model_selection import current_caption_model, update_caption_model
from search import search
from flask import Flask, jsonify, render_template, request, send_from_directory, redirect, url_for

from index import index_folder
from database import getCaptionProgress, setupDatabase
from ocr import startOCRWorker

from config import (
    clear_saved_caption_model,
    load_caption_model,
    load_config,
    load_current_folder,
    load_library_path,
    save_caption_model,
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
    split_path_parts,
    build_duplicate_preview,
    get_indexed_subtree_items,
)
from metadata import get_image_metadata
from thumbnails import (
    THUMBNAIL_CACHE_DIR,
    start_thumbnail_worker,
)


app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def home():
    """Display the current folder or search results."""
    folder_path = None
    search_pattern = ""
    folder_name = ""

    files = []
    directories = []
    gallery = []

    library_path = load_library_path()
    library_index = index_folder(library_path) if library_path else []

    if library_path:
        start_thumbnail_worker(library_index, library_path)
        startOCRWorker()

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
                matches = search(
                    get_indexed_subtree_items(library_index, folder_path),
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
    library_index = index_folder(root_folder)

    start_thumbnail_worker(
        library_index,
        root_folder,
    )
    
    startOCRWorker()

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
    duplicate_preview = build_duplicate_preview(metadata["duplicates"], root_folder)

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
        duplicate_preview=duplicate_preview,
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


@app.route("/generate_captions", methods=["POST"])
def generate_captions():
    """Starts caption generation on user input"""
    library_path = load_library_path()
    
    if library_path:
        startCaptionWorker()
        
    return redirect(url_for('home'))


@app.route("/caption_progress", methods=["GET"])
def caption_progress():
    result = getCaptionProgress()
    completed = result[1]
    total = result[0]
    
    pending = total - completed
    percentage = (completed / total) * 100 if total else 0
    
    running = isCaptionWorkerRunning()
    status = captionWorkerStatus()
    
    caption_values = {
        'total': total, 
        'completed': completed,
        'pending': pending,
        'percentage': percentage,
        'running': running,
        'status': status
    }
    
    return jsonify(caption_values)


@app.route("/select_caption_model", methods=["POST"])
def select_caption_model():
    caption_folder_path = select_folder("Select a caption model")
    update_caption_model(caption_folder_path)
    active_model = current_caption_model()
    
    return jsonify({"model_path": str(active_model)})


@app.route("/get_model_status", methods=["GET"])
def get_model_status():
    active_model_path = str(current_caption_model())
    remembered_status = False
    config = load_config()
    active_selection = bool(active_model_path)
    
    if active_model_path == config.get("caption_model") and active_selection:
        remembered_status = True
        
    return jsonify({"active_model_path": active_model_path, 
                   "remembered_status": remembered_status, 
                   "active_selection": active_selection}
                )
    

@app.route("/update_model_checkbox", methods=["POST"])
def update_model_checkbox():
    is_checked = request.json.get('remembered_status')
    is_active = bool(current_caption_model())
    
    if isinstance(is_checked, bool):
        
        if is_checked and is_active:
            save_caption_model()
            return jsonify("Caption model saved.")
    
        if is_checked and not is_active:
            return jsonify("No model selected to save."), 400
        
        else:
            clear_saved_caption_model()
            return jsonify("Caption model cleared.")
        
    else:
        return jsonify("Error."), 400



load_caption_model()
setupDatabase()


if __name__ == "__main__":
    app.run(debug=True)