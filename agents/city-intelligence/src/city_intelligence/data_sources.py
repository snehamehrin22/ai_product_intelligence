"""
Data source integrations for City Intelligence Agent.

Provides functions to fetch data from various sources with caching to minimize API costs.

Supported sources:
- Statistics Canada (census data)
- Google Maps/Places (business listings, foot traffic proxies)
- Reddit (community discussions)
- Municipal open data portals
- Transit data
- Real estate data

All functions cache results to data/cache/ directory.
"""

import os
import json
import hashlib
import requests
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any
import time


class DataSourceCache:
    """Simple file-based cache for API responses."""

    def __init__(self, cache_dir: Optional[Path] = None):
        """Initialize cache directory."""
        if cache_dir is None:
            cache_dir = Path(__file__).parent.parent.parent / "data" / "cache"
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _get_cache_key(self, source: str, query: str) -> str:
        """Generate cache key from source and query."""
        combined = f"{source}:{query}"
        return hashlib.md5(combined.encode()).hexdigest()

    def get(self, source: str, query: str, max_age_hours: int = 168) -> Optional[Dict]:
        """Get cached data if exists and not expired (default 1 week)."""
        cache_key = self._get_cache_key(source, query)
        cache_file = self.cache_dir / f"{cache_key}.json"

        if not cache_file.exists():
            return None

        # Check age
        file_time = datetime.fromtimestamp(cache_file.stat().st_mtime)
        age = datetime.now() - file_time
        if age > timedelta(hours=max_age_hours):
            return None

        # Load cached data
        with open(cache_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def set(self, source: str, query: str, data: Dict):
        """Cache data to file."""
        cache_key = self._get_cache_key(source, query)
        cache_file = self.cache_dir / f"{cache_key}.json"

        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)


# Global cache instance
cache = DataSourceCache()


# ============================================================================
# Census Data (Statistics Canada)
# ============================================================================

