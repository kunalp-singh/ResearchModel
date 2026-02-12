import requests
import json
import time

print("\n🔍 DEBUGGING FLASK MODEL PREDICTIONS\n" + "="*60)

# Test 1: Safe network
print("\nTest 1: SAFE NETWORK")
print("Sending request...")
start = time.time()
response1 = requests.post(
    'http://127.0.0.1:5000/monitor',
    json={'force_ddos': False},
    timeout=35
)
duration1 = time.time() - start
result1 = response1.json()
print(f"Duration: {duration1:.1f}s")
print(f"Response: {json.dumps(result1, indent=2)}")

# Test 2: DDoS attack
print("\n" + "="*60)
print("\nTest 2: DDoS ATTACK")
print("Sending request...")
start = time.time()
response2 = requests.post(
    'http://127.0.0.1:5000/monitor',    
    json={'force_ddos': True},
    timeout=35
)
duration2 = time.time() - start
result2 = response2.json()
print(f"Duration: {duration2:.1f}s")
print(f"Response: {json.dumps(result2, indent=2)}")

print("\n" + "="*60)
print(f"\n✅ Safe network: {result1['pred']*100:.2f}% (should be <20%)")
print(f"🚨 DDoS attack: {result2['pred']*100:.2f}% (should be >80%)")

if result1['pred'] < 0.20 and result2['pred'] > 0.80:
    print("\n🎉 PERFECT! Both tests passed!")
else:
    print("\n⚠️ ERROR: Flask not using updated code or model issue!")
    print("   Check if Flask restarted properly")
