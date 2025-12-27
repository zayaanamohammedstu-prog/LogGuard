"""
Anomaly Detection Model for LogGuard
Uses Isolation Forest algorithm to detect anomalies in server logs
"""
import os
import joblib
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from typing import Tuple, List, Dict


class AnomalyDetector:
    """Anomaly detection using Isolation Forest"""
    
    def __init__(self, contamination: float = 0.1):
        """
        Initialize anomaly detector
        
        Args:
            contamination: Expected proportion of outliers in the dataset
        """
        self.contamination = contamination
        self.model = IsolationForest(
            contamination=contamination,
            random_state=42,
            n_estimators=100
        )
        self.scaler = StandardScaler()
        self.is_trained = False
        self.feature_names = None
    
    def train(self, X: pd.DataFrame) -> None:
        """
        Train the anomaly detection model
        
        Args:
            X: Training data (numerical features)
        """
        if X.empty:
            raise ValueError("Training data is empty")
        
        self.feature_names = X.columns.tolist()
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Train model
        self.model.fit(X_scaled)
        self.is_trained = True
        
        print(f"Model trained on {len(X)} samples")
    
    def predict(self, X: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """
        Predict anomalies
        
        Args:
            X: Feature data
            
        Returns:
            Tuple of (predictions, anomaly_scores)
            predictions: -1 for anomaly, 1 for normal
            anomaly_scores: Lower scores indicate anomalies
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before prediction")
        
        if X.empty:
            return np.array([]), np.array([])
        
        # Ensure feature order matches training
        X = X[self.feature_names]
        
        # Scale features
        X_scaled = self.scaler.transform(X)
        
        # Predict
        predictions = self.model.predict(X_scaled)
        anomaly_scores = self.model.score_samples(X_scaled)
        
        return predictions, anomaly_scores
    
    def detect_anomalies(self, X: pd.DataFrame) -> List[int]:
        """
        Detect anomalies and return indices
        
        Args:
            X: Feature data
            
        Returns:
            List of indices where anomalies were detected
        """
        predictions, _ = self.predict(X)
        anomaly_indices = np.where(predictions == -1)[0].tolist()
        return anomaly_indices
    
    def save_model(self, model_path: str, scaler_path: str) -> None:
        """
        Save trained model to disk
        
        Args:
            model_path: Path to save model
            scaler_path: Path to save scaler
        """
        if not self.is_trained:
            raise ValueError("Cannot save untrained model")
        
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        os.makedirs(os.path.dirname(scaler_path), exist_ok=True)
        
        joblib.dump({
            'model': self.model,
            'feature_names': self.feature_names,
            'contamination': self.contamination
        }, model_path)
        joblib.dump(self.scaler, scaler_path)
        
        print(f"Model saved to {model_path}")
        print(f"Scaler saved to {scaler_path}")
    
    def load_model(self, model_path: str, scaler_path: str) -> None:
        """
        Load trained model from disk
        
        Args:
            model_path: Path to model file
            scaler_path: Path to scaler file
        """
        if not os.path.exists(model_path) or not os.path.exists(scaler_path):
            raise FileNotFoundError("Model files not found")
        
        model_data = joblib.load(model_path)
        self.model = model_data['model']
        self.feature_names = model_data['feature_names']
        self.contamination = model_data['contamination']
        self.scaler = joblib.load(scaler_path)
        self.is_trained = True
        
        print(f"Model loaded from {model_path}")
    
    def get_anomaly_report(self, df: pd.DataFrame, X: pd.DataFrame) -> List[Dict]:
        """
        Generate detailed anomaly report
        
        Args:
            df: Original DataFrame with all log data
            X: Feature DataFrame
            
        Returns:
            List of dictionaries containing anomaly details
        """
        predictions, scores = self.predict(X)
        
        anomalies = []
        for idx, (pred, score) in enumerate(zip(predictions, scores)):
            if pred == -1:  # Anomaly detected
                anomaly_info = {
                    'index': idx,
                    'anomaly_score': float(score),
                    'timestamp': str(df.iloc[idx]['timestamp']) if 'timestamp' in df.columns else 'N/A',
                    'ip': df.iloc[idx]['ip'] if 'ip' in df.columns else 'N/A',
                    'severity': df.iloc[idx]['severity'] if 'severity' in df.columns else 'N/A',
                    'status_code': int(df.iloc[idx]['status_code']) if 'status_code' in df.columns else 0,
                    'response_time': int(df.iloc[idx]['response_time']) if 'response_time' in df.columns else 0,
                    'raw_log': df.iloc[idx]['raw_log'] if 'raw_log' in df.columns else 'N/A',
                }
                anomalies.append(anomaly_info)
        
        return anomalies
