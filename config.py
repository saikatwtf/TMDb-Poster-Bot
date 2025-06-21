import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Telegram Bot Token
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# TMDb API Key
TMDB_API_KEY = os.getenv("TMDB_API_KEY")

# TMDb API Base URLs
TMDB_API_BASE_URL = "https://api.themoviedb.org/3"
TMDB_IMAGE_BASE_URL = "https://image.tmdb.org/t/p"

# Image sizes
POSTER_SIZES = {
    "small": "w342",
    "medium": "w500",
    "large": "w780",
    "original": "original"
}

BACKDROP_SIZES = {
    "small": "w300",
    "medium": "w780",
    "large": "w1280",
    "original": "original"
}

LOGO_SIZES = {
    "small": "w154",
    "medium": "w300",
    "large": "w500",
    "original": "original"
}

