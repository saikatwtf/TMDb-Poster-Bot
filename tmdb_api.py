import requests
import logging
from config import TMDB_API_KEY, TMDB_API_BASE_URL, TMDB_IMAGE_BASE_URL, POSTER_SIZES, BACKDROP_SIZES

# Set up logger
logger = logging.getLogger(__name__)

class TMDbAPI:
    def __init__(self):
        self.api_key = TMDB_API_KEY
        self.base_url = TMDB_API_BASE_URL
        self.image_base_url = TMDB_IMAGE_BASE_URL
    
    def search_multi(self, query, language="en-US", page=1):
        """Search for movies, TV shows, and people in a single request"""
        endpoint = f"{self.base_url}/search/multi"
        params = {
            "api_key": self.api_key,
            "query": query,
            "language": language,
            "page": page,
            "include_adult": False
        }
        
        try:
            response = requests.get(endpoint, params=params, timeout=10)
            return response.json() if response.status_code == 200 else None
        except requests.exceptions.RequestException as e:
            logger.error(f"Error searching TMDb: {e}")
            return None
    
    def get_details(self, media_type, media_id, language="en-US"):
        """Get detailed information about a specific movie or TV show"""
        if media_type not in ["movie", "tv"]:
            return None
            
        endpoint = f"{self.base_url}/{media_type}/{media_id}"
        params = {
            "api_key": self.api_key,
            "language": language,
            "append_to_response": "images"
        }
        
        try:
            response = requests.get(endpoint, params=params, timeout=10)
            return response.json() if response.status_code == 200 else None
        except requests.exceptions.RequestException as e:
            logger.error(f"Error getting details from TMDb: {e}")
            return None
    
    def get_poster_url(self, poster_path, size="medium"):
        """Generate poster URL from poster path"""
        if not poster_path:
            return None
            
        size_key = POSTER_SIZES.get(size, "medium")
        return f"{self.image_base_url}/{size_key}{poster_path}"
    
    def get_backdrop_url(self, backdrop_path, size="medium"):
        """Generate backdrop URL from backdrop path"""
        if not backdrop_path:
            return None
            
        size_key = BACKDROP_SIZES.get(size, "medium")
        return f"{self.image_base_url}/{size_key}{backdrop_path}"