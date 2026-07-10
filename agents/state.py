from typing import TypedDict, Dict, Any

class CaseState(TypedDict):
    transaction_id: str
    transaction_data: Dict[str, Any]
    risk_scores: Dict[str, Any]
    shap_explanation: str
    detector_summary: str      # Added from Detector
    customer_profile: str      # Added from Investigator Tools
    sanctions_check: str       # Added from Investigator Tools
    investigation_notes: str   # Added from Investigator
    relevant_policies: str     # Added from Report Writer (RAG)
    final_report: str          # Added from Report Writer
    recommended_action: str    # Added from Escalation Agent