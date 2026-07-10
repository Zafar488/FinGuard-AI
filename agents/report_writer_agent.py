import os
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from agents.state import CaseState

llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.1)

# Load RAG DB
current_dir = os.path.dirname(os.path.abspath(__file__))
vector_store_path = os.path.join(current_dir, '..', 'rag', 'vector_store')
try:
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vector_store = FAISS.load_local(vector_store_path, embeddings, allow_dangerous_deserialization=True)
except Exception:
    vector_store = None

def report_writer_agent(state: CaseState):
    print("📝 [Node 3] Report Writer Agent querying policy & drafting case file...")
    
    # 1. Retrieve Policy
    policies = "No internal policies found."
    if vector_store:
        query = f"Transaction amount {state['transaction_data'].get('Amount', 0)} with features {state.get('shap_explanation', '')}"
        docs = vector_store.similarity_search(query, k=2)
        policies = "\n".join([d.page_content for d in docs])

    # 2. Write Report
    prompt = f"""
    Write a final fraud case report based on:
    Investigation Notes: {state.get('investigation_notes', '')}
    Internal Policy: {policies}
    
    Format:
    - EVIDENCE SUMMARY: [Bullet points]
    - DB VERIFICATION: [Customer history & Sanctions check]
    - POLICY CITATION: [Applicable rule]
    """
    response = llm.invoke([SystemMessage(content="You write factual, auditable compliance reports."), HumanMessage(content=prompt)])
    
    return {"relevant_policies": policies, "final_report": response.content}