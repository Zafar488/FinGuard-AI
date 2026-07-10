import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

# 1. Define paths
current_dir = os.path.dirname(os.path.abspath(__file__))
pdf_path = os.path.join(current_dir, "FINANCIAL_CRIME_FRAUD_INVESTIGATION_POLICY_2026.pdf")
vector_store_path = os.path.join(current_dir, "vector_store")

print(f"📄 Loading Policy Document from: {pdf_path}...")

try:
    # 2. Load the PDF
    # Agar aapki file ka naam exactly yeh nahi hai toh upar pdf_path mein theek kar lein
    loader = PyPDFLoader(pdf_path)
    documents = loader.load()
    print(f"✅ Successfully loaded {len(documents)} pages.")

    # 3. Chunk the Text
    # LLMs ek sath poori kitaab nahi parh sakte, isliye hum isko chotay hisson (chunks) mein todte hain
    print("✂️ Splitting document into searchable chunks...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )
    chunks = text_splitter.split_documents(documents)
    print(f"✅ Created {len(chunks)} text chunks.")

    # 4. Generate Embeddings (Text to Numbers)
    print("🧠 Generating Embeddings (This will download a small model the first time)...")
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    # 5. Store in FAISS Vector Database
    print("🗄️ Building FAISS Vector Database...")
    vector_db = FAISS.from_documents(chunks, embeddings)

    # 6. Save the Database Locally
    vector_db.save_local(vector_store_path)
    print(f"\n🎉 SUCCESS! FAISS Vector Database saved to: {vector_store_path}")
    print("Your LangGraph Agent can now read the company mind!")

except Exception as e:
    print(f"\n❌ Error: {e}")
    print("Please make sure your PDF file name matches exactly and is in the 'rag' folder.")