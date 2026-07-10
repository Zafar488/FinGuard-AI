from agents.state import CaseState

def escalation_agent(state: CaseState):
    print("⚖️ [Node 4] Escalation Agent determining final action...")
    
    risk_score = state['risk_scores'].get('xgboost', 0)
    sanctions = state.get('sanctions_check', '')
    
    if "WARNING" in sanctions or risk_score >= 95:
        action = "IMMEDIATELY FREEZE ACCOUNT & NOTIFY ANALYST"
    elif risk_score >= 60:
        action = "TEMPORARILY BLOCK & REQUIRE OTP VERIFICATION"
    else:
        action = "AUTO-DISMISS (FALSE POSITIVE)"
        
    return {"recommended_action": action}