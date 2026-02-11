"""
Configuration management - loads from Bitwarden
"""

import sys
import os
from functools import lru_cache

# Add credentials path
sys.path.append(os.path.expanduser('~/.config/ai_credentials'))
from get_credential import get_credential


class Settings:
    def __init__(self):
        # Get credentials from Bitwarden
        supabase_url = get_credential("supabase", "url")
        # Extract project ID from dashboard URL and construct API URL
        if "dashboard/project/" in supabase_url:
            project_id = supabase_url.split("dashboard/project/")[-1].strip("/")
            self.SUPABASE_URL = f"https://{project_id}.supabase.co"
        else:
            self.SUPABASE_URL = supabase_url

        self.SUPABASE_KEY = get_credential("supabase", "api_key")
        self.APIFY_API_KEY = get_credential("apify", "api_key")
        self.OPENAI_API_KEY = get_credential("Open AI", "api_key")

        # Optional settings
        self.MAX_REDDIT_URLS = 10
        self.MAX_POSTS_PER_URL = 20
        self.MAX_COMMENTS_PER_POST = 20


@lru_cache()
def get_settings() -> Settings:
    return Settings()
