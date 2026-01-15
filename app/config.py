from dotenv import load_dotenv
import os

load_dotenv()

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = "async_auth_db"

JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440
