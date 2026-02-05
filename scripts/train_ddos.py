import pandas as pd
import numpy as np
import lightgbm as lgb
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_predict
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, confusion_matrix, classification_report, roc_curve
)
import matplotlib.pyplot as plt
import os

# Get the script's directory for relative paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)

print("="*60)
print("SecurNet DDoS Detection Model Training")
print("="*60)

# Load dataset
print("\n[1/5] Loading dataset...")
df = pd.read_csv(os.path.join(PROJECT_DIR, "datasets/sample_ddos.csv"))
print(f"Dataset shape: {df.shape}")

# Feature extraction
X = df[["FlowDuration", "PacketLength"]]
y = df["Label"].apply(lambda x: 1 if "DDoS" in x else 0)

print(f"Class distribution:")
print(f"  - Normal (0): {(y == 0).sum()}")
print(f"  - DDoS (1):   {(y == 1).sum()}")

# Scale features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# ============================================================
# Cross-Validation with Stratified K-Fold
# ============================================================
print("\n[2/5] Performing 5-Fold Stratified Cross-Validation...")

kfold = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

# Store metrics for each fold
cv_accuracy = []
cv_precision = []
cv_recall = []
cv_f1 = []
cv_auc = []

for fold, (train_idx, val_idx) in enumerate(kfold.split(X_scaled, y), 1):
    X_train_fold, X_val_fold = X_scaled[train_idx], X_scaled[val_idx]
    y_train_fold, y_val_fold = y.iloc[train_idx], y.iloc[val_idx]
    
    # Train LightGBM model
    model_fold = lgb.LGBMClassifier(
        n_estimators=100,
        learning_rate=0.1,
        max_depth=5,
        random_state=42,
        verbose=-1
    )
    model_fold.fit(X_train_fold, y_train_fold)
    
    # Predictions
    y_pred = model_fold.predict(X_val_fold)
    y_pred_proba = model_fold.predict_proba(X_val_fold)[:, 1]
    
    # Calculate metrics
    cv_accuracy.append(accuracy_score(y_val_fold, y_pred))
    cv_precision.append(precision_score(y_val_fold, y_pred, zero_division=0))
    cv_recall.append(recall_score(y_val_fold, y_pred, zero_division=0))
    cv_f1.append(f1_score(y_val_fold, y_pred, zero_division=0))
    cv_auc.append(roc_auc_score(y_val_fold, y_pred_proba))
    
    print(f"  Fold {fold}: Accuracy={cv_accuracy[-1]:.4f}, F1={cv_f1[-1]:.4f}, AUC={cv_auc[-1]:.4f}")

print("\n" + "-"*60)
print("Cross-Validation Results (Mean ± Std):")
print("-"*60)
print(f"  Accuracy:  {np.mean(cv_accuracy):.4f} ± {np.std(cv_accuracy):.4f}")
print(f"  Precision: {np.mean(cv_precision):.4f} ± {np.std(cv_precision):.4f}")
print(f"  Recall:    {np.mean(cv_recall):.4f} ± {np.std(cv_recall):.4f}")
print(f"  F1-Score:  {np.mean(cv_f1):.4f} ± {np.std(cv_f1):.4f}")
print(f"  AUC-ROC:   {np.mean(cv_auc):.4f} ± {np.std(cv_auc):.4f}")

# ============================================================
# Final Model Training with Train/Test Split
# ============================================================
print("\n[3/5] Training final model with 80/20 split...")

X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, y, test_size=0.2, random_state=42, stratify=y
)

final_model = lgb.LGBMClassifier(
    n_estimators=100,
    learning_rate=0.1,
    max_depth=5,
    random_state=42,
    verbose=-1
)
final_model.fit(X_train, y_train)

# ============================================================
# Final Evaluation on Test Set
# ============================================================
print("\n[4/5] Evaluating on held-out test set...")

y_test_pred = final_model.predict(X_test)
y_test_proba = final_model.predict_proba(X_test)[:, 1]

print("\n" + "="*60)
print("FINAL TEST SET PERFORMANCE METRICS")
print("="*60)
print(f"\nAccuracy:  {accuracy_score(y_test, y_test_pred):.4f}")
print(f"Precision: {precision_score(y_test, y_test_pred, zero_division=0):.4f}")
print(f"Recall:    {recall_score(y_test, y_test_pred, zero_division=0):.4f}")
print(f"F1-Score:  {f1_score(y_test, y_test_pred, zero_division=0):.4f}")
print(f"AUC-ROC:   {roc_auc_score(y_test, y_test_proba):.4f}")

print("\nConfusion Matrix:")
cm = confusion_matrix(y_test, y_test_pred)
print(f"  TN={cm[0,0]:5d}  FP={cm[0,1]:5d}")
print(f"  FN={cm[1,0]:5d}  TP={cm[1,1]:5d}")

print("\nClassification Report:")
print(classification_report(y_test, y_test_pred, target_names=['Normal', 'DDoS']))

# ============================================================
# Save Model
# ============================================================
print("[5/5] Saving model...")
model_path = os.path.join(PROJECT_DIR, "models/ddos_dnn.h5")
final_model.booster_.save_model(model_path)
print(f"Model saved to: {model_path}")

print("\n" + "="*60)
print("DDoS Model Training Complete!")
print("="*60)