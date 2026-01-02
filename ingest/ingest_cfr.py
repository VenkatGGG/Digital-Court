import xml.etree.ElementTree as ET
import chromadb
import os

# --- CONFIGURATION ---
XML_FILE_PATH = "xml_t28a.xml"  # Your specific XML file
DB_PATH = "./judge_db"
COLLECTION_NAME = "judge_rulebook"

def parse_cfr_xml(filepath):
    print(f"📂 Parsing CFR XML: {filepath}...")
    
    try:
        tree = ET.parse(filepath)
        root = tree.getroot()
    except Exception as e:
        print(f"❌ XML Error: {e}")
        return []

    documents = []
    
    # State variables
    current_section = None
    current_text = []
    current_subject = ""

    # Iterate over all tags to catch the flow
    for elem in root.iter():
        
        # 1. New Section Number (e.g., "0.1")
        if elem.tag == 'SECTNO':
            # Save previous chunk
            if current_section and current_text:
                # Format: "Section 0.1: General Functions... [body]"
                full_doc = f"Section {current_section}: {current_subject}\n\n" + "\n".join(current_text)
                documents.append(full_doc)
            
            # Reset
            current_section = elem.text.strip() if elem.text else "Unknown"
            current_text = []
            current_subject = ""
            
        # 2. Section Title
        elif elem.tag == 'SUBJECT':
            current_subject = elem.text.strip() if elem.text else ""

        # 3. Paragraph Text
        elif elem.tag == 'P':
            text = "".join(elem.itertext()).strip()
            if text:
                current_text.append(text)

    # Save the last one
    if current_section and current_text:
        full_doc = f"Section {current_section}: {current_subject}\n\n" + "\n".join(current_text)
        documents.append(full_doc)

    print(f"✅ Extracted {len(documents)} distinct regulations.")
    return documents

def save_to_chroma(documents):
    if not documents:
        print("⚠️ No documents to save.")
        return

    print(f"💾 Saving to ChromaDB at {DB_PATH}...")
    client = chromadb.PersistentClient(path=DB_PATH)
    
    # 'get_or_create' ensures we don't delete your PDF data if you already ran that
    collection = client.get_or_create_collection(name=COLLECTION_NAME)
    
    # Create distinct IDs
    count = collection.count()
    ids = [f"cfr_{count + i}" for i in range(len(documents))]
    metadatas = [{"source": "28 CFR (DOJ Regulations)", "type": "regulation"} for _ in documents]
    
    # Batch insert
    batch_size = 100
    for i in range(0, len(documents), batch_size):
        end = min(i + batch_size, len(documents))
        print(f"   Writing batch {i} to {end}...")
        collection.add(
            documents=documents[i:end],
            ids=ids[i:end],
            metadatas=metadatas[i:end]
        )
    
    print("🚀 CFR Ingestion Complete!")

if __name__ == "__main__":
    if not os.path.exists(XML_FILE_PATH):
        print(f"❌ Error: File '{XML_FILE_PATH}' not found.")
    else:
        docs = parse_cfr_xml(XML_FILE_PATH)
        save_to_chroma(docs)