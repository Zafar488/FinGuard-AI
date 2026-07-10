import os
from dotenv import load_dotenv
# Load environment variables FIRST
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from agents.state import CaseState

llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.1)

def detector_agent(state: CaseState):
    print(f"🚨 [Node 1] Detector Agent parsing ML outputs for {state['transaction_id']}...")
    
    prompt = f"""
    You are the First-Line Fraud Detector Agent.
    Risk Score: {state['risk_scores']}
    Anomalies: {state['shap_explanation']}
    
    Translate these raw machine learning metrics into a 2-sentence initial threat summary for the investigation team.
    """
    response = llm.invoke([SystemMessage(content="You are an AI Threat Detector."), HumanMessage(content=prompt)])
    
    return {"detector_summary": response.content}