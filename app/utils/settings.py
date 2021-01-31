from dotenv import load_dotenv
import os

load_dotenv()
MONGO_URL = os.getenv("MONGO_URL")
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
API_PREFIX = os.getenv("API_PREFIX")
