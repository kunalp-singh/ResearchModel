"""
Train DDoS Detection Model with REAL CICIDS2017 Dataset
This should give MUCH better accuracy than the synthetic ddos_paper.csv!
"""
import pandas as pd
import numpy as np
import pickle
import os
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score, accuracy_score
from imblearn.over_sampling import SMOTE
import warnings

# Filter only specific warnings, not all
warnings.filterwarnings('ignore', category=FutureWarning)
warnings.filterwarnings('ignore', category=DeprecationWarning)

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

print("="*70)
print("DDoS Detection Training with REAL CICIDS2017 Dataset")
print("="*70)

# ============================================================
# Load CICIDS2017 Data
# ============================================================
print("\n[1/7] Loading CICIDS2017 dataset...")
print("This is REAL network traffic data - much better than synthetic!")

# CICIDS2017 feature names (with spaces)
CICIDS_FEATURES = {
    'FlowDuration': ' Flow Duration',
    'TotLenFwdPkts': ' Total Length of Fwd Packets',
    'FwdPktLenMean': ' Fwd Packet Length Mean',
    'BwdPktLenMean': ' Bwd Packet Length Mean',
    'FlowIATMean': ' Flow IAT Mean',
    'PktLenVar': ' Packet Length Variance'
}

# Files to load
traffic_files = [
    'TrafficLabelling/Friday-WorkingHours-Afternoon-DDos.pcap_ISCX.csv',  # DDoS attacks
    'TrafficLabelling/Monday-WorkingHours.pcap_ISCX.csv',                  # Benign
    'TrafficLabelling/Tuesday-WorkingHours.pcap_ISCX.csv',                 # Benign
    'TrafficLabelling/Wednesday-workingHours.pcap_ISCX.csv',               # Benign
    'TrafficLabelling/Friday-WorkingHours-Morning.pcap_ISCX.csv'           # Benign
]

dfs = []
for file in traffic_files:
    filepath = os.path.join(PROJECT_DIR, file)
    if os.path.exists(filepath):
        print(f"  Loading {os.path.basename(file)}...")
        df = pd.read_csv(filepath)
        
        # Filter for DDoS and BENIGN only
        label_col = ' Label' if ' Label' in df.columns else 'Label'
        df_filtered = df[df[label_col].isin(['BENIGN', 'DDoS'])]
        
        if len(df_filtered) > 0:
            dfs.append(df_filtered)
            print(f"    → Found {len(df_filtered)} samples")
            print(f"    → Labels: {df_filtered[label_col].value_counts().to_dict()}")

if len(dfs) == 0:
    print("\n❌ ERROR: No data loaded!")
    print("Make sure TrafficLabelling/*.csv files exist in project directory")
    exit(1)

# Combine all data
print("\n[2/7] Combining datasets...")
df_combined = pd.concat(dfs, ignore_index=True)
print(f"Total samples loaded: {len(df_combined)}")

# ============================================================
# Extract Features with Additional Feature Engineering
# ============================================================
print("\n[3/7] Extracting features with feature engineering...")

