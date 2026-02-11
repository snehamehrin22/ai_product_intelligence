"""
Database connection and operations
"""

from supabase import create_client, Client
from config.settings import get_settings
from typing import Optional, List, Dict, Any

settings = get_settings()


class Database:
    def __init__(self):
        self.client: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
    
    def _map_prospect_to_app(self, db_prospect: Dict[str, Any]) -> Dict[str, Any]:
        """Map dim_prospects columns to app format"""
        return {
            'id': db_prospect['id'],
            'brand_name': db_prospect.get('company_name', ''),
            'industry_category': db_prospect.get('industry', ''),
            'est_revenue_range': db_prospect.get('revenue', ''),
            'hq_location': db_prospect.get('location', ''),
            'website': db_prospect.get('website', ''),
            'linkedin_url': db_prospect.get('linkedin_url', ''),
            'why_good_fit': db_prospect.get('notes', ''),
            'created_at': db_prospect.get('created_at', '')
        }

    def _map_app_to_prospect(self, app_data: Dict[str, Any]) -> Dict[str, Any]:
        """Map app format to dim_prospects columns"""
        return {
            'company_name': app_data.get('brand_name', ''),
            'industry': app_data.get('industry_category', ''),
            'revenue': app_data.get('est_revenue_range', ''),
            'location': app_data.get('hq_location', ''),
            'website': app_data.get('website', ''),
            'linkedin_url': app_data.get('linkedin_url', ''),
            'notes': app_data.get('why_good_fit', '')
        }

    async def get_prospect_by_name(self, brand_name: str) -> Optional[Dict[str, Any]]:
        """Get prospect by brand name"""
        response = self.client.table('dim_prospects').select('*').eq('company_name', brand_name).execute()
        if response.data:
            return self._map_prospect_to_app(response.data[0])
        return None

    async def create_prospect(self, prospect_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new prospect"""
        db_data = self._map_app_to_prospect(prospect_data)
        response = self.client.table('dim_prospects').insert(db_data).execute()
        return self._map_prospect_to_app(response.data[0])

    async def get_all_prospects(self) -> List[Dict[str, Any]]:
        """Get all prospects"""
        response = self.client.table('dim_prospects').select('*').execute()
        return [self._map_prospect_to_app(p) for p in response.data]

    async def update_prospect(self, prospect_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update prospect"""
        db_data = self._map_app_to_prospect(data)
        response = self.client.table('dim_prospects').update(db_data).eq('id', prospect_id).execute()
        return self._map_prospect_to_app(response.data[0])
    
    async def insert_reddit_urls(self, urls: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Insert Reddit URLs"""
        response = self.client.schema('case_studies_factory').table('brand_google_reddit').insert(urls).execute()
        return response.data

    async def get_reddit_urls(self, prospect_id: str) -> List[Dict[str, Any]]:
        """Get Reddit URLs for prospect"""
        response = self.client.schema('case_studies_factory').table('brand_google_reddit').select('*').eq('prospect_id', prospect_id).execute()
        return response.data

    async def insert_posts_comments(self, data: List[Dict[str, Any]]) -> None:
        """Bulk insert posts and comments"""
        if not data:
            return

        # Batch insert in chunks of 1000
        chunk_size = 1000
        for i in range(0, len(data), chunk_size):
            chunk = data[i:i + chunk_size]
            self.client.schema('case_studies_factory').table('brand_reddit_posts_comments').insert(chunk).execute()

    async def insert_analysis_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Insert analysis result"""
        response = self.client.schema('case_studies_factory').table('reddit_brand_analysis_results').insert(result).execute()
        return response.data[0]

    async def mark_urls_processed(self, prospect_id: str, urls: List[str]) -> None:
        """Mark URLs as processed after scraping"""
        for url in urls:
            self.client.schema('case_studies_factory').table('brand_google_reddit').update({'processed': True}).eq('prospect_id', prospect_id).eq('url', url).execute()

