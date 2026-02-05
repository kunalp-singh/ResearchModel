# SecurNet - EPICS Project

SecurNet is a cybersecurity application designed to detect DDoS attacks and identify phishing URLs using machine learning models. It features a web-based interface for live network monitoring and URL analysis.

## Features

- **DDoS Detection**: Real-time network traffic monitoring and analysis using a LightGBM model to detect potential DDoS attacks.
- **Phishing URL Detection**: Analyzes URLs based on lexical features (length, special characters, HTTPS status) to identify phishing attempts.
- **Live Monitoring**: Captures network packets for a specified duration (default: 20 seconds) to calculate flow statistics.
- **Web Interface**: User-friendly dashboard built with Flask.

## Project Structure

```
EPICS Project/
├── flask_app.py          # Main Flask application entry point
├── models/               # Directory containing trained ML models
│   ├── ddos_dnn.h5       # Trained model for DDoS detection
│   └── phishing_lightgbm.txt # Trained model for Phishing detection
├── scripts/              # Training scripts
│   ├── train_ddos.py     # Script to train the DDoS model
│   └── train_phishing.py # Script to train the Phishing model
├── datasets/             # Directory for training datasets
├── static/               # Static assets (CSS, JS, images)
├── templates/            # HTML templates for the web interface
└── requirements.txt      # (Optional) Python dependencies
```

## Installation

1.  **Clone the repository** (if applicable) or navigate to the project directory.

2.  **Install Dependencies**:
    Ensure you have Python installed. Install the required libraries:
    ```bash
    pip install flask pandas lightgbm numpy scikit-learn scapy
    ```
    *Note: You may need to run as administrator/root for `scapy` to capture packets.*

3.  **Prepare Models**:
    Ensure the trained models exist in the `models/` directory. If not, you can train them using the scripts in `scripts/`:
    ```bash
    python scripts/train_ddos.py
    python scripts/train_phishing.py
    ```

## Usage

1.  **Start the Application**:
    Run the Flask app:
    ```bash
    sudo python flask_app.py
    ```
    *Note: `sudo` (or running as Administrator on Windows) is often required for `scapy` to sniff network packets.*

2.  **Access the Dashboard**:
    Open your web browser and go to:
    ```
    http://127.0.0.1:5000
    ```

3.  **Features**:
    - **Monitor Network**: Use the monitoring feature to check for DDoS activity.
    - **Check URL**: Enter a URL to check if it's a potential phishing site.

## Technologies Used

- **Backend**: Python, Flask
- **Machine Learning**: LightGBM, Scikit-learn
- **Data Processing**: Pandas, NumPy
- **Network Analysis**: Scapy
- **Frontend**: HTML, CSS (in `static/` and `templates/`)

## Notes

- The application uses `scapy` for packet sniffing, which requires elevated privileges.
- The DDoS detection is based on flow statistics calculated over a 20-second window.
