from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home():
    folder_path = None
    if request.method == 'POST':
        folder_path = request.form.get('folder_path')
    return render_template('index.html', folder_path=folder_path)

if __name__ == '__main__':
    app.run(debug=True)