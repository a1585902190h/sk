"""
ELO Rating System for Football Match Prediction

The ELO rating system was originally designed for chess but can be adapted for football.
It's a simple yet effective method that updates ratings based on match results.
"""

import math
from typing import Dict, Tuple, Optional
from datetime import datetime

from utils.logger import get_logger

logger = get_logger(__name__)


class ELOPredictor:
    """
    ELO Rating System for Football Predictions
    
    The ELO system works by:
    1. Assigning each team a rating (starting at 1500)
    2. Calculating expected win probability based on rating difference
    3. Updating ratings after match results
    
    Key parameters:
    - K factor: Controls how much ratings change (higher K = more volatile)
    - Home advantage: Bonus points for playing at home
    """
    
    def __init__(self, k_factor: float = 32.0, home_advantage: float = 60.0):
        """
        Initialize ELO predictor
        
        Args:
            k_factor: Controls rating volatility (default: 32)
            home_advantage: Home team rating bonus (default: 60)
        """
        self.k_factor = k_factor
        self.home_advantage = home_advantage
        self.ratings: Dict[str, float] = {}
        self.initial_rating = 1500.0
        
        logger.info(f"Initialized ELO predictor: k_factor={k_factor}, "
                   f"home_advantage={home_advantage}")
    
    def get_team_rating(self, team_name: str) -> float:
        """Get current rating for a team"""
        if team_name not in self.ratings:
            self.ratings[team_name] = self.initial_rating
        return self.ratings[team_name]
    
    def set_team_rating(self, team_name: str, rating: float):
        """Set rating for a team"""
        self.ratings[team_name] = max(0, rating)  # Prevent negative ratings
    
    def calculate_win_probability(
        self,
        home_rating: float,
        away_rating: float
    ) -> Tuple[float, float, float]:
        """
        Calculate win probabilities using ELO formula
        
        Args:
            home_rating: Home team ELO rating
            away_rating: Away team ELO rating
        
        Returns:
            Tuple of (home_win_prob, draw_prob, away_win_prob)
        """
        # ELO formula for expected score
        rating_diff = home_rating - away_rating
        expected_home = 1.0 / (1.0 + math.pow(10, -rating_diff / 400.0))
        expected_away = 1.0 - expected_home
        
        # Estimate draw probability based on close ratings
        # Teams with very different ratings are less likely to draw
        rating_diff_abs = abs(rating_diff)
        draw_probability = 0.25 * math.exp(-rating_diff_abs / 1500.0)
        
        # Adjust win probabilities
        home_win_prob = expected_home * (1 - draw_probability)
        away_win_prob = expected_away * (1 - draw_probability)
        
        return (
            round(home_win_prob, 4),
            round(draw_probability, 4),
            round(away_win_prob, 4)
        )
    
    def predict_match(
        self,
        home_team: str,
        away_team: str,
    ) -> Dict:
        """
        Predict match outcome
        
        Args:
            home_team: Home team name
            away_team: Away team name
        
        Returns:
            Dictionary with prediction results
        """
        # Get team ratings
        home_rating = self.get_team_rating(home_team)
        away_rating = self.get_team_rating(away_team)
        
        # Apply home advantage
        adjusted_home_rating = home_rating + self.home_advantage
        
        # Calculate probabilities
        home_win_prob, draw_prob, away_win_prob = self.calculate_win_probability(
            adjusted_home_rating,
            away_rating
        )
        
        # Determine most likely outcome
        probs = {
            "home_win": home_win_prob,
            "draw": draw_prob,
            "away_win": away_win_prob
        }
        predicted_result = max(probs, key=probs.get)
        confidence = probs[predicted_result]
        
        prediction = {
            "model_name": "elo",
            "home_team": home_team,
            "away_team": away_team,
            "home_rating": round(home_rating, 2),
            "away_rating": round(away_rating, 2),
            "home_win_probability": home_win_prob,
            "draw_probability": draw_prob,
            "away_win_probability": away_win_prob,
            "predicted_result": predicted_result,
            "confidence_score": confidence,
            "timestamp": datetime.utcnow().isoformat(),
        }
        
        logger.debug(f"ELO Prediction: {home_team} vs {away_team} - {prediction}")
        
        return prediction
    
    def update_ratings(
        self,
        home_team: str,
        away_team: str,
        home_score: int,
        away_score: int,
    ):
        """
        Update ELO ratings after match result
        
        Args:
            home_team: Home team name
            away_team: Away team name
            home_score: Goals scored by home team
            away_score: Goals scored by away team
        """
        # Get current ratings
        home_rating = self.get_team_rating(home_team)
        away_rating = self.get_team_rating(away_team)
        
        # Apply home advantage for rating calculation
        adjusted_home_rating = home_rating + self.home_advantage
        
        # Calculate expected scores
        expected_home = 1.0 / (1.0 + math.pow(10, -(adjusted_home_rating - away_rating) / 400.0))
        expected_away = 1.0 - expected_home
        
        # Determine actual result
        if home_score > away_score:
            home_result = 1.0  # Win
            away_result = 0.0  # Loss
        elif home_score < away_score:
            home_result = 0.0  # Loss
            away_result = 1.0  # Win
        else:
            home_result = 0.5  # Draw
            away_result = 0.5  # Draw
        
        # Apply goal difference factor (larger wins cause bigger rating changes)
        goal_diff = abs(home_score - away_score)
        goal_factor = math.log(max(goal_diff, 1) + 1) / math.log(2)
        
        # Calculate rating changes
        home_change = self.k_factor * goal_factor * (home_result - expected_home)
        away_change = self.k_factor * goal_factor * (away_result - expected_away)
        
        # Update ratings
        new_home_rating = home_rating + home_change
        new_away_rating = away_rating + away_change
        
        self.set_team_rating(home_team, new_home_rating)
        self.set_team_rating(away_team, new_away_rating)
        
        logger.info(
            f"Updated ELO ratings: {home_team} "
            f"{home_rating:.0f}->{new_home_rating:.0f}, "
            f"{away_team} {away_rating:.0f}->{new_away_rating:.0f}"
        )
    
    def get_top_teams(self, n: int = 10) -> list:
        """Get top N teams by ELO rating"""
        sorted_teams = sorted(
            self.ratings.items(),
            key=lambda x: x[1],
            reverse=True
        )
        return [(team, round(rating, 2)) for team, rating in sorted_teams[:n]]
    
    def reset_ratings(self):
        """Reset all ratings to initial value"""
        self.ratings = {}
        logger.info("Reset all ELO ratings to initial value")
    
    def to_dict(self) -> Dict:
        """Export ratings to dictionary"""
        return {
            team: round(rating, 2)
            for team, rating in self.ratings.items()
        }
    
    def from_dict(self, ratings_dict: Dict):
        """Import ratings from dictionary"""
        self.ratings = {
            team: float(rating)
            for team, rating in ratings_dict.items()
        }
        logger.info(f"Loaded {len(self.ratings)} team ratings from dictionary")


# Example usage
if __name__ == "__main__":
    # Initialize predictor
    elo = ELOPredictor()
    
    # Set initial ratings for teams
    elo.set_team_rating("Manchester United", 1600)
    elo.set_team_rating("Liverpool", 1650)
    elo.set_team_rating("Manchester City", 1700)
    elo.set_team_rating("Arsenal", 1580)
    
    # Make prediction
    prediction = elo.predict_match("Manchester United", "Liverpool")
    print("Prediction:", prediction)
    
    # Update ratings after match
    elo.update_ratings("Manchester United", "Liverpool", 2, 1)
    print("Updated ratings:", elo.to_dict())
    
    # Get top teams
    print("Top teams:", elo.get_top_teams())
