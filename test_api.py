import requests
import json

# Your local FastAPI server URL
API_URL = "http://127.0.0.1:8000/process_transaction"

print("🚀 Starting FinGuard API End-to-End Test...\n")

# ==========================================
# SCENARIO 1: NORMAL TRANSACTION
# ==========================================
normal_tx = {
    "transaction_id": "TXN-NORMAL-001",
    "Time": 10.0, "Amount": 25.50,
    # Normal PCA values (mostly close to 0)
    "V1": -0.5, "V2": 0.5, "V3": 1.2, "V4": -0.2, "V5": 0.1, 
    "V6": 0.0, "V7": 0.3, "V8": 0.0, "V9": 0.1, "V10": -0.1,
    "V11": -0.2, "V12": 0.5, "V13": -0.1, "V14": 0.2, "V15": 0.8, 
    "V16": 0.1, "V17": -0.3, "V18": 0.2, "V19": 0.1, "V20": 0.0,
    "V21": -0.1, "V22": 0.2, "V23": 0.0, "V24": 0.1, "V25": 0.2, 
    "V26": 0.0, "V27": 0.0, "V28": 0.0
}

# ==========================================
# SCENARIO 2: HIGHLY SUSPICIOUS TRANSACTION
# ==========================================
fraud_tx = {
    "transaction_id": "TXN-FRAUD-999",
    "Time": 450.0, "Amount": 8500.00,
    # Highly anomalous PCA values (especially V14, V10, V4 based on your SHAP plots)
    "V1": -4.5, "V2": 3.5, "V3": -5.2, "V4": 4.8, "V5": -3.1, 
    "V6": -1.0, "V7": -4.3, "V8": 2.0, "V9": -2.1, "V10": -6.1,
    "V11": 3.2, "V12": -7.5, "V13": -0.5, "V14": -8.2, "V15": 1.8, 
    "V16": -5.1, "V17": -9.3, "V18": -3.2, "V19": 1.1, "V20": 1.5,
    "V21": 1.1, "V22": 0.2, "V23": -0.5, "V24": 0.1, "V25": 0.2, 
    "V26": 0.8, "V27": 1.0, "V28": 0.5
}

def run_test(scenario_name, payload):
    print(f"=========================================")
    print(f"▶️ RUNNING: {scenario_name}")
    print(f"=========================================")
    
    try:
        response = requests.post(API_URL, json=payload)
        data = response.json()
        
        # Pretty print the JSON response
        print(json.dumps(data, indent=2))
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: Cannot connect to the API. Is your FastAPI server running?")
    except Exception as e:
        print(f"❌ Error: {e}")
    print("\n")

# Run the tests!
run_test("SCENARIO 1 (Safe Customer Purchase)", normal_tx)
run_test("SCENARIO 2 (Simulated Fraud Attack)", fraud_tx)