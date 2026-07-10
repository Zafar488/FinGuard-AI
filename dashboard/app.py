import streamlit as st
import requests
import time
import os  # 👈 NAYA IMPORT

# 1. Page Configuration
st.set_page_config(page_title="FinGuard AI | Ops Center", page_icon="🛡️", layout="wide", initial_sidebar_state="expanded")

# --- Custom CSS ---
st.markdown("""
    <style>
    .agent-report {
        background-color: #f8f9fa;
        border-left: 5px solid #004085;
        padding: 20px;
        border-radius: 5px;
        font-family: 'Courier New', Courier, monospace;
        color: #000000;
        white-space: pre-wrap;
    }
    .status-blocked { color: #dc3545; font-weight: bold; font-size: 1.2rem;}
    .status-approved { color: #28a745; font-weight: bold; font-size: 1.2rem;}
    .sidebar-text { font-size: 0.9rem; color: #6c757d; }
    </style>
""", unsafe_allow_html=True)

# 🌐 UPDATED API URL LOGIC
# Agar cloud par API_URL set hai toh wo use karo, warna default local (127.0.0.1) use karo.
API_URL = os.getenv("API_URL", "http://127.0.0.1:8000/process_transaction")

# --- Sidebar (System Status) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2716/2716652.png", width=60)
    st.title("System Status")
    st.markdown("---")
    st.success("🟢 ML Engine (XGBoost): **ONLINE**")
    st.success("🟢 Graph Engine (GNN): **ONLINE**")
    st.success("🟢 LangGraph Agents: **ONLINE**")
    st.success("🟢 PostgreSQL DB: **CONNECTED**")
    st.markdown("---")
    st.markdown(f"<p class='sidebar-text'>API Endpoint: {API_URL.split('/')[2]}</p>", unsafe_allow_html=True) # Dikhayega ke konsi API connected hai

# --- UI Header ---
st.title("🛡️ FinGuard AI: Operations Center")
st.markdown("**Autonomous Fraud Detection, Agentic Investigation & Database Logging**")
st.divider()

tab1, tab2 = st.tabs(["🚦 Live Simulator (Presets)", "🔬 Manual Investigation (Custom Input)"])

def analyze_transaction(payload):
    with st.spinner("🧠 FinGuard ML Engine & Agentic AI Analyzing..."):
        time.sleep(0.8) 
        try:
            response = requests.post(API_URL, json=payload)
            
            if response.status_code != 200:
                st.error(f"API Error {response.status_code}: {response.text}")
                return
                
            res = response.json()
            st.markdown("### 📊 Analysis Results")
            
            # SCENARIO 1: FAST-PATH (APPROVED)
            if res.get("status") == "APPROVED":
                st.markdown(f"<p class='status-approved'>✅ {res['status']} | ID: {res['transaction_id']}</p>", unsafe_allow_html=True)
                
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("XGBoost (Tabular)", f"{res['risk_scores'].get('xgboost', 0)}%", delta="Low Risk", delta_color="inverse")
                m2.metric("GNN (Network Risk)", f"{res['risk_scores'].get('gnn_network_risk', 0)}%", delta="Safe Ring", delta_color="inverse")
                m3.metric("Isolation Forest", "Clean")
                m4.metric("Agent Action", "Bypassed")
                
                max_risk = max(res['risk_scores'].get('xgboost', 0), res['risk_scores'].get('gnn_network_risk', 0))
                st.progress(max_risk / 100)
                st.info("💾 Transaction processed instantly via ML & Graph layers and saved to Database.")
                
            # SCENARIO 2: LANGGRAPH INVESTIGATION (BLOCKED)
            elif res.get("status") == "BLOCKED & INVESTIGATED":
                st.markdown(f"<p class='status-blocked'>🚨 {res['status']} | ID: {res['transaction_id']}</p>", unsafe_allow_html=True)
                
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("XGBoost (Tabular)", f"{res['ml_risk_scores'].get('xgboost', 0)}%", delta="High Risk", delta_color="inverse")
                m2.metric("GNN (Network Risk)", f"{res['ml_risk_scores'].get('gnn_network_risk', 0)}%", delta="Fraud Ring Warning", delta_color="inverse")
                
                iso_alert = "⚠️ ANOMALY" if res['ml_risk_scores'].get('isolation_forest_alert') else "Clean"
                m3.metric("Isolation Forest", iso_alert)
                m4.metric("Agent Decision", res['agent_decision'])
                
                max_risk = max(res['ml_risk_scores'].get('xgboost', 0), res['ml_risk_scores'].get('gnn_network_risk', 0))
                st.progress(max_risk / 100)
                st.warning("⚠️ High Risk Detected. FinGuard LangGraph Agent queried the Database & Policies to generate this report.")
                
                st.markdown("### 📑 Official Agentic Case Report")
                with st.container(border=True):
                    st.markdown(f"<div class='agent-report'>{res['agent_case_report']}</div>", unsafe_allow_html=True)

        except requests.exceptions.ConnectionError:
            st.error(f"❌ Connection Error: Cannot reach the FastAPI server at {API_URL}. Is your backend deployed and running?")
        except Exception as e:
            st.error(f"❌ Unexpected Error: {e}")

