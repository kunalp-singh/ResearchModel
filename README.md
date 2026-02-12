# 🛡️ SecurNet - Network Security & Threat Detection System

SecurNet is a production-ready cybersecurity application that uses machine learning to detect DDoS attacks and identify phishing URLs in real-time. Built with Flask and powered by state-of-the-art ML models trained on real-world datasets.

## ✨ Features

- **🚨 DDoS Detection**: Real-time network traffic analysis using Random Forest model trained on CICIDS2017 dataset
  - 99.98% accuracy with 1.0000 AUC-ROC
  - 25-second monitoring window with live visualization
  - Professional security reports with traffic metrics
  
- **🎣 Phishing URL Detection**: Advanced URL analysis using LightGBM with 18 lexical features
  - 80.28% accuracy with 0.8960 AUC-ROC
  - Trusted domain whitelist for instant verification
  - Three-tier classification: Trusted → Legitimate → Suspicious → Phishing
  
- **📊 Live Dashboard**: Interactive web interface with real-time charts and alerts
  - Real-time traffic visualization with Chart.js
  - Professional ASCII-bordered security reports
  - Color-coded threat indicators

- **🔒 Production Ready**: Professional logging, input validation, and error handling
  - Waitress WSGI server for production deployment
  - 7-layer input validation
  - RotatingFileHandler with configurable debug mode

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Windows/Linux/Mac OS
- Admin/sudo privileges (for network monitoring)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/kunalp-singh/ResearchModel.git
   cd ResearchModel
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Start the application**
   ```bash
   # Windows
   START_FLASK.bat
   
   # Linux/Mac (requires sudo for network monitoring)
   sudo python flask_app.py
   ```

4. **Access the dashboard**
   ```
   http://127.0.0.1:5000
   ```

## 📊 Project Structure

```
SecurNet/
├── flask_app.py              # Main Flask application with API endpoints
├── requirements.txt          # Python dependencies
├── START_FLASK.bat           # Windows startup script
├── restart_flask.ps1         # PowerShell restart script
│
├── models/                   # Pre-trained ML models (production-ready)
│   ├── ddos_rf_cicids2017.pkl       # DDoS Random Forest model (65MB)
│   ├── ddos_scaler.pkl              # Feature scaler
│   ├── ddos_features.pkl            # Feature names
│   ├── ddos_model_info.pkl          # Model metadata
│   └── phishing_lightgbm.txt        # Phishing LightGBM model (20MB)
│
├── scripts/                  # Training scripts for model retraining
│   ├── train_ddos_cicids2017.py     # DDoS model training
│   └── train_phishing.py            # Phishing model training
│
├── static/                   # Frontend assets
│   ├── css/style.css                # UI styles
│   └── js/main.js                   # Frontend logic & visualization
│
├── templates/
│   └── index.html                   # Web dashboard
│
└── test_model_direct.py      # Model testing script
```

## 🎯 Usage

### DDoS Detection

1. Click **"Start Monitoring"** button
2. Wait for 25-second scan to complete
3. View detailed security report with:
   - Threat assessment and risk level
   - Traffic metrics (flow duration, bytes/sec, packets/sec)
   - Actionable recommendations

### Phishing URL Check

1. Enter URL in the input field
2. Click **"Check URL"**
3. Instant analysis with:
   - Verdict (Trusted/Legitimate/Suspicious/Phishing)
   - Risk level and confidence score
   - Detailed security recommendations

### Simulate Attack

- Click **"Simulate Attack"** to test DDoS detection with attack patterns
- Useful for demonstration and testing

## 🔧 Configuration

### Debug Mode

Enable detailed logging for troubleshooting:

```bash
# Windows PowerShell
$env:SECURNET_DEBUG="true"
python flask_app.py

# Windows CMD
set SECURNET_DEBUG=true
python flask_app.py

# Linux/Mac
export SECURNET_DEBUG=true
python flask_app.py
```

### Port Configuration

Default port is 5000. To change:

```python
# In flask_app.py, modify:
serve(app, host='127.0.0.1', port=5000)  # Change port here
```

## 📊 Model Performance

### DDoS Detection (Random Forest on CICIDS2017)

| Metric | Value |
|--------|-------|
| Accuracy | 99.98% |
| AUC-ROC | 1.0000 |
| False Positives | 2 out of 18,591 samples (0.01%) |
| Training Samples | 1.8M real network packets |
| Features | 12 (6 base + 6 engineered) |

**Features Used:**
- Base: FlowDuration, TotLenFwdPkts, FwdPktLenMean, BwdPktLenMean, FlowIATMean, PktLenVar
- Engineered: FwdBwdRatio, FlowDurationPerPkt, IATPerPkt, LogFlowDuration, LogPktLenVar, FlowDuration_x_IAT

### Phishing Detection (LightGBM)

| Metric | Value |
|--------|-------|
| Accuracy | 80.28% |
| AUC-ROC | 0.8960 |
| Precision | 84.06% |
| Training Samples | 782K URLs |
| Features | 18 lexical features |

## 📚 Datasets

Pre-trained models are included, but you can retrain with your own data:

