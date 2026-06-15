"""Application configuration - 校园跑腿Web平台"""

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Database - using MySQL 8.0 as per design spec
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "mysql+aiomysql://root:root@localhost:3306/campus_errand_db"
)

# Security
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
SESSION_EXPIRE_SECONDS = 3600  # 1 hour

# Server
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))

# CORS - comma-separated origins, e.g. "http://locahost:5173,https://yourdomain.com"
CORS_ORIGINS = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:5173,http://localhost:8000"
).split(",")

# App
APP_TITLE = "校园跑腿平台"
APP_VERSION = "1.0.0"
