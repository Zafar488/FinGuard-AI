from langgraph.graph import StateGraph, START, END

# Import the shared state
from agents.state import CaseState

# Import the individual agents
from agents.detector_agent import detector_agent
from agents.investigator_agent import investigator_agent
from agents.report_writer_agent import report_writer_agent
from agents.escalation_agent import escalation_agent

print("🧩 Initializing FinGuard Modular Multi-Agent Workflow...")

# Build the Graph
workflow = StateGraph(CaseState)

# Add all imported nodes
workflow.add_node("Detector", detector_agent)
workflow.add_node("Investigator", investigator_agent)
workflow.add_node("Report_Writer", report_writer_agent)
workflow.add_node("Escalation", escalation_agent)

# Define the precise flow
workflow.add_edge(START, "Detector")
workflow.add_edge("Detector", "Investigator")
workflow.add_edge("Investigator", "Report_Writer")
workflow.add_edge("Report_Writer", "Escalation")
workflow.add_edge("Escalation", END)

# Compile into our API-ready app
finguard_app = workflow.compile()

print("✅ Enterprise Modular Graph Compiled Successfully!")