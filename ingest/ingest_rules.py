import chromadb
import re
from pypdf import PdfReader
import os

# --- CONFIGURATION ---
PDF_PATH = "fcr.pdf"  # Your specific filename
DB_PATH = "./judge_db"
COLLECTION_NAME = "judge_rulebook"

def extract_text_from_pdf(pdf_path):
    print(f"📖 Reading {pdf_path}...")
    try:
        reader = PdfReader(pdf_path)
        full_text = ""
        # Loop through all pages to extract text
        for page in reader.pages:
            text = page.extract_text()
            if text:
                full_text += text + "\n"
        return full_text
    except Exception as e:
        print(f"❌ Error reading PDF: {e}")
        return None

def chunk_rules(text):
    print("✂️  Splitting text into Civil Procedure Rules...")
    
    # REGEX STRATEGY:
    # We look for "Rule" followed by a number and a period.
    # Example: "Rule 12." or "Rule 56."
    pattern = r"(Rule\s+\d+\.)"
    
    # Split text. The capture group () keeps the "Rule 12." delimiter in the list.
    chunks = re.split(pattern, text)
    
    clean_docs = []
    current_header = ""
    
    # The split results in: [text_before, "Rule 1.", " body text...", "Rule 2.", " body..."]
    for segment in chunks:
        segment = segment.strip()
        if not segment: continue
        
        # If this segment is the Header (e.g. "Rule 12.")
        if re.match(pattern, segment):
            current_header = segment
        else:
            # This is the body. Combine with the header we just found.
            if current_header:
                full_rule = f"{current_header} {segment}"
                
                # Cleanup: Remove strict header/footer noise if possible (basic length check)
                if len(full_rule) > 50: 
                    clean_docs.append(full_rule)
                
                current_header = "" # Reset
    
    print(f"✅ Extracted {len(clean_docs)} Federal Rules.")
    return clean_docs

def save_to_chroma(documents):
    if not documents:
        print("⚠️ No documents to save.")
        return

    print(f"💾 Saving to ChromaDB at {DB_PATH}...")
    client = chromadb.PersistentClient(path=DB_PATH)
    
    # USE get_or_create to APPEND to the data you ingested from the XML
    collection = client.get_or_create_collection(name=COLLECTION_NAME)
    
    # Create unique IDs with 'frcp_' prefix to avoid clashing with the 'cfr_' IDs
    ids = [f"frcp_{i}" for i in range(len(documents))]
    
    metadatas = [{"source": "Federal Rules of Civil Procedure", "type": "rule"} for _ in documents]
    
    # Batch insert (safety for large lists)
    batch_size = 100
    for i in range(0, len(documents), batch_size):
        end = min(i + batch_size, len(documents))
        print(f"   Writing batch {i} to {end}...")
        collection.add(
            documents=documents[i:end],
            ids=ids[i:end],
            metadatas=metadatas[i:end]
        )
    
    print("🚀 Ingestion Complete! Your Judge is now an expert.")

if __name__ == "__main__":
    if not os.path.exists(PDF_PATH):
        print(f"❌ Error: File '{PDF_PATH}' not found. Please ensure it is in this folder.")
    else:
        raw_text = extract_text_from_pdf(PDF_PATH)
        if raw_text:
            rules = chunk_rules(raw_text)
            save_to_chroma(rules)