# Map CICIDS column names to our feature names
try:
    feature_data = {}
    for our_name, cicids_name in CICIDS_FEATURES.items():
        if cicids_name in df_combined.columns:
            feature_data[our_name] = df_combined[cicids_name]
        else:
            print(f"  ⚠️ Warning: {cicids_name} not found, trying without space...")
            cicids_name_nospace = cicids_name.strip()
            if cicids_name_nospace in df_combined.columns:
                feature_data[our_name] = df_combined[cicids_name_nospace]
            else:
                print(f"  ❌ ERROR: Cannot find column for {our_name}")
                print(f"  Available columns: {list(df_combined.columns)[:20]}")
                exit(1)
    
    X = pd.DataFrame(feature_data)
    
    # FEATURE ENGINEERING: Add derived features for better pattern detection
    print("  Adding engineered features...")
    
    # Ratio features (detect anomalous patterns)
    X['FwdBwdPktLenRatio'] = X['FwdPktLenMean'] / (X['BwdPktLenMean'] + 1)  # Avoid division by zero
    X['FlowDurationPerPkt'] = X['FlowDuration'] / (X['TotLenFwdPkts'] + 1)
    X['IATPerPkt'] = X['FlowIATMean'] / (X['TotLenFwdPkts'] + 1)
    
    # Log-transformed features (handle skewed distributions)
    X['LogFlowDuration'] = np.log1p(X['FlowDuration'])
    X['LogPktLenVar'] = np.log1p(X['PktLenVar'])
    
    # Interaction features (capture non-linear relationships)
    X['FlowDuration_x_IAT'] = X['FlowDuration'] * X['FlowIATMean'] / 1e12  # Normalize
    
    print(f"  Total features after engineering: {len(X.columns)}")
    
    # Extract labels
    label_col = ' Label' if ' Label' in df_combined.columns else 'Label'
    y = df_combined[label_col].apply(lambda x: 1 if 'DDoS' in str(x) else 0)
    
    # Remove rows with NaN or infinite values
    print("  Cleaning data (removing NaN and infinity)...")
    mask = ~(X.isnull().any(axis=1) | np.isinf(X).any(axis=1))
    X = X[mask]
    y = y[mask]
    
    print(f"\n  Features: {list(X.columns)}")
    print(f"  Samples after cleaning: {len(X)}")
    print(f"  Class distribution:")
    print(f"    - Benign (0): {(y == 0).sum()} ({(y == 0).sum() / len(y) * 100:.1f}%)")
    print(f"    - DDoS (1):   {(y == 1).sum()} ({(y == 1).sum() / len(y) * 100:.1f}%)")
    
except Exception as e:
    print(f"\n❌ ERROR during feature extraction: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# ============================================================
# Handle Class Imbalance with SMOTE
# ============================================================
print("\n[4/7] Applying SMOTE for class balancing...")
if len(X) < 10000:
    # If dataset is small, use all data
    print("  Using regular SMOTE...")
    smote = SMOTE(random_state=42)
    X_balanced, y_balanced = smote.fit_resample(X, y)
else:
    # If dataset is large, sample first to speed up training
    print("  Large dataset detected - sampling 50K for training...")
    X_sample, _, y_sample, _ = train_test_split(X, y, train_size=50000, 
                                                  random_state=42, stratify=y)
    smote = SMOTE(random_state=42)
    X_balanced, y_balanced = smote.fit_resample(X_sample, y_sample)

print(f"  After SMOTE: {len(X_balanced)} samples")
print(f"    - Benign: {(y_balanced == 0).sum()}")
print(f"    - DDoS:   {(y_balanced == 1).sum()}")

# ============================================================
# Scale Features
# ============================================================
print("\n[5/7] Scaling features...")
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X_balanced)

# ============================================================
# Train Optimized Random Forest with Better Hyperparameters
# ============================================================
print("\n[6/7] Training optimized Random Forest model...")
print("  Using REAL network traffic data for much better accuracy!")

X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, y_balanced, test_size=0.2, random_state=42, stratify=y_balanced
)

# Optimized Random Forest with better hyperparameters
rf_model = RandomForestClassifier(
    n_estimators=400,        # Increased from 300
    max_depth=25,            # Increased from 20
    min_samples_split=8,     # Reduced for more splits
    min_samples_leaf=3,      # Reduced for finer splits
    max_features='sqrt',     # Faster training
    max_samples=0.8,         # Bootstrap sampling
    class_weight='balanced',
    random_state=42,
    n_jobs=-1,
    verbose=1,
    oob_score=True           # Out-of-bag score for validation
)

print("\n  Training Random Forest (400 trees with OOB scoring)...")
rf_model.fit(X_train, y_train)

# Out-of-bag score
if hasattr(rf_model, 'oob_score_'):
    print(f"\n  Out-of-Bag Score: {rf_model.oob_score_:.4f}")