def get_census_data(
    census_subdivision: str,
    variables: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Fetch census data from Statistics Canada.

    Args:
        census_subdivision: Census subdivision code (e.g., '3520005' for Toronto)
        variables: List of census variables to fetch (None = default set)

    Returns:
        Dictionary with census data

    Note: This is a simplified wrapper. Production implementation would use
    Statistics Canada's official API or data tables.
    """
    cache_key = f"census_{census_subdivision}_{','.join(variables or [])}"
    cached = cache.get("stats_canada", cache_key, max_age_hours=8760)  # 1 year
    if cached:
        return cached

    # Default variables if none specified
    if variables is None:
        variables = [
            "population",
            "median_age",
            "median_household_income",
            "unemployment_rate",
            "bachelor_degree_or_higher",
            "renter_percentage"
        ]

    # In production, this would call Statistics Canada API
    # For now, return structure for manual data entry
    result = {
        "source": "Statistics Canada",
        "census_subdivision": census_subdivision,
        "last_census_year": 2021,
        "data": {var: None for var in variables},
        "note": "Manual data entry required - visit https://www12.statcan.gc.ca/census-recensement/"
    }

    cache.set("stats_canada", cache_key, result)
    return result


# ============================================================================
# Google Maps / Places API
# ============================================================================

def search_businesses_google(
    neighborhood: str,
    city: str,
    business_type: str,
    api_key: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Search for businesses using Google Places API.

    Args:
        neighborhood: Neighborhood name
        city: City name
        business_type: Business type (e.g., 'cafe', 'restaurant', 'gym')
        api_key: Google Places API key (or from GOOGLE_PLACES_API_KEY env var)

    Returns:
        List of business dictionaries
    """
    if api_key is None:
        api_key = os.getenv("GOOGLE_PLACES_API_KEY")

    cache_key = f"{neighborhood}_{city}_{business_type}"
    cached = cache.get("google_places", cache_key, max_age_hours=168)  # 1 week
    if cached:
        return cached

    if not api_key:
        return {
            "error": "GOOGLE_PLACES_API_KEY not found",
            "note": "Set GOOGLE_PLACES_API_KEY in .env file"
        }

    # Google Places Text Search API
    url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    query = f"{business_type} in {neighborhood}, {city}"

    params = {
        "query": query,
        "key": api_key
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        results = []
        for place in data.get("results", []):
            results.append({
                "name": place.get("name"),
                "address": place.get("formatted_address"),
                "rating": place.get("rating"),
                "user_ratings_total": place.get("user_ratings_total"),
                "price_level": place.get("price_level"),
                "types": place.get("types", [])
            })

        cache.set("google_places", cache_key, results)
        return results

    except requests.RequestException as e:
        return {"error": str(e)}


def count_businesses_by_type(
    neighborhood: str,
    city: str,
    business_types: List[str]
) -> Dict[str, int]:
    """
    Count businesses by type in a neighborhood.

    Args:
        neighborhood: Neighborhood name
        city: City name
        business_types: List of business types to count

    Returns:
        Dictionary mapping business type to count
    """
    counts = {}
    for business_type in business_types:
        results = search_businesses_google(neighborhood, city, business_type)
        if isinstance(results, list):
            counts[business_type] = len(results)
        else:
            counts[business_type] = 0

    return counts


# ============================================================================
# Reddit API
# ============================================================================

def search_reddit(
    subreddit: str,
    query: str,
    limit: int = 100,
    time_filter: str = "year"
) -> List[Dict[str, Any]]:
    """
    Search Reddit for discussions about a neighborhood.

    Args:
        subreddit: Subreddit to search (e.g., 'toronto')
        query: Search query
        limit: Number of results to return
        time_filter: Time filter ('hour', 'day', 'week', 'month', 'year', 'all')

    Returns:
        List of Reddit posts/comments
    """
    cache_key = f"{subreddit}_{query}_{limit}_{time_filter}"
    cached = cache.get("reddit", cache_key, max_age_hours=24)  # 1 day
    if cached:
        return cached

    # Using Reddit's JSON API (no auth required, but rate limited)
    url = f"https://www.reddit.com/r/{subreddit}/search.json"

    params = {
        "q": query,
        "limit": limit,
        "sort": "relevance",
        "t": time_filter,
        "restrict_sr": "on"
    }

    headers = {
        "User-Agent": "CityIntelligenceBot/1.0"
    }

    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()

        posts = []
        for post in data.get("data", {}).get("children", []):
            post_data = post.get("data", {})
            posts.append({
                "title": post_data.get("title"),
                "selftext": post_data.get("selftext"),
                "score": post_data.get("score"),
                "num_comments": post_data.get("num_comments"),
                "created_utc": post_data.get("created_utc"),
                "url": post_data.get("url"),
                "author": post_data.get("author")
            })

        cache.set("reddit", cache_key, posts)
        time.sleep(2)  # Rate limiting
        return posts

    except requests.RequestException as e:
        return {"error": str(e)}


def analyze_reddit_sentiment(
    neighborhood: str,
    city: str,
    subreddit: Optional[str] = None
) -> Dict[str, Any]:
    """
    Analyze Reddit sentiment about a neighborhood.

    Args:
        neighborhood: Neighborhood name
        city: City name
        subreddit: Subreddit to search (default: city name in lowercase)

    Returns:
        Dictionary with sentiment analysis and key themes
    """
    if subreddit is None:
        subreddit = city.lower().replace(" ", "")

    posts = search_reddit(subreddit, neighborhood, limit=100)

    if isinstance(posts, dict) and "error" in posts:
        return posts

    # Simple analysis: count mentions of common themes
    themes = {
        "safety": 0,
        "expensive": 0,
        "affordable": 0,
        "gentrification": 0,
        "transit": 0,
        "restaurants": 0,
        "nightlife": 0,
        "family-friendly": 0,
        "walkable": 0
    }

    for post in posts:
        text = (post.get("title", "") + " " + post.get("selftext", "")).lower()
        for theme in themes:
            if theme in text or theme.replace("-", " ") in text:
                themes[theme] += 1

    return {
        "total_posts": len(posts),
        "total_score": sum(p.get("score", 0) for p in posts),
        "themes": themes,
        "recent_discussions": posts[:5]  # Top 5 most relevant
    }


# ============================================================================
# Municipal Open Data
# ============================================================================

def get_toronto_open_data(
    dataset_id: str
) -> Dict[str, Any]:
    """
    Fetch data from Toronto Open Data Portal.

    Args:
        dataset_id: Dataset identifier from Toronto Open Data Portal

    Returns:
        Dataset dictionary

    Example dataset IDs:
    - Business licenses: various
    - Demographics: various
    - Transit: various

    See: https://open.toronto.ca/
    """
    cache_key = f"toronto_{dataset_id}"
    cached = cache.get("toronto_open_data", cache_key, max_age_hours=168)
    if cached:
        return cached

    # Toronto Open Data uses CKAN API
    url = f"https://ckan0.cf.opendata.inter.prod-toronto.ca/api/3/action/package_show?id={dataset_id}"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        cache.set("toronto_open_data", cache_key, data)
        return data

    except requests.RequestException as e:
        return {"error": str(e)}


# ============================================================================
# Transit Data
# ============================================================================

def get_transit_data(
    city: str,
    neighborhood: str
) -> Dict[str, Any]:
    """
    Get transit information for a neighborhood.

    Args:
        city: City name
        neighborhood: Neighborhood name

    Returns:
        Transit data dictionary

    Note: This is a placeholder. Production implementation would integrate
    with transit agency APIs (TTC, TransLink, etc.)
    """
    cache_key = f"{city}_{neighborhood}"
    cached = cache.get("transit", cache_key, max_age_hours=168)
    if cached:
        return cached

    # Placeholder structure for manual data entry
    result = {
        "city": city,
        "neighborhood": neighborhood,
        "subway_stations": [],
        "bus_routes": [],
        "streetcar_routes": [],
        "bike_lanes": None,
        "walkability_score": None,
        "note": "Manual data entry required or use transit agency API"
    }

    cache.set("transit", cache_key, result)
    return result


# ============================================================================
# Helper Functions
# ============================================================================

def get_neighborhood_context(
    neighborhood: str,
    city: str
) -> Dict[str, Any]:
    """
    Get comprehensive context about a neighborhood.

    This is a convenience function that aggregates data from multiple sources.

    Args:
        neighborhood: Neighborhood name
        city: City name

    Returns:
        Dictionary with aggregated neighborhood data
    """
    return {
        "neighborhood": neighborhood,
        "city": city,
        "census_data": get_census_data("manual_entry_required"),
        "business_counts": count_businesses_by_type(
            neighborhood,
            city,
            ["cafe", "restaurant", "gym", "bar", "park", "coworking"]
        ),
        "reddit_sentiment": analyze_reddit_sentiment(neighborhood, city),
        "transit_data": get_transit_data(city, neighborhood),
        "timestamp": datetime.now().isoformat()
    }


def clear_cache(source: Optional[str] = None):
    """
    Clear cached data.

    Args:
        source: Specific source to clear (None = clear all)
    """
    if source:
        # Clear specific source cache files
        pattern = f"*{source}*"
        for cache_file in cache.cache_dir.glob(pattern):
            cache_file.unlink()
    else:
        # Clear all cache
        for cache_file in cache.cache_dir.glob("*.json"):
            cache_file.unlink()


# ============================================================================
# Real Estate Data (Placeholder)
# ============================================================================

def get_real_estate_data(
    neighborhood: str,
    city: str
) -> Dict[str, Any]:
    """
    Get real estate data for a neighborhood.

    Args:
        neighborhood: Neighborhood name
        city: City name

    Returns:
        Real estate data dictionary

    Note: This is a placeholder. Production implementation would integrate
    with real estate APIs (Rentals.ca, Condos.ca, Zillow, etc.)
    """
    cache_key = f"{city}_{neighborhood}"
    cached = cache.get("real_estate", cache_key, max_age_hours=168)
    if cached:
        return cached

    result = {
        "neighborhood": neighborhood,
        "city": city,
        "median_rent_1br": None,
        "median_rent_2br": None,
        "median_sale_price_condo": None,
        "median_sale_price_house": None,
        "rental_vacancy_rate": None,
        "year_over_year_change": None,
        "note": "Manual data entry required or use real estate API"
    }

    cache.set("real_estate", cache_key, result)
    return result


# ============================================================================
# Data Validation
# ============================================================================

def validate_data_sources() -> Dict[str, bool]:
    """
    Validate that required API keys and data sources are configured.

    Returns:
        Dictionary mapping source to availability status
    """
    return {
        "google_places_api": bool(os.getenv("GOOGLE_PLACES_API_KEY")),
        "reddit_api": True,  # No auth required for basic search
        "census_data": True,  # Manual entry or public data
        "toronto_open_data": True,  # Public API
        "transit_data": True,  # Manual entry or public data
        "real_estate_data": True  # Manual entry or paid API
    }
