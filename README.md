# 🛡️ LogGuard - Intelligent IT Audit System

LogGuard is a project that combines Machine Learning and Web Development to create an intelligent IT audit system for automated anomaly detection in server logs. The system helps IT auditors proactively identify suspicious activities, potential security threats, and operational issues.

## ✨ Features

- 🤖 **Machine Learning-based Anomaly Detection**: Uses Isolation Forest algorithm to identify unusual patterns in server logs
- 📊 **Real-time Analysis**: Analyze logs in real-time through web interface or API
- 🔍 **Pattern Recognition**: Automatically detects suspicious activities and security threats
- 📈 **Comprehensive Reporting**: Detailed statistics and visualizations of detected anomalies
- ⚡ **Fast Processing**: Efficiently handles large log files
- 🌐 **Web Interface**: User-friendly dashboard for log analysis and monitoring
- 🔌 **REST API**: Easy integration with existing systems

## 🏗️ Architecture

LogGuard consists of two main components:

1. **ML Engine** (`ml_engine/`):
   - `log_parser.py`: Parses and extracts features from server logs
   - `anomaly_detector.py`: Machine learning model for anomaly detection using Isolation Forest

2. **Web Application** (`web_app/`):
   - Flask-based REST API
   - Interactive web dashboard
   - Real-time log analysis capabilities

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/zayaanamohammedstu-prog/LogGuard.git
cd LogGuard
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Train the anomaly detection model:
```bash
python train_model.py
```

This will train the model on the sample logs provided in `data/sample_logs.log`.

4. Start the web application:
```bash
python web_app/app.py
```

5. Open your browser and navigate to:
```
http://localhost:5000
```

## 📖 Usage

### Web Interface

1. **Quick Log Analysis**: Paste a single log line to check if it's anomalous
2. **Batch Analysis**: 
   - Upload a log file or paste multiple log lines
   - View comprehensive analysis results with statistics and detected anomalies
3. **Dashboard**: View detailed reports of anomalies with severity levels and scores

### API Endpoints

#### Check System Status
```bash
curl http://localhost:5000/api/status
```

#### Analyze Single Log Line
```bash
curl -X POST http://localhost:5000/api/analyze-line \
  -H "Content-Type: application/json" \
  -d '{"log_line": "2024-01-15 14:23:45 192.168.1.100 INFO \"GET /api/users 200 45ms\""}'
```

#### Analyze Batch Logs
```bash
curl -X POST http://localhost:5000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"logs": "2024-01-15 08:15:23 192.168.1.100 INFO \"GET /api/users 200 45ms\"\n2024-01-15 08:16:45 192.168.1.101 INFO \"POST /api/login 200 120ms\""}'
```

Or upload a file:
```bash
curl -X POST http://localhost:5000/api/analyze \
  -F "file=@data/sample_logs.log"
```

## 🧪 Training Your Own Model

To train the model on your own log files:

```bash
python train_model.py --log-file path/to/your/logs.log
```

### Log Format

LogGuard expects logs in the following format:
```
YYYY-MM-DD HH:MM:SS IP_ADDRESS SEVERITY "METHOD ENDPOINT STATUS_CODE RESPONSE_TIMEms"
```

Example:
```
2024-01-15 08:15:23 192.168.1.100 INFO "GET /api/users 200 45ms"
2024-01-15 08:35:23 10.0.0.50 ERROR "GET /api/admin 500 5000ms"
```

## 🔧 Configuration

Edit `config.py` to customize:

- Model parameters (contamination rate, thresholds)
- Server settings (host, port)
- Feature extraction settings
- File paths

## 📁 Project Structure

```
LogGuard/
├── ml_engine/              # Machine Learning components
│   ├── __init__.py
│   ├── log_parser.py      # Log parsing and feature extraction
│   └── anomaly_detector.py # Anomaly detection model
├── web_app/               # Web application
│   ├── __init__.py
│   └── app.py            # Flask application
├── templates/             # HTML templates
│   └── index.html        # Main dashboard
├── static/               # Static files
│   ├── css/
│   │   └── style.css    # Stylesheet
│   └── js/
│       └── app.js       # Frontend JavaScript
├── data/                 # Data directory
│   └── sample_logs.log  # Sample log file
├── models/               # Trained models (generated)
├── config.py            # Configuration file
├── train_model.py       # Model training script
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## 🎯 How It Works

1. **Log Parsing**: The system parses server logs and extracts relevant features:
   - Timestamp (hour, minute, day of week)
   - IP address
   - Severity level
   - HTTP status code
   - Response time
   - Request patterns

2. **Feature Engineering**: Numerical features are extracted and normalized:
   - Temporal features (time of day, day of week)
   - Error indicators
   - Performance metrics (response time)
   - Request frequency per IP

3. **Anomaly Detection**: Uses Isolation Forest algorithm to identify outliers:
   - Trained on normal log patterns
   - Detects deviations from expected behavior
   - Assigns anomaly scores to each log entry

4. **Reporting**: Provides detailed analysis:
   - Anomaly count and percentage
   - Severity distribution
   - Individual anomaly details with scores
   - Original log lines for context

## 🔒 Security Use Cases

LogGuard helps identify:

- **Unauthorized Access Attempts**: Unusual login patterns or failed authentication
- **DDoS Attacks**: Abnormal request volumes from specific IPs
- **API Abuse**: Excessive API calls or unusual endpoints
- **System Errors**: Unusual error rates or response times
- **Data Exfiltration**: Suspicious data access patterns
- **Privilege Escalation**: Unauthorized admin access attempts

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## 📄 License

This project is open source and available for educational and commercial use.

## 👤 Author

Created by [zayaanamohammedstu-prog](https://github.com/zayaanamohammedstu-prog)

## 🙏 Acknowledgments

- Isolation Forest algorithm from scikit-learn
- Flask web framework
- The open-source community

---

**Note**: This system is designed to assist IT auditors in identifying potential issues. Always verify anomalies manually before taking action.
