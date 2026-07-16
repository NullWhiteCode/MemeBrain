from flask import Flask, render_template, request, send_from_directory
from pathlib import Path
import json, mimetypes, hashlib
import tkinter as tk
from tkinter import filedialog
from datetime import datetime
from PIL import Image

"""
MemeBrain

A Flask application for browsing and searching local image collections.
"""

app = Flask(__name__)

# Only display image formats currently supported by MemeBrain.
SUPPORTED_EXTENSIONS = {
".png",
".jpg",
".jpeg",
".gif",
".webp",
".bmp"
}

CONFIG_FILE = Path("config.json")


def get_folder_contents(folder_path):
    """Return supported image files and immediate directories."""
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


def search_file_names(folder_path, search_pattern):
    """Return image paths whose filenames contain the search text."""
    files, _ = get_folder_contents(folder_path)
    matching_files = []

    for file in files:
        if search_pattern.lower() in file.lower():
            matching_files.append(file)

    return matching_files


def save_library_path(folder_path):
    if CONFIG_FILE.exists():
        json_data = CONFIG_FILE.read_text(encoding="utf-8")
        parsed_data = json.loads(json_data)
        parsed_data["library_path"] = str(folder_path)
        json_data = json.dumps(parsed_data, indent=2)

        CONFIG_FILE.write_text(json_data, encoding="utf-8")


def load_library_path():
    """Load the saved library path from the JSON config file."""
    if CONFIG_FILE.exists():
        json_data = CONFIG_FILE.read_text(encoding="utf-8")
        parsed_data = json.loads(json_data)
        return parsed_data.get("library_path")
    
    return None


def save_current_folder(folder_path):
    if CONFIG_FILE.exists():
        json_data = CONFIG_FILE.read_text(encoding="utf-8")
        parsed_data = json.loads(json_data)
        parsed_data["current_folder"] = str(folder_path)
        json_data = json.dumps(parsed_data, indent=2)

        CONFIG_FILE.write_text(json_data, encoding="utf-8")

    
def load_current_folder():
    if CONFIG_FILE.exists():
        json_data = CONFIG_FILE.read_text(encoding="utf-8")
        parsed_data = json.loads(json_data)
        return parsed_data.get("current_folder")
    
    return None


def split_path_parts(current_folder):
    path_parts = Path(current_folder).parts
    cumulative_path = []
    breadcrumbs = []

    for part in path_parts:
        cumulative_path.append(part)
        breadcrumbs.append(
            {
                "display": part,
                "link": Path(*cumulative_path).as_posix(),
            }
        )

    return breadcrumbs


def get_image_metadata(image_path):
    image_path = Path(image_path)

    if not image_path.is_file():
        return None

    file_stats = image_path.stat()

    with Image.open(image_path) as image_stats:
        metadata = {
            "filename": image_path.name,
            "extension": image_path.suffix.lower(),
            "filesize": format_filesize(file_stats.st_size),
            "modified": format_timestamp(file_stats.st_mtime),
            "created": format_timestamp(file_stats.st_birthtime),
            "mime_type": mimetypes.guess_type(str(image_path))[0] or "Unknown",
            "dimensions": f"{image_stats.width} × {image_stats.height}",
            "mode": image_stats.mode,
            "animated": getattr(image_stats, "is_animated", False),
        }

    return metadata


def build_image_thumbnail(image_path, library_path):
    image_path = Path(image_path)
    size = (384, 384)

    if not image_path.is_file():

        return None
    
    relative_path = image_path.relative_to(library_path)
    cache_filename = hashlib.md5(str(relative_path).encode("utf-8")).hexdigest()
    cache_dir = Path("cache") / "thumbnails"
    cache_path = cache_dir / f"{cache_filename}.webp"
    
    cache_dir.mkdir(parents=True, exist_ok=True)

    if cache_path.exists():

        return cache_path
    
    with Image.open(image_path) as im:
        im.thumbnail(size)
        im.save(cache_path, "WEBP")

        return cache_path
    

def build_gallery(folder_path, library_path, files=None):
    gallery = []

    if files is None:
        files, _ = get_folder_contents(folder_path)

    for filename in files:
        image_path = Path(folder_path) / filename
        thumbnail_path = build_image_thumbnail(image_path, library_path)

        if thumbnail_path is None:
            continue

        gallery.append({
            "filename": filename,
            "thumbnail": thumbnail_path.name,
        })

    return gallery


def format_filesize(filesize):
    for unit in ['B', 'KB', 'MB']:
        if filesize < 1024.0:
            return f"{filesize:.2f} {unit}"
        filesize /= 1024.0
    return f"{filesize:.2f} GB"


def format_timestamp(timestamp):
    dt = datetime.fromtimestamp(timestamp)
    return dt.strftime("%Y-%m-%d %H:%M:%S")


