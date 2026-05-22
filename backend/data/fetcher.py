"""
Data fetcher module for retrieving football match data from various sources
"""

import asyncio
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import aiohttp
import requests
from bs4 import BeautifulSoup

from config import settings
from utils.logger import get_logger

logger = get_logger(__name__)


class DataSource(ABC):
    """Abstract base class for data sources"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.session = None
    
    @abstractmethod
    async def fetch_matches(
        self,
        league: str,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None
    ) -> List[Dict]:
        """Fetch matches from the data source"""
        pass
    
    @abstractmethod
    async def fetch_team_stats(self, team_name: str) -> Dict:
        """Fetch team statistics"""
        pass


class FootballDataSource(DataSource):
    """Data source for Football-Data.org API"""
    
    BASE_URL = "https://api.football-data.org/v4"
    
    LEAGUE_CODES = {
        "EPL": "PL",
        "LA_LIGA": "SA",
        "SERIE_A": "SA",
        "BUNDESLIGA": "BL1",
        "LIGUE_1": "FL1",
    }
    
    async def fetch_matches(
        self,
        league: str,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None
    ) -> List[Dict]:
        """Fetch matches from Football-Data.org"""
        try:
            league_code = self.LEAGUE_CODES.get(league)
            if not league_code:
                logger.warning(f"League {league} not supported")
                return []
            
            url = f"{self.BASE_URL}/competitions/{league_code}/matches"
            headers = {"X-Auth-Token": self.api_key}
            
            params = {}
            if date_from:
                params["dateFrom"] = date_from.strftime("%Y-%m-%d")
            if date_to:
                params["dateTo"] = date_to.strftime("%Y-%m-%d")
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, params=params) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        matches = self._parse_matches(data.get("matches", []))
                        logger.info(f"Fetched {len(matches)} matches from Football-Data.org")
                        return matches
                    else:
                        logger.error(f"Football-Data API error: {resp.status}")
                        return []
        
        except Exception as e:
            logger.error(f"Error fetching from Football-Data.org: {str(e)}")
            return []
    
    async def fetch_team_stats(self, team_name: str) -> Dict:
        """Fetch team statistics"""
        # Placeholder implementation
        return {
            "team_name": team_name,
            "matches": 0,
            "wins": 0,
            "draws": 0,
            "losses": 0,
            "goals_for": 0,
            "goals_against": 0,
        }
    
    def _parse_matches(self, matches_data: List) -> List[Dict]:
        """Parse match data from API response"""
        parsed = []
        
        for match in matches_data:
            parsed_match = {
                "match_id": str(match.get("id")),
                "home_team": match.get("homeTeam", {}).get("name"),
                "away_team": match.get("awayTeam", {}).get("name"),
                "date": match.get("utcDate"),
                "status": match.get("status"),
                "home_score": match.get("score", {}).get("fullTime", {}).get("home"),
                "away_score": match.get("score", {}).get("fullTime", {}).get("away"),
                "venue": match.get("venue"),
            }
            parsed.append(parsed_match)
        
        return parsed


class ESPNDataSource(DataSource):
    """Data source for ESPN API"""
    
    BASE_URL = "https://site.api.espn.com/v2"
    
    async def fetch_matches(
        self,
        league: str,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None
    ) -> List[Dict]:
        """Fetch matches from ESPN"""
        try:
            # Map league to ESPN league code
            league_map = {
                "EPL": "eng.1",
                "LA_LIGA": "esp.1",
                "SERIE_A": "ita.1",
                "BUNDESLIGA": "ger.1",
                "LIGUE_1": "fra.1",
            }
            
            league_code = league_map.get(league)
            if not league_code:
                logger.warning(f"League {league} not supported in ESPN")
                return []
            
            url = f"{self.BASE_URL}/sites/espn/site/leagues/{league_code}/events"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        matches = self._parse_matches(data.get("events", []))
                        logger.info(f"Fetched {len(matches)} matches from ESPN")
                        return matches
                    else:
                        logger.error(f"ESPN API error: {resp.status}")
                        return []
        
        except Exception as e:
            logger.error(f"Error fetching from ESPN: {str(e)}")
            return []
    
    async def fetch_team_stats(self, team_name: str) -> Dict:
        """Fetch team statistics from ESPN"""
        # Placeholder implementation
        return {
            "team_name": team_name,
            "matches": 0,
            "wins": 0,
            "draws": 0,
            "losses": 0,
            "goals_for": 0,
            "goals_against": 0,
        }
    
    def _parse_matches(self, events_data: List) -> List[Dict]:
        """Parse match data from ESPN API response"""
        parsed = []
        
        for event in events_data:
            competitors = event.get("competitions", [{}])[0].get("competitors", [])
            
            if len(competitors) >= 2:
                home_team = competitors[0].get("team", {}).get("name")
                away_team = competitors[1].get("team", {}).get("name")
                
                parsed_match = {
                    "match_id": event.get("id"),
                    "home_team": home_team,
                    "away_team": away_team,
                    "date": event.get("date"),
                    "status": event.get("status", {}).get("type"),
                    "home_score": competitors[0].get("score"),
                    "away_score": competitors[1].get("score"),
                    "venue": event.get("competitions", [{}])[0].get("venue", {}).get("fullName"),
                }
                parsed.append(parsed_match)
        
        return parsed


class WebScraperDataSource(DataSource):
    """Data source using web scraping"""
    
    async def fetch_matches(
        self,
        league: str,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None
    ) -> List[Dict]:
        """Fetch matches using web scraping"""
        try:
            # This would need to be implemented with specific website scraping
            # Example using a football results website
            
            logger.info(f"Fetching matches for {league} using web scraping")
            return []
        
        except Exception as e:
            logger.error(f"Error fetching matches via web scraper: {str(e)}")
            return []
    
    async def fetch_team_stats(self, team_name: str) -> Dict:
        """Fetch team statistics using web scraping"""
        # Placeholder implementation
        return {
            "team_name": team_name,
            "matches": 0,
            "wins": 0,
            "draws": 0,
            "losses": 0,
            "goals_for": 0,
            "goals_against": 0,
        }


class DataFetcher:
    """Main data fetcher orchestrating multiple sources"""
    
    def __init__(self):
        self.sources: Dict[str, DataSource] = {}
        self._initialize_sources()
    
    def _initialize_sources(self):
        """Initialize all data sources"""
        # Football-Data.org
        if settings.FOOTBALL_DATA_API_KEY:
            self.sources["football_data"] = FootballDataSource(
                api_key=settings.FOOTBALL_DATA_API_KEY
            )
        
        # ESPN
        self.sources["espn"] = ESPNDataSource()
        
        # Web Scraper
        self.sources["web_scraper"] = WebScraperDataSource()
        
        logger.info(f"Initialized {len(self.sources)} data sources")
    
    async def fetch_matches(
        self,
        league: str,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        sources: Optional[List[str]] = None
    ) -> List[Dict]:
        """Fetch matches from specified sources"""
        
        if sources is None:
            sources = list(self.sources.keys())
        
        all_matches = []
        tasks = []
        
        for source_name in sources:
            if source_name in self.sources:
                task = self.sources[source_name].fetch_matches(
                    league, date_from, date_to
                )
                tasks.append(task)
        
        if not tasks:
            logger.warning(f"No valid sources specified: {sources}")
            return []
        
        # Fetch from all sources concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Error fetching matches: {result}")
            else:
                all_matches.extend(result)
        
        # Remove duplicates based on match_id
        unique_matches = {m["match_id"]: m for m in all_matches}.values()
        
        logger.info(f"Total matches fetched: {len(unique_matches)}")
        return list(unique_matches)
    
    async def fetch_team_stats(
        self,
        team_name: str,
        source: str = "football_data"
    ) -> Dict:
        """Fetch team statistics"""
        
        if source not in self.sources:
            logger.warning(f"Data source {source} not found")
            return {}
        
        stats = await self.sources[source].fetch_team_stats(team_name)
        return stats


# Global fetcher instance
_fetcher: Optional[DataFetcher] = None


def get_fetcher() -> DataFetcher:
    """Get global data fetcher instance"""
    global _fetcher
    if _fetcher is None:
        _fetcher = DataFetcher()
    return _fetcher


# Example usage
if __name__ == "__main__":
    async def main():
        fetcher = get_fetcher()
        
        # Fetch matches for English Premier League
        matches = await fetcher.fetch_matches(
            league="EPL",
            date_from=datetime.now() - timedelta(days=7),
            date_to=datetime.now() + timedelta(days=7)
        )
        
        print(f"Fetched {len(matches)} matches")
        for match in matches[:5]:
            print(match)
    
    asyncio.run(main())
