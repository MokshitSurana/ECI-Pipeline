"""DeltaRAG + Graph-RAG Retriever — retrieve change-grounded context for agents."""
from rag.embedder import query_similar
from rag.entity_extractor import extract_entities
from rag.knowledge_graph import KnowledgeGraph
from utils.db import get_session, Change, Source


def retrieve_context(query: str, top_k: int = 5, source_filter: int = None,
                     category_filter: str = None) -> dict:
    """Retrieve relevant context chunks and format for agent consumption.

    Args:
        query: Natural language query or change description
        top_k: Number of chunks to retrieve
        source_filter: Optional source_id to restrict retrieval
        category_filter: Optional source_category to restrict retrieval

    Returns:
        {
            "chunks": [list of retrieved chunks],
            "formatted_context": "numbered evidence string for LLM",
            "chunk_ids": [list of chunk IDs for citation]
        }
    """
    filters = None
    if source_filter and category_filter:
        filters = {"$and": [
            {"source_id": source_filter},
            {"source_category": category_filter},
        ]}
    elif source_filter:
        filters = {"source_id": source_filter}
    elif category_filter:
        filters = {"source_category": category_filter}

    chunks = query_similar(query, top_k=top_k, filters=filters)

    # Format as numbered evidence blocks for the agent
    evidence_blocks = []
    chunk_ids = []
    for idx, chunk in enumerate(chunks, 1):
        evidence_blocks.append(
            f"[Evidence {idx}] (source_id={chunk['metadata'].get('source_id', '?')}, "
            f"category={chunk['metadata'].get('source_category', '?')}, "
            f"change_id={chunk['metadata'].get('change_id', '?')}, "
            f"kind={chunk['metadata'].get('kind', '?')}, "
            f"distance={chunk['distance']:.4f})\n"
            f"{chunk['text'][:800]}"
        )
        chunk_ids.append(chunk["id"])

    formatted = "\n\n".join(evidence_blocks) if evidence_blocks else "No relevant evidence found."

    return {
        "chunks": chunks,
        "formatted_context": formatted,
        "chunk_ids": chunk_ids,
    }


def retrieve_graph_rag(change_text: str, source_id: int, top_k: int = 5) -> dict:
    """Graph-RAG retrieval: combine vector similarity with knowledge graph traversal.

    This replaces the old retrieve_cross_source() with true Graph-RAG:
    1. Standard DeltaRAG vector search for semantically similar chunks
    2. Extract entities from the change text
    3. Traverse knowledge graph 2 hops from extracted entities
    4. Retrieve chunks associated with connected change events
    5. Merge and deduplicate results

    Args:
        change_text: The change content to find cross-source connections for
        source_id: Source ID of the current change (to identify cross-source)
        top_k: Number of results to return

    Returns:
        Same format as retrieve_context() plus graph metadata.
    """
    # Step 1: Vector similarity search (exclude same-source)
    all_chunks = query_similar(change_text, top_k=top_k * 2)
    vector_chunks = [c for c in all_chunks if c["metadata"].get("source_id") != source_id]

    # Step 2: Extract entities from change text
    entities = extract_entities(change_text)
    entity_ids = [e.value for e in entities.entities]

    # Step 3: Knowledge graph traversal
    graph_chunk_ids = set()
    graph_change_ids = []
    if entity_ids:
        kg = KnowledgeGraph.load_or_create()
        graph_change_ids = kg.get_related_change_ids(entity_ids, max_hops=2)

        # Step 4: Get chunks for graph-discovered change events
        for cid in graph_change_ids:
            # Find chunks belonging to this change from vector store
            try:
                change_chunks = query_similar(
                    change_text, top_k=3,
                    filters={"change_id": cid}
                )
                for c in change_chunks:
                    if c["metadata"].get("source_id") != source_id:
                        graph_chunk_ids.add(c["id"])
                        # Add to results if not already present
                        if not any(vc["id"] == c["id"] for vc in vector_chunks):
                            vector_chunks.append(c)
            except Exception:
                pass

    # Step 5: Deduplicate and limit
    seen_ids = set()
    merged = []
    for chunk in vector_chunks:
        if chunk["id"] not in seen_ids:
            seen_ids.add(chunk["id"])
            merged.append(chunk)
    merged = merged[:top_k]

    # Format evidence blocks
    evidence_blocks = []
    chunk_ids = []
    for idx, chunk in enumerate(merged, 1):
        # Look up source name
        session = get_session()
        src = session.query(Source).filter_by(id=chunk["metadata"].get("source_id")).first()
        source_name = src.name if src else "Unknown"
        session.close()

        # Mark graph-discovered evidence
        discovery = "graph" if chunk["id"] in graph_chunk_ids else "vector"

        evidence_blocks.append(
            f"[Cross-Source Evidence {idx}] (source={source_name}, "
            f"category={chunk['metadata'].get('source_category', '?')}, "
            f"change_id={chunk['metadata'].get('change_id', '?')}, "
            f"discovery={discovery}, "
            f"distance={chunk['distance']:.4f})\n"
            f"{chunk['text'][:800]}"
        )
        chunk_ids.append(chunk["id"])

    formatted = "\n\n".join(evidence_blocks) if evidence_blocks else "No cross-source connections found."

    return {
        "chunks": merged,
        "formatted_context": formatted,
        "chunk_ids": chunk_ids,
        "entities_extracted": len(entity_ids),
        "graph_change_ids": graph_change_ids,
        "discovery_method": "graph_rag",
    }


# Keep backward compatibility
def retrieve_cross_source(change_text: str, source_id: int, top_k: int = 5) -> dict:
    """Backward-compatible alias for retrieve_graph_rag."""
    return retrieve_graph_rag(change_text, source_id, top_k)