@app.route('/', methods=['GET', 'POST'])
def home():
    folder_path = None
    search_pattern = ""
    folder_name = ""

    files = []
    directories = []
    gallery = []

    library_path = load_library_path()
    library_name = None
    current_folder = load_current_folder() or ""
    breadcrumbs = split_path_parts(current_folder)
    metadata = None
    
    if library_path:
        library_name = Path(library_path).name
        folder_path = Path(library_path) / current_folder

        if folder_path.is_dir():
            files, directories = get_folder_contents(folder_path)
            gallery = build_gallery(folder_path, library_path)
            folder_name = folder_path.name

    if request.method == 'POST':
        # Preserve the current folder and search text after the form is submitted.
        folder_path = request.form.get('folder_path')
        search_pattern = request.form.get("search_pattern", "").strip()
        
        folder_path = Path(folder_path)
        folder_name = folder_path.name
        files, directories = get_folder_contents(folder_path)

        if search_pattern:
            files = search_file_names(folder_path, search_pattern)
            
        gallery = build_gallery(folder_path, library_path, files)


    return render_template('index.html', folder_path=folder_path, files=files, directories=directories, search_pattern=search_pattern, folder_name=folder_name, breadcrumbs=breadcrumbs, current_folder=current_folder, library_name=library_name, metadata=metadata, gallery=gallery)


@app.route('/file/<path:filename>')
def serve_image(filename):
    """Serve an image from the currently selected folder."""
    folder_path = request.args.get('folder_path')
    folder_path = Path(folder_path)
    file_path = folder_path / filename
    
    if file_path.is_file() and file_path.suffix.lower() in SUPPORTED_EXTENSIONS:
        # Only serve existing files with supported image extensions.    
        return send_from_directory(folder_path, filename)
    else:
        return "File not found or unsupported file type.", 404
    

@app.route('/folder_browser')
def folder_browser():
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)

    folder_path = filedialog.askdirectory(
        title="Select a folder to browse",
        parent=root
    )

    root.destroy()

    if folder_path == "":
        gallery=[]
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
            gallery=gallery
        )
    
    folder_name = Path(folder_path).name

    save_library_path(folder_path)
    save_current_folder("")
    breadcrumbs = []
    metadata = None

    root_folder = load_library_path()
    files, directories = get_folder_contents(folder_path)
    gallery = build_gallery(folder_path, root_folder)
    return render_template(
        'index.html',
        folder_path=folder_path,
        files=files,
        directories=directories,
        search_pattern="",
        folder_name=folder_name,
        breadcrumbs=breadcrumbs,
        current_folder="",
        library_name=Path(folder_path).name,
        metadata=metadata,
        gallery=gallery
    )


@app.route("/path/<path:subpath>")
def navigate_folder(subpath):
    root_folder = load_library_path()
    if not root_folder:
        return "No library selected.", 400
    
    new_current_folder = subpath
    folder_path = Path(root_folder) / new_current_folder

    if not folder_path.is_dir():
        return "Folder not found.", 404
    
    save_current_folder(new_current_folder)
    breadcrumbs = split_path_parts(new_current_folder)

    library_name = Path(root_folder).name
    folder_name = folder_path.name
    files, directories = get_folder_contents(folder_path)
    gallery = build_gallery(folder_path, root_folder)
    metadata = None
    return render_template(
        'index.html',
        folder_path=folder_path,
        files=files,
        directories=directories,
        search_pattern="",
        folder_name=folder_name,
        breadcrumbs=breadcrumbs,
        current_folder=new_current_folder,
        library_name=library_name,
        metadata=metadata,
        gallery=gallery
    )

@app.route('/library_root')
def root_navigation_route():
    root_folder = load_library_path()
    folder_path = Path(root_folder)
    if not root_folder:
        return "No library selected.", 400
    
    save_current_folder("")
    files, directories = get_folder_contents(root_folder)
    gallery = build_gallery(folder_path, root_folder)
    metadata = None
    
    return render_template(
        'index.html',
        folder_path=root_folder,
        files=files,
        directories=directories,
        search_pattern="",
        folder_name=Path(root_folder).name,
        breadcrumbs=[],
        current_folder="",
        library_name=Path(root_folder).name,
        metadata=metadata,
        gallery=gallery
    )


@app.route('/image_metadata/<path:filename>')
def image_metadata(filename):
    library_root = load_library_path()
    current_folder = load_current_folder() or ""
    folder_path = Path(library_root) / current_folder
    image_path = folder_path / filename

    if image_path.is_file() and image_path.suffix.lower() in SUPPORTED_EXTENSIONS:
        metadata = get_image_metadata(image_path)
        files, directories = get_folder_contents(folder_path)
        gallery = build_gallery(folder_path, library_root)

        return render_template('index.html', folder_path=folder_path, files=files, directories=directories, search_pattern="", folder_name=folder_path.name, breadcrumbs=split_path_parts(current_folder), current_folder=current_folder, library_name=Path(library_root).name, metadata=metadata, gallery=gallery)
    
    return "File not found or unsupported file type.", 404
    

@app.route("/thumbnail/<path:filename>")
def serve_thumbnail(filename):
    cache_dir = Path("cache") / "thumbnails"
    thumbnail_path = cache_dir / filename

    if thumbnail_path.is_file():

        return send_from_directory(cache_dir, filename)

    return "Thumbnail not found.", 404
    

    
if __name__ == '__main__':
    app.run(debug=True)