# TAB 1: PRESET SIMULATOR
with tab1:
    col_sim1, col_sim2 = st.columns([1, 1])
    with col_sim1:
        st.subheader("Simulate Incoming Traffic")
        if st.button("☕ Process Safe Purchase ($25)", use_container_width=True, type="secondary"):
            normal_tx = {"transaction_id": "TXN-NORMAL-001", "Time": 10.0, "Amount": 25.50, "V1": -0.5, "V2": 0.5, "V3": 1.2, "V4": -0.2, "V5": 0.1, "V6": 0.0, "V7": 0.3, "V8": 0.0, "V9": 0.1, "V10": -0.1, "V11": -0.2, "V12": 0.5, "V13": -0.1, "V14": 0.2, "V15": 0.8, "V16": 0.1, "V17": -0.3, "V18": 0.2, "V19": 0.1, "V20": 0.0, "V21": -0.1, "V22": 0.2, "V23": 0.0, "V24": 0.1, "V25": 0.2, "V26": 0.0, "V27": 0.0, "V28": 0.0}
            analyze_transaction(normal_tx)
            
    with col_sim2:
        st.subheader("Simulate Attack Vector")
        if st.button("💸 Process Anomalous Transfer ($8,500)", use_container_width=True, type="primary"):
            fraud_tx = {"transaction_id": "TXN-FRAUD-999", "Time": 450.0, "Amount": 8500.00, "V1": -4.5, "V2": 3.5, "V3": -5.2, "V4": 4.8, "V5": -3.1, "V6": -1.0, "V7": -4.3, "V8": 2.0, "V9": -2.1, "V10": -6.1, "V11": 3.2, "V12": -7.5, "V13": -0.5, "V14": -8.2, "V15": 1.8, "V16": -5.1, "V17": -9.3, "V18": -3.2, "V19": 1.1, "V20": 1.5, "V21": 1.1, "V22": 0.2, "V23": -0.5, "V24": 0.1, "V25": 0.2, "V26": 0.8, "V27": 1.0, "V28": 0.5}
            analyze_transaction(fraud_tx)

# TAB 2: MANUAL INVESTIGATION (CUSTOM INPUT)
with tab2:
    st.subheader("✍️ Enter Custom Transaction Details")
    with st.form("custom_tx_form"):
        c1, c2 = st.columns(2)
        amount_input = c1.number_input("Transaction Amount ($)", min_value=0.0, value=5000.0, step=50.0)
        time_input = c2.number_input("Time (Seconds from Day Start)", min_value=0.0, value=3600.0)
        
        st.markdown("**Key Predictive Features (PCA)**")
        v14_input = st.slider("V14 (Primary Risk Driver)", min_value=-15.0, max_value=15.0, value=-8.5, step=0.1)
        v4_input = st.slider("V4 (Secondary Risk Driver)", min_value=-15.0, max_value=15.0, value=5.0, step=0.1)
        v10_input = st.slider("V10 (Tertiary Risk Driver)", min_value=-15.0, max_value=15.0, value=-6.0, step=0.1)
        
        submitted = st.form_submit_button("🔍 Run Custom Analysis & Save to DB", type="primary")
        
        if submitted:
            custom_payload = {
                "transaction_id": f"TXN-CUSTOM-{int(time.time())}", 
                "Time": time_input, "Amount": amount_input,
                "V1": 0.0, "V2": 0.0, "V3": 0.0, "V4": v4_input, "V5": 0.0, 
                "V6": 0.0, "V7": 0.0, "V8": 0.0, "V9": 0.0, "V10": v10_input,
                "V11": 0.0, "V12": 0.0, "V13": 0.0, "V14": v14_input, "V15": 0.0, 
                "V16": 0.0, "V17": 0.0, "V18": 0.0, "V19": 0.0, "V20": 0.0,
                "V21": 0.0, "V22": 0.0, "V23": 0.0, "V24": 0.0, "V25": 0.0, 
                "V26": 0.0, "V27": 0.0, "V28": 0.0
            }
            analyze_transaction(custom_payload)
