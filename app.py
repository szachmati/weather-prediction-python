from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


@app.route('/api/hello-world')
def hello_world():
    return {
        "user": "Mati",
        "title": "Title"
    }


if __name__ == '__main__':
    app.run()
