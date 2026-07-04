from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello_world():
    return """
    <h1>MemeBrain</h1>

    <p>Hello teammate 😎</p>
    """

if __name__ == '__main__':
    app.run(debug=True)