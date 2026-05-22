"""
Data Fetcher Module - Fetches football data from multiple sources
"""

import aiohttp
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import requests
from bs4 import BeautifulSoup

from config import settings
from utils.logger import get_logger

logger = get_logger(__name__)


class FootballDataFetcher:
    """Fetches data from football-data.org API"""
    
    def __init__(self, api_key: str = settings.FOOTBALL_DATA_API_KEY):
        self.api_key = api_key
        self.base_url = "https://api.football-data.org/v4"
        self.headers = {"X-Auth-Token": api_key}
        self.session = None
    
    async def get_matches(
        self,
        league_id: str,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> List[Dict]:
        """Fetch matches from football-data.org"""
        logger.info(f"Fetching matches from football-data.org for league: {league_id}")
        
        params = {}
        if date_from:
            params["dateFrom"] = date_from.strftime("%Y-%m-%d")
        if date_to:
            params["dateTo"] = date_to.strftime("%Y-%m-%d")
        
        try:
            url = f"{self.base_url}/competitions/{league_id}/matches"
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            matches = data.get("matches", [])
            logger.info(f"Retrieved {len(matches)} matches from football-data.org")
            
            return matches
        except Exception as e:
            logger.error(f"Error fetching from football-data.org: {str(e)}")
            return []
    
    async def get_team_stats(self, team_id: str) -> Dict:
        """Fetch team statistics"""
        logger.info(f"Fetching team stats for team_id: {team_id}")
        
        try:
            url = f"{self.base_url}/teams/{team_id}"
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Retrieved team stats for {data.get('name')}")
            
            return data
        except Exception as e:
            logger.error(f"Error fetching team stats: {str(e)}")
            return {}


class ESPNFetcher:
    """Fetches data from ESPN API"""
    
    def __init__(self):
        self.base_url = "https://site.api.espn.com/apis/site/v2/sports/soccer"
    
    async def get_matches(self, league: str = "eng.1") -> List[Dict]:
        """Fetch matches from ESPN"""
        logger.info(f"Fetching matches from ESPN for league: {league}")
        
        try:
            url = f"{self.base_url}/{league}/scoreboard"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            matches = data.get("events", [])
            logger.info(f"Retrieved {len(matches)} matches from ESPN")
            
            return matches
        except Exception as e:
            logger.error(f"Error fetching from ESPN: {str(e)}")
            return []


class RapidAPIFetcher:
    """Fetches data from RapidAPI football APIs"""
    
    def __init__(self, api_key: str = settings.RAPIDAPI_KEY):
        self.api_key = api_key
        self.base_url = "https://api-football-v1.p.rapidapi.com/v3"
        self.headers = {
            "x-rapidapi-key": api_key,
            "x-rapidapi-host": "api-football-v1.p.rapidapi.com"
        }
    
    async def get_fixtures(
        self,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> List[Dict]:
        """Fetch fixtures/matches"""
        logger.info("Fetching fixtures from RapidAPI")
        
        params = {}
        if date_from:
            params["from"] = date_from.strftime("%Y-%m-%d")
        if date_to:
            params["to"] = date_to.strftime("%Y-%m-%d")
        
        try:
            url = f"{self.base_url}/fixtures"
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            fixtures = data.get("response", [])
            logger.info(f"Retrieved {len(fixtures)} fixtures from RapidAPI")
            
            return fixtures
        except Exception as e:
            logger.error(f"Error fetching from RapidAPI: {str(e)}")
            return []


class WebScraper:
    """Scrapes football data from websites"""
    
    async def scrape_odds(self, match_url: str) -> Dict:
        """Scrape betting odds from websites"""
        logger.info(f"Scraping odds from: {match_url}")
        
        try:
            response = requests.get(match_url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            # Parse odds from HTML (specific to website structure)
            # This is a placeholder - actual implementation depends on target website
            
            logger.info(f"Successfully scraped odds from {match_url}")
            return {}
        except Exception as e:
            logger.error(f"Error scraping odds: {str(e)}")
            return {}


class DataFetcherManager:
    """Manages all data fetchers"""
    
    def __init__(self):
        self.fetchers = {
            "football_data": FootballDataFetcher(),
            "espn": ESPNFetcher(),
            "rapidapi": RapidAPIFetcher(),
            "web_scraper": WebScraper(),
        }
    
    async def fetch_all_sources(
        self,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> Dict:
        """Fetch data from all enabled sources"""
        logger.info("Starting data collection from all sources")
        
        results = {}
        tasks = []
        
        for source in settings.data_sources_list:
            if source in self.fetchers:
                fetcher = self.fetchers[source]
                if hasattr(fetcher, 'get_matches'):
                    tasks.append(
                        self._fetch_with_source(source, fetcher, date_from, date_to)
                    )
        
        # Execute all tasks concurrently
        results_list = await asyncio.gather(*tasks, return_exceptions=True)
        
        for source, result in zip(settings.data_sources_list, results_list):
            if isinstance(result, Exception):
                logger.error(f"Error fetching from {source}: {result}")
                results[source] = []
            else:
                results[source] = result
        
        logger.info(f"Data collection completed. Total sources: {len(results)}")
        return results
    
    async def _fetch_with_source(
        self,
        source: str,
        fetcher,
        date_from: Optional[datetime],
        date_to: Optional[datetime],
    ) -> List[Dict]:
        """Fetch from a specific source"""
        try:
            if hasattr(fetcher, 'get_matches'):
                return await fetcher.get_matches(date_from=date_from, date_to=date_to)
            elif hasattr(fetcher, 'get_fixtures'):
                return await fetcher.get_fixtures(date_from=date_from, date_to=date_to)
        except Exception as e:
            logger.error(f"Error in {source}: {str(e)}")
            raise


if __name__ == "__main__":
    # Example usage
    import asyncio
    
    async def main():
        manager = DataFetcherManager()
        data = await manager.fetch_all_sources(
            date_from=datetime.now() - timedelta(days=7),
            date_to=datetime.now()
        )
        print(f"Fetched data: {data}")
    
    asyncio.run(main())
