"""
Data Processor Module - Processes and cleans fetched football data
"""

import pandas as pd
import numpy as np
from datetime import datetime
from typing import List, Dict, Tuple, Optional

from utils.logger import get_logger

logger = get_logger(__name__)


class DataProcessor:
    """Processes raw football data"""
    
    def __init__(self):
        self.data = None
    
    def load_data(self, data: List[Dict]) -> pd.DataFrame:
        """Load raw data into DataFrame"""
        logger.info(f"Loading {len(data)} records into DataFrame")
        
        self.data = pd.DataFrame(data)
        logger.info(f"Loaded data shape: {self.data.shape}")
        
        return self.data
    
    def clean_data(self) -> pd.DataFrame:
        """Clean and standardize data"""
        logger.info("Starting data cleaning")
        
        # Remove duplicates
        self.data = self.data.drop_duplicates()
        logger.info(f"Removed duplicates. New shape: {self.data.shape}")
        
        # Handle missing values
        self.data = self._handle_missing_values()
        
        # Standardize column names
        self.data.columns = self.data.columns.str.lower().str.replace(' ', '_')
        
        # Convert data types
        self.data = self._convert_data_types()
        
        logger.info(f"Data cleaning completed. Final shape: {self.data.shape}")
        return self.data
    
    def _handle_missing_values(self) -> pd.DataFrame:
        """Handle missing values in data"""
        logger.info("Handling missing values")
        
        # Fill numeric columns with median
        numeric_columns = self.data.select_dtypes(include=[np.number]).columns
        for col in numeric_columns:
            if self.data[col].isnull().any():
                self.data[col] = self.data[col].fillna(self.data[col].median())
        
        # Fill categorical columns with mode
        categorical_columns = self.data.select_dtypes(include=['object']).columns
        for col in categorical_columns:
            if self.data[col].isnull().any():
                self.data[col] = self.data[col].fillna(self.data[col].mode()[0] if not self.data[col].mode().empty else 'Unknown')
        
        logger.info("Missing values handled")
        return self.data
    
    def _convert_data_types(self) -> pd.DataFrame:
        """Convert data types appropriately"""
        logger.info("Converting data types")
        
        # Convert date columns
        date_columns = ['date', 'utc_date', 'kickoff_time', 'scheduled']
        for col in date_columns:
            if col in self.data.columns:
                self.data[col] = pd.to_datetime(self.data[col], errors='coerce')
        
        # Convert boolean columns
        bool_columns = ['is_finished', 'is_live', 'is_upcoming']
        for col in bool_columns:
            if col in self.data.columns:
                self.data[col] = self.data[col].astype(bool)
        
        logger.info("Data types converted")
        return self.data
    
    def extract_matches(self) -> pd.DataFrame:
        """Extract match data with key information"""
        logger.info("Extracting match data")
        
        # Select and rename relevant columns
        match_columns = {
            'match_id': 'id',
            'home_team': ['home_team', 'home_team_name'],
            'away_team': ['away_team', 'away_team_name'],
            'home_score': ['home_score', 'full_time_home_team'],
            'away_score': ['away_score', 'full_time_away_team'],
            'date': ['date', 'utc_date'],
            'league': ['competition', 'league'],
            'status': ['status', 'state'],
        }
        
        matches = self.data.copy()
        
        for target_col, source_cols in match_columns.items():
            if isinstance(source_cols, list):
                for col in source_cols:
                    if col in matches.columns:
                        matches[target_col] = matches[col]
                        break
            else:
                if source_cols in matches.columns:
                    matches[target_col] = matches[source_cols]
        
        logger.info(f"Extracted {len(matches)} matches")
        return matches
    
    def aggregate_team_stats(self, matches: pd.DataFrame) -> Dict[str, Dict]:
        """Aggregate team statistics from matches"""
        logger.info("Aggregating team statistics")
        
        team_stats = {}
        
        # Process home teams
        home_stats = matches.groupby('home_team').agg({
            'home_score': ['sum', 'mean', 'std'],
            'away_score': ['sum', 'mean', 'std'],
            'match_id': 'count',
        }).reset_index()
        
        # Process away teams
        away_stats = matches.groupby('away_team').agg({
            'away_score': ['sum', 'mean', 'std'],
            'home_score': ['sum', 'mean', 'std'],
            'match_id': 'count',
        }).reset_index()
        
        logger.info(f"Aggregated statistics for {len(team_stats)} teams")
        return team_stats
    
    def normalize_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normalize numeric features"""
        logger.info("Normalizing features")
        
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        
        for col in numeric_columns:
            mean = df[col].mean()
            std = df[col].std()
            if std > 0:
                df[col] = (df[col] - mean) / std
        
        logger.info(f"Normalized {len(numeric_columns)} numeric features")
        return df
    
    def get_summary_statistics(self) -> Dict:
        """Get summary statistics of processed data"""
        logger.info("Calculating summary statistics")
        
        return {
            "total_records": len(self.data),
            "shape": self.data.shape,
            "columns": list(self.data.columns),
            "dtypes": self.data.dtypes.to_dict(),
            "missing_values": self.data.isnull().sum().to_dict(),
            "summary": self.data.describe().to_dict(),
        }


if __name__ == "__main__":
    # Example usage
    sample_data = [
        {
            "id": 1,
            "home_team": "Team A",
            "away_team": "Team B",
            "home_score": 2,
            "away_score": 1,
            "date": "2024-01-15",
        }
    ]
    
    processor = DataProcessor()
    processor.load_data(sample_data)
    processor.clean_data()
    stats = processor.get_summary_statistics()
    print(f"Summary: {stats}")
