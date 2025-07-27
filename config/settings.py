from decouple import config
from pathlib import Path 

BASE_DIR = Path(__file__).resolve().parent.parent 

class Config:
    SECRET_KEY = config('SECRET_KEY', default="super-secret-key")
    SQLALCHEMY_DATABASE_URI = config('DATABASE_URL', default=f"sqlite:///{BASE_DIR / 'app.db'}")
    DEBUG = config('DEBUG', default=False, cast=bool) 
