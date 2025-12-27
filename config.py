"""
Configuration file for LogGuard system
"""
import os

# Base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Data directories
DATA_DIR = os.path.join(BASE_DIR, 'data')
MODELS_DIR = os.path.join(BASE_DIR, 'models')
LOGS_DIR = os.path.join(BASE_DIR, 'logs')

# Model configuration
MODEL_FILE = os.path.join(MODELS_DIR, 'anomaly_detector.pkl')
SCALER_FILE = os.path.join(MODELS_DIR, 'scaler.pkl')

# Anomaly detection thresholds
CONTAMINATION = 0.1  # Expected proportion of outliers in the dataset
ANOMALY_SCORE_THRESHOLD = -0.5

# Log patterns
LOG_PATTERNS = {
    'timestamp': r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}',
    'ip': r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}',
    'severity': r'(INFO|WARNING|ERROR|CRITICAL|DEBUG)',
    'status_code': r'\s(\d{3})\s',
}

# Server configuration
FLASK_HOST = '0.0.0.0'
FLASK_PORT = 5000
# Set DEBUG to False in production environment
DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() in ('true', '1', 'yes')

# Feature extraction configuration
FEATURES = [
    'hour',
    'minute',
    'day_of_week',
    'is_error',
    'status_code',
    'response_time',
    'request_count'
]
