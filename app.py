from flask import Flask, render_template, request
from pathlib import Path

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home():
    folder_path = None
    if request.method == 'POST':
        folder_path = request.form.get('folder_path')
        folder_path = Path(folder_path)
        if folder_path.is_dir():
            for child in folder_path.iterdir():
                if child.is_file():
                    print(f"File: {child.name}")
                elif child.is_dir():
                    print(f"Directory: {child.name}")
    return render_template('index.html', folder_path=folder_path)

if __name__ == '__main__':
    app.run(debug=True)