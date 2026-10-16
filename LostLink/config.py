import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "default-dev-key")
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
    DATABASE_NAME = os.getenv("DATABASE_NAME", "lostlink")
    UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), os.getenv("UPLOAD_FOLDER", "uploads"))
    MATCH_THRESHOLD = int(os.getenv("MATCH_THRESHOLD", 50))
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max upload
