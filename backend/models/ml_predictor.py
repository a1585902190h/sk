"""
Machine Learning Models for Football Prediction

Includes:
- Logistic Regression
- Random Forest
- XGBoost
- LightGBM
"""

import numpy as np
import pandas as pd
from typing import Dict, Tuple, Optional
from datetime import datetime
from joblib import dump, load

from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
import xgboost as xgb
import lightgbm as lgb

from utils.logger import get_logger

logger = get_logger(__name__)


class MLPredictorBase:
    """Base class for ML predictors"""
    
    def __init__(self, model_name: str):
        self.model_name = model_name
        self.model = None
        self.scaler = StandardScaler()
        self.feature_names = None
        self.is_trained = False
    
    def train(self, X: pd.DataFrame, y: pd.Series) -> Dict:
        """Train the model"""
        logger.info(f"Training {self.model_name} model")
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        self.feature_names = X.columns.tolist()
        
        # Train model
        self.model.fit(X_scaled, y)
        self.is_trained = True
        
        # Get training metrics
        train_score = self.model.score(X_scaled, y)
        logger.info(f"Training completed. Accuracy: {train_score:.4f}")
        
        return {
            "model_name": self.model_name,
            "training_accuracy": train_score,
            "features_count": len(self.feature_names),
            "training_time": datetime.utcnow().isoformat(),
        }
    
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """Make predictions"""
        if not self.is_trained:
            raise ValueError(f"Model {self.model_name} is not trained yet")
        
        X_scaled = self.scaler.transform(X)
        return self.model.predict(X_scaled)
    
    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        """Predict probabilities"""
        if not self.is_trained:
            raise ValueError(f"Model {self.model_name} is not trained yet")
        
        X_scaled = self.scaler.transform(X)
        if hasattr(self.model, 'predict_proba'):
            return self.model.predict_proba(X_scaled)
        else:
            logger.warning(f"{self.model_name} does not support predict_proba")
            return None
    
    def evaluate(self, X: pd.DataFrame, y: pd.Series) -> Dict:
        """Evaluate model performance"""
        from sklearn.metrics import (
            accuracy_score,
            precision_score,
            recall_score,
            f1_score,
            roc_auc_score,
            confusion_matrix,
        )
        
        logger.info(f"Evaluating {self.model_name} model")
        
        y_pred = self.predict(X)
        y_pred_proba = self.predict_proba(X)
        
        metrics = {
            "accuracy": accuracy_score(y, y_pred),
            "precision": precision_score(y, y_pred, average='weighted', zero_division=0),
            "recall": recall_score(y, y_pred, average='weighted', zero_division=0),
            "f1_score": f1_score(y, y_pred, average='weighted', zero_division=0),
        }
        
        if y_pred_proba is not None:
            try:
                metrics["auc_roc"] = roc_auc_score(y, y_pred_proba, multi_class='ovr')
            except:
                metrics["auc_roc"] = None
        
        logger.info(f"Evaluation metrics: {metrics}")
        return metrics
    
    def save(self, filepath: str):
        """Save model to file"""
        logger.info(f"Saving {self.model_name} model to {filepath}")
        dump(self.model, filepath)
    
    def load(self, filepath: str):
        """Load model from file"""
        logger.info(f"Loading {self.model_name} model from {filepath}")
        self.model = load(filepath)
        self.is_trained = True


class LogisticRegressionPredictor(MLPredictorBase):
    """Logistic Regression classifier for match prediction"""
    
    def __init__(self):
        super().__init__("logistic_regression")
        self.model = LogisticRegression(
            max_iter=1000,
            random_state=42,
            solver='lbfgs',
            multi_class='multinomial'
        )


class RandomForestPredictor(MLPredictorBase):
    """Random Forest classifier for match prediction"""
    
    def __init__(self):
        super().__init__("random_forest")
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            n_jobs=-1,
        )


class XGBoostPredictor(MLPredictorBase):
    """XGBoost classifier for match prediction"""
    
    def __init__(self):
        super().__init__("xgboost")
        self.model = xgb.XGBClassifier(
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            random_state=42,
            objective='multi:softprob',
            tree_method='hist',
            n_jobs=-1,
        )


class LightGBMPredictor(MLPredictorBase):
    """LightGBM classifier for match prediction"""
    
    def __init__(self):
        super().__init__("lightgbm")
        self.model = lgb.LGBMClassifier(
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            random_state=42,
            n_jobs=-1,
        )


class MLEnsemblePredictor:
    """Ensemble of multiple ML models"""
    
    def __init__(self):
        self.models = {
            "logistic_regression": LogisticRegressionPredictor(),
            "random_forest": RandomForestPredictor(),
            "xgboost": XGBoostPredictor(),
            "lightgbm": LightGBMPredictor(),
        }
        self.weights = {
            "logistic_regression": 0.15,
            "random_forest": 0.25,
            "xgboost": 0.35,
            "lightgbm": 0.25,
        }
    
    def train(self, X: pd.DataFrame, y: pd.Series) -> Dict:
        """Train all models"""
        logger.info("Training ML ensemble")
        
        results = {}
        for model_name, model in self.models.items():
            results[model_name] = model.train(X, y)
        
        logger.info("Ensemble training completed")
        return results
    
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """Ensemble prediction"""
        logger.info("Making ensemble prediction")
        
        predictions = []
        for model_name, model in self.models.items():
            pred = model.predict_proba(X)
            if pred is not None:
                weight = self.weights[model_name]
                predictions.append(pred * weight)
        
        ensemble_pred = np.sum(predictions, axis=0)
        return np.argmax(ensemble_pred, axis=1)
    
    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        """Ensemble probability prediction"""
        predictions = []
        for model_name, model in self.models.items():
            pred = model.predict_proba(X)
            if pred is not None:
                weight = self.weights[model_name]
                predictions.append(pred * weight)
        
        return np.sum(predictions, axis=0)
    
    def evaluate(self, X: pd.DataFrame, y: pd.Series) -> Dict:
        """Evaluate ensemble performance"""
        logger.info("Evaluating ML ensemble")
        
        results = {}
        for model_name, model in self.models.items():
            results[model_name] = model.evaluate(X, y)
        
        return results


if __name__ == "__main__":
    # Example usage
    from sklearn.datasets import make_classification
    from sklearn.model_selection import train_test_split
    
    # Generate sample data
    X, y = make_classification(n_samples=1000, n_features=20, n_classes=3, n_informative=15)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    X_train = pd.DataFrame(X_train)
    X_test = pd.DataFrame(X_test)
    y_train = pd.Series(y_train)
    y_test = pd.Series(y_test)
    
    # Train models
    rf_model = RandomForestPredictor()
    rf_model.train(X_train, y_train)
    metrics = rf_model.evaluate(X_test, y_test)
    print(f"Random Forest Metrics: {metrics}")
