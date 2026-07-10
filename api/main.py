from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
import joblib
import xgboost as xgb
import pandas as pd
import numpy as np
import os
import shap
import torch
import torch.nn.functional as F
from torch_geometric.data import Data
from torch_geometric.nn import GCNConv

# 🗄️ Database Imports
from sqlalchemy.orm import Session
from database.database import get_db
from database.models import TransactionRecord

# Import our LangGraph App
from agents.finguard_graph import finguard_app

app = FastAPI(title="FinGuard AI Engine", description="End-to-End Fraud Detection & Investigation API")

# Global variables
scaler = None
iso_forest = None
xgb_model = None
explainer = None
gnn_model = None

# --- GNN Architecture Definition ---
class FraudGNN(torch.nn.Module):
    def __init__(self, num_features):
        super(FraudGNN, self).__init__()
        self.conv1 = GCNConv(num_features, 16)
        self.conv2 = GCNConv(16, 2)

    def forward(self, data):
        x, edge_index = data.x, data.edge_index
        x = self.conv1(x, edge_index)
        x = F.relu(x)
        x = self.conv2(x, edge_index)
        return F.log_softmax(x, dim=1)

class TransactionInput(BaseModel):
    transaction_id: str
    Time: float
    Amount: float
    V1: float; V2: float; V3: float; V4: float; V5: float
    V6: float; V7: float; V8: float; V9: float; V10: float
    V11: float; V12: float; V13: float; V14: float; V15: float
    V16: float; V17: float; V18: float; V19: float; V20: float
    V21: float; V22: float; V23: float; V24: float; V25: float
    V26: float; V27: float; V28: float

@app.on_event("startup")
def load_models():
    global scaler, iso_forest, xgb_model, explainer, gnn_model
    try:
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Models'))
        
        print("Loading ML components (XGBoost, Isolation Forest)...")
        scaler = joblib.load(os.path.join(base_dir, "robust_scaler.joblib"))
        iso_forest = joblib.load(os.path.join(base_dir, "isolation_forest_model.joblib"))
        
        xgb_model = xgb.XGBClassifier()
        xgb_model.load_model(os.path.join(base_dir, "xgboost_fraud_model.json"))
        
        print("Loading GNN Model...")
        gnn_model = FraudGNN(num_features=30)
        gnn_model.load_state_dict(torch.load(os.path.join(base_dir, "gnn_fraud_model.pth")))
        gnn_model.eval() # Set to evaluation mode
        
        print("Initializing SHAP Explainer...")
        explainer = shap.TreeExplainer(xgb_model)
        
        print("✅ FinGuard Engine Fully Operational with GNN!")
    except Exception as e:
        print(f"❌ Initialization Error: {e}")

def get_shap_explanation(df, df_scaled):
    shap_vals = explainer.shap_values(df_scaled)[0]
    features = df_scaled.columns
    impacts = sorted(zip(features, shap_vals), key=lambda x: abs(x[1]), reverse=True)
    
    explanation_text = "Top Anomaly Drivers:\n"
    for feat, impact in impacts[:5]:
        direction = "increased" if impact > 0 else "decreased"
        explanation_text += f"- {feat} {direction} risk score by {abs(impact):.2f}\n"
    return explanation_text

@app.post("/process_transaction")
def process_transaction(transaction: TransactionInput, db: Session = Depends(get_db)):
    try:
        data_dict = transaction.dict()
        trans_id = data_dict.pop("transaction_id")
        target_cust_id = "CUST-FRAUD-999" if "FRAUD" in trans_id.upper() else "CUST-NORMAL-001"
        
        df = pd.DataFrame([data_dict])
        df_scaled = df.copy()
        
        df_scaled['scaled_amount'] = scaler.transform(df_scaled['Amount'].values.reshape(-1, 1))
        df_scaled['scaled_time'] = scaler.transform(df_scaled['Time'].values.reshape(-1, 1))
        df_scaled.drop(['Time', 'Amount'], axis=1, inplace=True)
        
        cols = ['V1', 'V2', 'V3', 'V4', 'V5', 'V6', 'V7', 'V8', 'V9', 'V10',
                'V11', 'V12', 'V13', 'V14', 'V15', 'V16', 'V17', 'V18', 'V19', 'V20',
                'V21', 'V22', 'V23', 'V24', 'V25', 'V26', 'V27', 'V28', 
                'scaled_amount', 'scaled_time']
        df_scaled = df_scaled[cols]
        
        # --- 1. Traditional ML Inference ---
        xgb_prob = float(xgb_model.predict_proba(df_scaled)[0][1])
        iso_pred_raw = iso_forest.predict(df_scaled)[0]
        
        # --- 2. GNN Inference (Network Graph Risk) ---
        x_tensor = torch.tensor(df_scaled.values, dtype=torch.float)
        # Create a self-loop edge for real-time isolated inference
        edge_index = torch.tensor([[0], [0]], dtype=torch.long)
        gnn_data = Data(x=x_tensor, edge_index=edge_index)
        
        with torch.no_grad():
            gnn_out = gnn_model(gnn_data)
            # Get probability of class 1 (Fraud)
            gnn_prob = torch.exp(gnn_out)[0][1].item()
            
        # --- 3. Combined Risk Ensemble ---
        is_fraud = bool(xgb_prob > 0.5 or iso_pred_raw == -1 or gnn_prob > 0.6)
        risk_scores = {
            "xgboost": round(xgb_prob * 100, 2), 
            "gnn_network_risk": round(gnn_prob * 100, 2), # NEW GNN SCORE
            "isolation_forest_alert": bool(iso_pred_raw == -1)
        }
        
        if not is_fraud:
            new_tx = TransactionRecord(transaction_id=trans_id, customer_id=target_cust_id, amount=data_dict['Amount'], ml_risk_score=max(risk_scores['xgboost'], risk_scores['gnn_network_risk']), is_blocked=False, agent_action="FAST-PATH APPROVED")
            db.add(new_tx); db.commit()
            return {"transaction_id": trans_id, "status": "APPROVED", "message": "Transaction cleared.", "risk_scores": risk_scores}
            
        print(f"\n🚨 FRAUD DETECTED! Triggering Agentic Investigation for {trans_id}...")
        shap_explanation = get_shap_explanation(df, df_scaled)
        initial_state = {"transaction_id": trans_id, "transaction_data": data_dict, "risk_scores": risk_scores, "shap_explanation": shap_explanation}
        
        result_state = finguard_app.invoke(initial_state)
        final_action = result_state["recommended_action"]
        
        new_tx = TransactionRecord(transaction_id=trans_id, customer_id=target_cust_id, amount=data_dict['Amount'], ml_risk_score=max(risk_scores['xgboost'], risk_scores['gnn_network_risk']), is_blocked=True, agent_action=final_action)
        db.add(new_tx); db.commit()
        
        return {"transaction_id": trans_id, "status": "BLOCKED & INVESTIGATED", "ml_risk_scores": risk_scores, "agent_decision": final_action, "agent_case_report": result_state["final_report"]}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))