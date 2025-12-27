"""
Training script for LogGuard anomaly detection model
"""
import os
import sys
import argparse

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ml_engine.log_parser import LogParser
from ml_engine.anomaly_detector import AnomalyDetector
import config


def train_model(log_file: str, save_model: bool = True):
    """
    Train anomaly detection model on log data
    
    Args:
        log_file: Path to training log file
        save_model: Whether to save the trained model
    """
    print("=" * 60)
    print("LogGuard Model Training")
    print("=" * 60)
    
    # Initialize parser and detector
    parser = LogParser()
    detector = AnomalyDetector(contamination=config.CONTAMINATION)
    
    # Parse logs
    print(f"\nParsing logs from: {log_file}")
    df = parser.parse_log_file(log_file)
    
    if df.empty:
        print("Error: No valid logs found in file")
        return
    
    print(f"Parsed {len(df)} log entries")
    
    # Extract features
    print("\nExtracting features...")
    X = parser.extract_features(df)
    print(f"Extracted {len(X.columns)} features: {list(X.columns)}")
    
    # Train model
    print("\nTraining anomaly detection model...")
    detector.train(X)
    
    # Test predictions
    print("\nTesting model predictions...")
    predictions, scores = detector.predict(X)
    n_anomalies = (predictions == -1).sum()
    print(f"Detected {n_anomalies} anomalies in training data ({n_anomalies/len(df)*100:.2f}%)")
    
    # Save model
    if save_model:
        print("\nSaving model...")
        os.makedirs(config.MODELS_DIR, exist_ok=True)
        detector.save_model(config.MODEL_FILE, config.SCALER_FILE)
    
    # Generate sample report
    print("\nSample anomaly report:")
    anomalies = detector.get_anomaly_report(df, X)
    for i, anomaly in enumerate(anomalies[:5]):  # Show first 5
        print(f"\n  Anomaly {i+1}:")
        print(f"    Timestamp: {anomaly['timestamp']}")
        print(f"    IP: {anomaly['ip']}")
        print(f"    Severity: {anomaly['severity']}")
        print(f"    Status: {anomaly['status_code']}")
        print(f"    Score: {anomaly['anomaly_score']:.3f}")
    
    if len(anomalies) > 5:
        print(f"\n  ... and {len(anomalies) - 5} more anomalies")
    
    print("\n" + "=" * 60)
    print("Training complete!")
    print("=" * 60)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Train LogGuard anomaly detection model')
    parser.add_argument('--log-file', type=str, 
                       default='data/sample_logs.log',
                       help='Path to training log file')
    parser.add_argument('--no-save', action='store_true',
                       help='Do not save the trained model')
    
    args = parser.parse_args()
    
    train_model(args.log_file, save_model=not args.no_save)