# Cross-validation
print("\n  Performing 5-Fold Cross-Validation...")
kfold = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
cv_scores = cross_val_score(rf_model, X_scaled, y_balanced, cv=kfold, 
                             scoring='roc_auc', n_jobs=-1, verbose=0)
print(f"  CV AUC scores: {[f'{s:.4f}' for s in cv_scores]}")
print(f"  Mean AUC: {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")

# ============================================================
# Evaluate on Test Set
# ============================================================
print("\n[7/7] Evaluating on test set...")
y_pred = rf_model.predict(X_test)
y_pred_proba = rf_model.predict_proba(X_test)[:, 1]

accuracy = accuracy_score(y_test, y_pred)
auc = roc_auc_score(y_test, y_pred_proba)

print("\n" + "="*70)
print("FINAL TEST SET PERFORMANCE - CICIDS2017 Dataset")
print("="*70)
print(f"\n✅ Accuracy:  {accuracy:.4f} ({accuracy*100:.1f}%)")
print(f"✅ AUC-ROC:   {auc:.4f}")

cm = confusion_matrix(y_test, y_pred)
print(f"\nConfusion Matrix:")
print(f"  TN={cm[0,0]:6d}  FP={cm[0,1]:6d}")
print(f"  FN={cm[1,0]:6d}  TP={cm[1,1]:6d}")

print("\nClassification Report:")
print(classification_report(y_test, y_pred, target_names=['Benign', 'DDoS']))

# Feature Importance
print("\nFeature Importance:")
feature_importance = pd.DataFrame({
    'feature': X.columns,
    'importance': rf_model.feature_importances_
}).sort_values('importance', ascending=False)
print(feature_importance.to_string(index=False))

# ============================================================
# Save Model
# ============================================================
print("\n" + "="*70)
print("Saving model artifacts...")
print("="*70)

# Save Random Forest model
model_path = os.path.join(PROJECT_DIR, "models/ddos_rf_cicids2017.pkl")
with open(model_path, 'wb') as f:
    pickle.dump(rf_model, f)
print(f"✓ Model saved to: {model_path}")

# Save scaler
scaler_path = os.path.join(PROJECT_DIR, "models/ddos_scaler.pkl")
with open(scaler_path, 'wb') as f:
    pickle.dump(scaler, f)
print(f"✓ Scaler saved to: {scaler_path}")

# Save feature names
features_path = os.path.join(PROJECT_DIR, "models/ddos_features.pkl")
with open(features_path, 'wb') as f:
    pickle.dump(list(X.columns), f)
print(f"✓ Features saved to: {features_path}")

# Save model info
info = {
    'model_type': 'RandomForest',
    'model_name': 'CICIDS2017_DDoS_Detector',
    'accuracy': float(accuracy),
    'auc': float(auc),
    'training_samples': len(X_balanced),
    'features': list(X.columns),
    'dataset': 'CICIDS2017'
}
info_path = os.path.join(PROJECT_DIR, "models/ddos_model_info.pkl")
with open(info_path, 'wb') as f:
    pickle.dump(info, f)
print(f"✓ Model info saved to: {info_path}")

print("\n" + "="*70)
print("✅ TRAINING COMPLETE!")
print("="*70)
print(f"""
📊 Summary:
   Dataset: CICIDS2017 (Real Network Traffic)
   Training Samples: {len(X_balanced):,}
   Model: Random Forest (300 trees)
   Accuracy: {accuracy*100:.1f}%
   AUC-ROC: {auc:.4f}

🎯 Comparison with old model:
   Old (synthetic data): 62% accuracy, 0.66 AUC
   New (CICIDS2017):     {accuracy*100:.1f}% accuracy, {auc:.4f} AUC
   Improvement:          +{(accuracy-0.62)*100:.1f}% accuracy

💡 To use in Flask:
   The model has been saved to models/ddos_rf_cicids2017.pkl
   Flask will automatically detect and use this improved model!
   Just restart the Flask app.
""")
print("="*70)
