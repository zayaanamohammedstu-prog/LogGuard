"""
Flask Web Application for LogGuard
Provides REST API and web interface for anomaly detection
"""
import os
import sys
import tempfile
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from datetime import datetime
import pandas as pd

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ml_engine.log_parser import LogParser
from ml_engine.anomaly_detector import AnomalyDetector
import config

app = Flask(__name__, 
           template_folder='../templates',
           static_folder='../static')
CORS(app)

# Initialize ML components
parser = LogParser()
detector = AnomalyDetector(contamination=config.CONTAMINATION)

# Load trained model if exists
model_loaded = False
try:
    if os.path.exists(config.MODEL_FILE) and os.path.exists(config.SCALER_FILE):
        detector.load_model(config.MODEL_FILE, config.SCALER_FILE)
        model_loaded = True
        print("Model loaded successfully")
    else:
        print("No trained model found. Please train a model first.")
except Exception as e:
    print(f"Error loading model: {e}")


@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html', model_loaded=model_loaded)


@app.route('/api/status', methods=['GET'])
def get_status():
    """Get system status"""
    return jsonify({
        'status': 'running',
        'model_loaded': model_loaded,
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/analyze', methods=['POST'])
def analyze_logs():
    """
    Analyze logs for anomalies
    Accepts either a file upload or text input
    """
    if not model_loaded:
        return jsonify({
            'error': 'Model not loaded. Please train a model first.'
        }), 400
    
    try:
        # Check if file was uploaded
        if 'file' in request.files:
            file = request.files['file']
            if file.filename == '':
                return jsonify({'error': 'No file selected'}), 400
            
            # Validate file extension
            allowed_extensions = {'.log', '.txt'}
            file_ext = os.path.splitext(file.filename)[1].lower()
            if file_ext not in allowed_extensions:
                return jsonify({'error': 'Invalid file type. Only .log and .txt files are allowed'}), 400
            
            # Save temporarily and parse using secure temp file
            with tempfile.NamedTemporaryFile(mode='wb', suffix='.log', delete=False) as temp_file:
                temp_path = temp_file.name
                file.save(temp_path)
            
            try:
                df = parser.parse_log_file(temp_path)
            finally:
                # Ensure temp file is deleted
                if os.path.exists(temp_path):
                    os.remove(temp_path)
        
        # Check if text was provided
        elif request.json and 'logs' in request.json:
            log_text = request.json['logs']
            # Parse line by line
            parsed_logs = []
            for line in log_text.split('\n'):
                parsed = parser.parse_log_line(line)
                if parsed:
                    parsed_logs.append(parsed)
            
            df = pd.DataFrame(parsed_logs)
        
        else:
            return jsonify({'error': 'No logs provided'}), 400
        
        if df.empty:
            return jsonify({'error': 'No valid logs found'}), 400
        
        # Extract features and detect anomalies
        X = parser.extract_features(df)
        anomalies = detector.get_anomaly_report(df, X)
        
        # Calculate statistics
        total_logs = len(df)
        anomaly_count = len(anomalies)
        anomaly_percentage = (anomaly_count / total_logs * 100) if total_logs > 0 else 0
        
        # Categorize anomalies by severity
        severity_counts = {}
        for anomaly in anomalies:
            severity = anomaly.get('severity', 'UNKNOWN')
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        return jsonify({
            'success': True,
            'total_logs': total_logs,
            'anomaly_count': anomaly_count,
            'anomaly_percentage': round(anomaly_percentage, 2),
            'severity_counts': severity_counts,
            'anomalies': anomalies[:100]  # Limit to first 100 anomalies
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/analyze-line', methods=['POST'])
def analyze_single_line():
    """Analyze a single log line"""
    if not model_loaded:
        return jsonify({
            'error': 'Model not loaded. Please train a model first.'
        }), 400
    
    try:
        if not request.json:
            return jsonify({'error': 'Invalid JSON request'}), 400
        
        data = request.json
        log_line = data.get('log_line', '')
        
        if not log_line:
            return jsonify({'error': 'No log line provided'}), 400
        
        # Parse log line
        parsed = parser.parse_log_line(log_line)
        if not parsed:
            return jsonify({'error': 'Could not parse log line'}), 400
        
        df = pd.DataFrame([parsed])
        X = parser.extract_features(df)
        
        # Predict
        predictions, scores = detector.predict(X)
        is_anomaly = predictions[0] == -1
        anomaly_score = float(scores[0])
        
        return jsonify({
            'success': True,
            'is_anomaly': bool(is_anomaly),
            'anomaly_score': anomaly_score,
            'parsed_data': {
                'timestamp': str(parsed.get('timestamp', 'N/A')),
                'ip': parsed.get('ip', 'N/A'),
                'severity': parsed.get('severity', 'N/A'),
                'status_code': parsed.get('status_code', 'N/A'),
                'response_time': parsed.get('response_time', 'N/A'),
            }
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(
        host=config.FLASK_HOST,
        port=config.FLASK_PORT,
        debug=config.DEBUG
    )
