"""
core/rag.py - Retrieval-Augmented Generation Tools

ChromaDB integration for querying the legal knowledge base.
"""

import os
from typing import Optional
import chromadb

from config.settings import get_settings


class RAGError(Exception):
    """Custom exception for RAG-related errors."""
    pass


def get_legal_db():
    """
    Get a connection to the ChromaDB legal database.
    
    Returns:
        The 'judge_rulebook' collection
    
    Raises:
        RAGError: If the database doesn't exist
    """
    settings = get_settings()
    db_path = settings.chroma_db_path
    collection_name = settings.collection_name
    
    if not os.path.exists(db_path):
        raise RAGError(
            f"Legal database not found at '{db_path}'. "
            "Run ingest scripts first."
        )
    
    client = chromadb.PersistentClient(path=db_path)
    
    try:
        return client.get_collection(name=collection_name)
    except Exception as e:
        raise RAGError(f"Collection '{collection_name}' not found: {e}")


def query_legal_db(
    query: str,
    n_results: int = 5,
    source_filter: Optional[str] = None
) -> list[dict]:
    """
    Query the legal knowledge base for relevant rules.
    
    Args:
        query: Natural language query
        n_results: Maximum number of results
        source_filter: Optional filter by source
    
    Returns:
        List of dicts with 'content', 'source', 'relevance_score'
    """
    collection = get_legal_db()
    
    where_clause = None
    if source_filter:
        where_clause = {"source": {"$contains": source_filter}}
    
    results = collection.query(
        query_texts=[query],
        n_results=n_results,
        where=where_clause,
        include=["documents", "metadatas", "distances"]
    )
    
    formatted = []
    if results and results.get("documents"):
        documents = results["documents"][0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]
        
        for i, doc in enumerate(documents):
            metadata = metadatas[i] if i < len(metadatas) else {}
            distance = distances[i] if i < len(distances) else 0.0
            
            # Convert distance to similarity (lower = better)
            relevance = max(0, 1 - (distance / 2))
            
            formatted.append({
                "content": doc,
                "source": metadata.get("source", "Unknown"),
                "type": metadata.get("type", "rule"),
                "relevance_score": round(relevance, 3)
            })
    
    return formatted


def format_rules_for_context(rules: list[dict], max_rules: int = 3) -> str:
    """
    Format retrieved rules for inclusion in a prompt.
    
    Args:
        rules: List of rule dicts from query_legal_db
        max_rules: Maximum rules to include
    
    Returns:
        Formatted string for prompt context
    """
    if not rules:
        return "[No relevant rules found]"
    
    lines = ["RELEVANT LEGAL RULES:", "-" * 40]
    
    for i, rule in enumerate(rules[:max_rules], 1):
        lines.append(f"\n[{i}] Source: {rule['source']}")
        lines.append(f"    Relevance: {rule['relevance_score']:.0%}")
        content = rule['content']
        if len(content) > 500:
            content = content[:500] + "..."
        lines.append(f"    {content}")
    
    return "\n".join(lines)
