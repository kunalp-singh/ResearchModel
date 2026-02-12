import pickle
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler

# Load model
print("Loading CICIDS2017 model...")
with open('models/ddos_rf_cicids2017.pkl', 'rb') as f:
    model = pickle.load(f)
with open('models/ddos_scaler.pkl', 'rb') as f:
    scaler = pickle.load(f)
with open('models/ddos_features.pkl', 'rb') as f:
    features = pickle.load(f)

print(f"\nModel expects {len(features)} features: {features}")

def create_features(flow_duration, tot_len_fwd_pkts, fwd_pkt_len_mean, 
                    bwd_pkt_len_mean, flow_iat_mean, pkt_len_var):
    """Create all 12 features including engineered ones"""
    # Base features
    base = {
        'FlowDuration': flow_duration,
        'TotLenFwdPkts': tot_len_fwd_pkts,
        'FwdPktLenMean': fwd_pkt_len_mean,
        'BwdPktLenMean': bwd_pkt_len_mean,
        'FlowIATMean': flow_iat_mean,
        'PktLenVar': pkt_len_var
    }
    
    # Engineered features (matching training script)
    base['FwdBwdPktLenRatio'] = fwd_pkt_len_mean / (bwd_pkt_len_mean + 1)
    base['FlowDurationPerPkt'] = flow_duration / (tot_len_fwd_pkts + 1)
    base['IATPerPkt'] = flow_iat_mean / (tot_len_fwd_pkts + 1)
    base['LogFlowDuration'] = np.log1p(flow_duration)
    base['LogPktLenVar'] = np.log1p(pkt_len_var)
    base['FlowDuration_x_IAT'] = flow_duration * flow_iat_mean / 1e12
    
    return pd.DataFrame([base])[features]

print("\n" + "="*60)
print("TESTING MODEL WITH EXACT CICIDS2017 MEAN VALUES")
print("="*60)

# Test 1: EXACT BENIGN MEAN VALUES
benign_features = create_features(
    10559848,   # FlowDuration
    504,        # TotLenFwdPkts
    49,         # FwdPktLenMean
    170,        # BwdPktLenMean
    987982,     # FlowIATMean
    78194       # PktLenVar
)
benign_scaled = scaler.transform(benign_features)
benign_pred = model.predict_proba(benign_scaled)[0][1]
print(f"\n✅ BENIGN (exact mean): {benign_pred*100:.2f}% threat score")
print(f"   Classification: {'SAFE' if benign_pred < 0.20 else 'UNCERTAIN' if benign_pred < 0.80 else 'ATTACK'}")

# Test 2: EXACT DDoS MEAN VALUES
ddos_features = create_features(
    17173264,   # FlowDuration (62% higher)
    32,         # TotLenFwdPkts (94% LOWER!)
    7,          # FwdPktLenMean (85% LOWER!)
    1469,       # BwdPktLenMean (765% HIGHER!)
    1896305,    # FlowIATMean (92% higher)
    4230655     # PktLenVar (5300% HIGHER!)
)
ddos_scaled = scaler.transform(ddos_features)
ddos_pred = model.predict_proba(ddos_scaled)[0][1]
print(f"\n🚨 DDoS (exact mean): {ddos_pred*100:.2f}% threat score")
print(f"   Classification: {'SAFE' if ddos_pred < 0.20 else 'UNCERTAIN' if ddos_pred < 0.80 else 'ATTACK'}")

# Test 3: BENIGN with small variation
print("\n" + "="*60)
print("TESTING WITH SMALL RANDOM VARIATIONS")
print("="*60)

import random
for i in range(3):
    benign_variant = create_features(
        random.uniform(8000000, 13000000),      # FlowDuration ±25%
        random.uniform(400, 650),                # TotLenFwdPkts ±20%
        random.uniform(40, 60),                  # FwdPktLenMean ±20%
        random.uniform(140, 210),                # BwdPktLenMean ±20%
        random.uniform(700000, 1300000),         # FlowIATMean ±30%
        random.uniform(60000, 100000)            # PktLenVar ±25%
    )
    scaled = scaler.transform(benign_variant)
    pred = model.predict_proba(scaled)[0][1]
    print(f"  Benign variant {i+1}: {pred*100:.2f}% {'✅ SAFE' if pred < 0.20 else '⚠️ UNCERTAIN'}")

for i in range(3):
    ddos_variant = create_features(
        random.uniform(14000000, 21000000),      # FlowDuration ±20%
        random.uniform(20, 45),                  # TotLenFwdPkts ±30%
        random.uniform(5, 10),                   # FwdPktLenMean ±30%
        random.uniform(1100, 1900),              # BwdPktLenMean ±30%
        random.uniform(1400000, 2400000),        # FlowIATMean ±25%
        random.uniform(3000000, 5500000)         # PktLenVar ±30%
    )
    scaled = scaler.transform(ddos_variant)
    pred = model.predict_proba(scaled)[0][1]
    print(f"  DDoS variant {i+1}: {pred*100:.2f}% {'🚨 ATTACK' if pred > 0.80 else '⚠️ UNCERTAIN'}")

print("\n" + "="*60)
