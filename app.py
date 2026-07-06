from flask import Flask, render_template, request, send_from_directory
from pathlib import Path

app = Flask(__name__)

SUPPORTED_EXTENSIONS = {
".png",
".jpg",
".jpeg",
".gif",
".webp",
".bmp"
}

@app.route('/', methods=['GET', 'POST'])
def home():
    folder_path = None

    files = []
    directories = []

    if request.method == 'POST':
        folder_path = request.form.get('folder_path')
        folder_path = Path(folder_path)
        if folder_path.is_dir():
            for child in folder_path.iterdir():
                if child.is_file():
                    if child.suffix.lower() in SUPPORTED_EXTENSIONS:
                        files.append(child.name)
                elif child.is_dir():
                    directories.append(child.name)

    return render_template('index.html', folder_path=folder_path, files=files, directories=directories)

@app.route('/file/<path:filename>')
def file(filename):
    folder_path = request.args.get('folder_path')
    folder_path = Path(folder_path)
    file_path = folder_path / filename
    if file_path.is_file() and file_path.suffix.lower() in SUPPORTED_EXTENSIONS:
        return send_from_directory(folder_path, filename)
    else:
        return "File not found or unsupported file type.", 404
    

if __name__ == '__main__':
    app.run(debug=True)