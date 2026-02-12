# Dataset Information

This project uses two datasets that are not included in the repository due to their large size.

## 📊 Required Datasets

### 1. CICIDS2017 Dataset (DDoS Detection)
**Location:** `TrafficLabelling/` directory

**Source:** [Canadian Institute for Cybersecurity](https://www.unb.ca/cic/datasets/ids-2017.html)

**Files needed:**
- `Monday-WorkingHours.pcap_ISCX.csv`
- `Tuesday-WorkingHours.pcap_ISCX.csv`
- `Wednesday-workingHours.pcap_ISCX.csv`
- `Thursday-WorkingHours-Morning-WebAttacks.pcap_ISCX.csv`
- `Thursday-WorkingHours-Afternoon-Infilteration.pcap_ISCX.csv`
- `Friday-WorkingHours-Morning.pcap_ISCX.csv`
- `Friday-WorkingHours-Afternoon-PortScan.pcap_ISCX.csv`
- `Friday-WorkingHours-Afternoon-DDos.pcap_ISCX.csv`

**Total size:** ~3.1 GB

### 2. Phishing URL Dataset
**Location:** `datasets/phishing_site_urls.csv`

**Source:** [Kaggle - Phishing Site URLs](https://www.kaggle.com/datasets/taruntiwarihp/phishing-site-urls)

**Size:** ~782,000 URLs

## 🚀 Setup Instructions

1. **Download CICIDS2017:**
   ```bash
   # Create directory
   mkdir TrafficLabelling
   
   # Download from: https://www.unb.ca/cic/datasets/ids-2017.html
   # Extract CSV files to TrafficLabelling/ directory
   ```

2. **Download Phishing Dataset:**
   ```bash
   # Create directory
   mkdir datasets
   
   # Download from: https://www.kaggle.com/datasets/taruntiwarihp/phishing-site-urls
   # Place phishing_site_urls.csv in datasets/ directory
   ```

3. **Verify Setup:**
   ```bash
   python check_columns.py  # Check CICIDS2017 files
   python list_cols.py      # List available columns
   ```

4. **Train Models:**
   ```bash
   python scripts/train_ddos_cicids2017.py    # Train DDoS model
   python scripts/train_phishing.py            # Train phishing model
   ```

## 📝 Notes

- **Pre-trained models** are included in `models/` directory
- You can run the Flask app without datasets (uses pre-trained models)
- Datasets are only needed for retraining models
- Total dataset size: ~3.9 GB (excluded from git)

## 🔒 Data Privacy

Both datasets are publicly available for research purposes. Please review their respective licenses before use.
