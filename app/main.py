import datetime
from flask import Flask
from flask_cors import CORS
from pymongo import MongoClient
from .utils.settings import JWT_SECRET_KEY, MONGO_URL, API_PREFIX
from flask_jwt_extended import JWTManager

app = Flask(__name__)
CORS(app)

# app config
client = MongoClient(MONGO_URL)
db = client.weather_db
app.config['JWT_SECRET_KEY'] = JWT_SECRET_KEY
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(days=1)
jwt = JWTManager(app)

# blueprints
from .blueprint import authentication
app.register_blueprint(authentication, url_prefix=API_PREFIX)

if __name__ == '__main__':
    app.run()
