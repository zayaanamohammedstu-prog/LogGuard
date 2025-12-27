"""
Log Parser Module for LogGuard
Extracts features from server logs for anomaly detection
"""
import re
from datetime import datetime
from typing import Dict, List, Optional
import pandas as pd


class LogParser:
    """Parser for server log files"""
    
    def __init__(self):
        self.patterns = {
            'timestamp': r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})',
            'ip': r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})',
            'severity': r'(INFO|WARNING|ERROR|CRITICAL|DEBUG)',
            'status_code': r'\s(\d{3})\s',
            'response_time': r'(\d+)ms',
            'method': r'(GET|POST|PUT|DELETE|PATCH)',
            'endpoint': r'\"[A-Z]+\s([^\s\"]+)',
        }
    
    def parse_log_line(self, line: str) -> Optional[Dict]:
        """
        Parse a single log line and extract features
        
        Args:
            line: Raw log line string
            
        Returns:
            Dictionary containing extracted features or None if parsing fails
        """
        if not line or line.strip() == '':
            return None
            
        features = {}
        
        # Extract timestamp
        timestamp_match = re.search(self.patterns['timestamp'], line)
        if timestamp_match:
            try:
                dt = datetime.strptime(timestamp_match.group(1), '%Y-%m-%d %H:%M:%S')
                features['timestamp'] = dt
                features['hour'] = dt.hour
                features['minute'] = dt.minute
                features['day_of_week'] = dt.weekday()
            except ValueError:
                return None
        else:
            return None
        
        # Extract IP address
        ip_match = re.search(self.patterns['ip'], line)
        features['ip'] = ip_match.group(1) if ip_match else 'unknown'
        
        # Extract severity
        severity_match = re.search(self.patterns['severity'], line)
        features['severity'] = severity_match.group(1) if severity_match else 'INFO'
        features['is_error'] = 1 if features['severity'] in ['ERROR', 'CRITICAL'] else 0
        
        # Extract status code
        status_match = re.search(self.patterns['status_code'], line)
        features['status_code'] = int(status_match.group(1)) if status_match else 200
        
        # Extract response time
        response_match = re.search(self.patterns['response_time'], line)
        features['response_time'] = int(response_match.group(1)) if response_match else 0
        
        # Extract HTTP method
        method_match = re.search(self.patterns['method'], line)
        features['method'] = method_match.group(1) if method_match else 'GET'
        
        # Extract endpoint
        endpoint_match = re.search(self.patterns['endpoint'], line)
        features['endpoint'] = endpoint_match.group(1) if endpoint_match else '/'
        
        features['raw_log'] = line.strip()
        
        return features
    
    def parse_log_file(self, filepath: str) -> pd.DataFrame:
        """
        Parse entire log file
        
        Args:
            filepath: Path to log file
            
        Returns:
            DataFrame containing parsed log entries
        """
        parsed_logs = []
        
        try:
            with open(filepath, 'r') as f:
                for line in f:
                    parsed = self.parse_log_line(line)
                    if parsed:
                        parsed_logs.append(parsed)
        except FileNotFoundError:
            print(f"Error: File {filepath} not found")
            return pd.DataFrame()
        
        return pd.DataFrame(parsed_logs)
    
    def extract_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Extract numerical features for ML model
        
        Args:
            df: DataFrame with parsed logs
            
        Returns:
            DataFrame with numerical features
        """
        if df.empty:
            return df
        
        # Create a copy for feature extraction
        features_df = df.copy()
        
        # Count requests per IP
        ip_counts = df.groupby('ip').size()
        features_df['request_count'] = features_df['ip'].map(ip_counts)
        
        # Select numerical features
        feature_columns = ['hour', 'minute', 'day_of_week', 'is_error', 
                          'status_code', 'response_time', 'request_count']
        
        return features_df[feature_columns]
