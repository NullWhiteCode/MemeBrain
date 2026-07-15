from flask import Flask, render_template, request, send_from_directory
from pathlib import Path
import json
import tkinter as tk
from tkinter import filedialog

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



@app.route('/', methods=['GET', 'POST'])
def home():
    folder_path = None
    search_pattern = ""
    folder_name = ""

    files = []
    directories = []

    library_path = load_library_path()
    library_name = None
    current_folder = load_current_folder() or ""
    breadcrumbs = split_path_parts(current_folder)

    if library_path:
        library_name = Path(library_path).name
        folder_path = Path(library_path) / current_folder

        if folder_path.is_dir():
            files, directories = get_folder_contents(folder_path)
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


    return render_template('index.html', folder_path=folder_path, files=files, directories=directories, search_pattern=search_pattern, folder_name=folder_name, breadcrumbs=breadcrumbs, current_folder=current_folder, library_name=library_name)


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
        return render_template(
            "index.html",
            folder_path=None,
            files=[],
            directories=[],
            search_pattern="",
            folder_name=None,
            breadcrumbs=[],
            current_folder="",
            library_name=None
        )
    
    folder_name = Path(folder_path).name

    save_library_path(folder_path)
    save_current_folder("")
    breadcrumbs = []

    files, directories = get_folder_contents(folder_path)
    return render_template(
        'index.html',
        folder_path=folder_path,
        files=files,
        directories=directories,
        search_pattern="",
        folder_name=folder_name,
        breadcrumbs=breadcrumbs,
        current_folder="",
        library_name=Path(folder_path).name
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
    return render_template(
        'index.html',
        folder_path=folder_path,
        files=files,
        directories=directories,
        search_pattern="",
        folder_name=folder_name,
        breadcrumbs=breadcrumbs,
        current_folder=new_current_folder,
        library_name=library_name
    )

@app.route('/library_root')
def root_navigation_route():
    root_folder = load_library_path()
    if not root_folder:
        return "No library selected.", 400
    
    save_current_folder("")
    files, directories = get_folder_contents(root_folder)
    
    return render_template(
        'index.html',
        folder_path=root_folder,
        files=files,
        directories=directories,
        search_pattern="",
        folder_name=Path(root_folder).name,
        breadcrumbs=[],
        current_folder="",
        library_name=Path(root_folder).name
    )

    



if __name__ == '__main__':
    app.run(debug=True)