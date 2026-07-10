import os
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from agents.state import CaseState

# 🗄️ Import Database Tools
from database.database import SessionLocal
from database.models import Customer

llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.1)

# --- REAL MCP Tool (Database Query) ---
def get_customer_history(txn_id: str) -> str:
    """Queries the SQL Database for customer profile"""
    db = SessionLocal()
    try:
        # For our demo, we link "FRAUD" in txn_id to our Suspicious Customer, and "NORMAL" to our VIP Customer.
        target_cust_id = "CUST-FRAUD-999" if "FRAUD" in txn_id.upper() else "CUST-NORMAL-001"
        
        # Real SQL Query using ORM
        customer = db.query(Customer).filter(Customer.customer_id == target_cust_id).first()
        
        if customer:
            return (f"Name: {customer.name} | Status: {customer.account_status} | "
                    f"Country: {customer.country_of_origin} | Avg Monthly Spend: ${customer.avg_monthly_spend}")
        else:
            return "No customer record found in database."
    finally:
        db.close() # Always close the connection

# --- Mock Sanctions API ---
def check_ofac_sanctions(txn_id: str) -> str:
    if "FRAUD" in txn_id.upper():
        return "WARNING: Partial Name Match on Watchlist (Crypto laundering suspected)."
    return "CLEAR: No sanctions found."

def investigator_agent(state: CaseState):
    print("🕵️‍♂️ [Node 2] Investigator Agent querying SQL Database...")
    
    cust_profile = get_customer_history(state['transaction_id'])
    sanctions = check_ofac_sanctions(state['transaction_id'])
    
    prompt = f"""
    Review the threat brief and external DBs:
    Threat: {state.get('detector_summary', '')}
    Customer SQL DB Record: {cust_profile}
    Sanctions API: {sanctions}
    
    Synthesize this data. Does the current transaction amount (${state['transaction_data'].get('Amount', 0)}) deviate significantly from their average monthly spend found in the DB?
    """
    response = llm.invoke([SystemMessage(content="You are an expert fraud analyst."), HumanMessage(content=prompt)])
    
    return {
        "customer_profile": cust_profile,
        "sanctions_check": sanctions,
        "investigation_notes": response.content
    }