### CICIDS2017 Dataset (DDoS Detection)
- **Source**: [Canadian Institute for Cybersecurity](https://www.unb.ca/cic/datasets/ids-2017.html)
- **Size**: ~3.1 GB (8 CSV files)
- **Location**: `TrafficLabelling/` directory
- **Purpose**: Real network traffic with labeled attacks

### Phishing URL Dataset
- **Source**: [Kaggle - Phishing Site URLs](https://www.kaggle.com/datasets/taruntiwarihp/phishing-site-urls)
- **Size**: 782K URLs
- **Location**: `datasets/phishing_site_urls.csv`
- **Purpose**: URL pattern analysis

**Note**: Datasets are excluded from repository (3.9GB total). Download instructions in [IMPROVEMENTS.md](IMPROVEMENTS.md#datasets).

## 🔄 Retraining Models

### Retrain Phishing Model
```bash
python scripts/train_phishing.py
```

Expected output:
```
Cross-Validation Results:
  Accuracy:  0.8028 ± 0.0005
  AUC-ROC:   0.8960 ± 0.0006

Model saved to: models/phishing_lightgbm.txt
```

### Retrain DDoS Model
```bash
python scripts/train_ddos_cicids2017.py
```

Expected output:
```
Final Test Set Performance:
  Accuracy:  0.9998 (99.98%)
  AUC-ROC:   1.0000

Model saved to: models/ddos_rf_cicids2017.pkl
```

### Test Models
```bash
python test_model_direct.py
```

Expected output:
```
✅ BENIGN: 0.00% threat score - SAFE
🚨 DDoS: 87.77% threat score - ATTACK
```

## 🧪 API Testing

### Test Endpoints

```bash
# Test phishing detection
python test_flask_api.py
```

Or use curl:

```bash
# Phishing URL
curl -X POST http://127.0.0.1:5000/phishing \
  -H "Content-Type: application/json" \
  -d '{"url":"http://secure-login-verify.tk/bank"}'

# Response: {"pred":0.95,"verdict":"phishing","confidence":"high"}

# Legitimate URL
curl -X POST http://127.0.0.1:5000/phishing \
  -H "Content-Type: application/json" \
  -d '{"url":"https://www.google.com"}'

# Response: {"pred":0.01,"verdict":"legitimate","trusted":true}
```

### Monitor Network (requires network activity simulation)
```bash
curl -X POST http://127.0.0.1:5000/monitor \
  -H "Content-Type: application/json" \
  -d '{"force_ddos":false}'

# Response: {"pred":0.02,"simulated":false,"model_type":"rf_cicids2017"}
```

## 🛠️ Technologies Used

- **Backend**: Python 3.8+, Flask 2.3.3, Waitress 2.1.2 (Production WSGI)
- **Machine Learning**: 
  - scikit-learn 1.3.0 (Random Forest)
  - lightgbm 4.0.0 (Gradient Boosting)
  - imbalanced-learn 0.11.0 (SMOTE)
- **Data Processing**: pandas 2.0.3, numpy 1.24.3
- **Visualization**: Chart.js (frontend), seaborn 0.12.2 (training)
- **Logging**: Python logging with RotatingFileHandler
- **Frontend**: HTML5, CSS3, JavaScript ES6

## 📈 Performance Benchmarks

| Operation | Time | Memory |
|-----------|------|--------|
| Flask Startup | ~3s | ~150MB |
| DDoS Model Loading | ~1s | ~65MB |
| Phishing Model Loading | ~0.5s | ~20MB |
| DDoS Prediction | ~6ms | +5MB |
| Phishing Prediction | ~2.5ms | +2MB |
| Network Scan (25s) | 25s | +50MB |

## 🔒 Security Features

- ✅ Input validation with length limits (10-2000 characters)
- ✅ Content-Type verification
- ✅ JSON parsing with error handling
- ✅ Model availability checks
- ✅ Trusted domain whitelist
- ✅ Rate limiting (can be added via Flask-Limiter)
- ✅ HTTPS ready (use reverse proxy like nginx)

## 🐛 Troubleshooting

### Port 5000 already in use
```bash
# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:5000 | xargs kill -9
```

### Models not loading
```bash
# Check if model files exist
ls models/

# If missing, retrain
python scripts/train_ddos_cicids2017.py
python scripts/train_phishing.py
```

### Import errors
```bash
# Reinstall all dependencies
pip install -r requirements.txt --force-reinstall
```

### Permission denied (network monitoring)
```bash
# Run with admin/sudo privileges
sudo python flask_app.py  # Linux/Mac
# Right-click "Run as Administrator" on Windows
```

## 📝 License

This project is for educational and research purposes. Please review dataset licenses before commercial use:
- CICIDS2017: Research purposes
- Phishing URLs: CC BY 4.0

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/improvement`)
3. Commit changes (`git commit -am 'Add new feature'`)
4. Push to branch (`git push origin feature/improvement`)
5. Create Pull Request

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/kunalp-singh/ResearchModel/issues)
- **Documentation**: See [IMPROVEMENTS.md](IMPROVEMENTS.md) for technical details

## 🎓 Research & References

- **CICIDS2017 Dataset**: [CSE-CIC-IDS2017](https://www.unb.ca/cic/datasets/ids-2017.html)
- **Random Forest**: Breiman, L. (2001). Random Forests. Machine Learning.
- **LightGBM**: Ke et al. (2017). LightGBM: A Highly Efficient Gradient Boosting Decision Tree.

---

**Version**: 1.0.0  
**Last Updated**: February 12, 2026  
**Status**: 🟢 Production Ready
