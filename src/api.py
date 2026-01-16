import requests
import time
from typing import Optional, Dict, Any

class ContentFetcher:
    """
    Handles fetching data from the JSONPlaceholder API with robust error handling.
    """
    BASE_URL = "https://dummyjson.com/posts"

    def __init__(self, timeout: int = 5, retries: int = 3):
        self.timeout = timeout
        self.retries = retries

    def get_post(self, post_id: int) -> Optional[Dict[str, Any]]:
        """
        Fetches a single post by ID.
        
        Args:
            post_id: The ID of the post to fetch (1-100).
            
        Returns:
            Dictionary containing post data (id, title, body) or None if failed.
        """
        url = f"{self.BASE_URL}/{post_id}"
        
        for attempt in range(1, self.retries + 1):
            try:
                print(f"[API] Fetching post {post_id} (Attempt {attempt}/{self.retries})...")
                response = requests.get(url, timeout=self.timeout)
                response.raise_for_status()
                return response.json()
                
            except requests.exceptions.RequestException as e:
                print(f"[API] Error fetching post {post_id}: {e}")
                if attempt < self.retries:
                    sleep_time = 1 * attempt  
                    time.sleep(sleep_time)
                else:
                    print(f"[API] Failed to fetch post {post_id} after {self.retries} attempts.")
                    return None
