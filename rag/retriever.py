"""DeltaRAG + Graph-RAG Retriever — retrieve change-grounded context for agents."""
from rag.embedder import query_similar
from rag.entity_extractor import extract_entities
from rag.knowledge_graph import KnowledgeGraph
from utils.db import get_session, Change, Source, Recommendation

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
    # Check if the user is explicitly asking about a specific change ID (only for Chat UI)
    import re
    explicit_filters = None
    match = None
    if source_id is None:
        match = re.search(r'change_(\d+)', change_text, re.IGNORECASE)
        if match:
            explicit_filters = {"change_id": int(match.group(1))}

    # Step 1: Vector similarity search (exclude same-source)
    all_chunks = query_similar(change_text, top_k=top_k * 2, filters=explicit_filters)
    vector_chunks = [c for c in all_chunks if c["metadata"].get("source_id") != source_id]

    # Step 2: Extract entities from change text
    entities = extract_entities(change_text)
    entity_ids = [e.value for e in entities.entities]

    # Explicitly add the change_X node to the entity traversal list so the graph connects it
    if match:
        entity_ids.append(f"change_{match.group(1)}")

    # Step 3: Knowledge graph traversal with relevance ranking
    graph_chunks = []
    if entity_ids:
        kg = KnowledgeGraph.load_or_create()

        # Look up query source category for cross-category ranking
        query_category = ""
        if source_id:
            session = get_session()
            query_src = session.query(Source).filter_by(id=source_id).first()
            query_category = query_src.category if query_src else ""
            session.close()

        ranked_changes = kg.get_ranked_change_ids(
            entity_ids, max_hops=2, query_source_category=query_category
        )

        # Step 4: Get chunks for graph-discovered change events
        for cid, _graph_score in ranked_changes:
            try:
                change_chunks = query_similar(
                    change_text, top_k=3,
                    filters={"change_id": cid}
                )
                for c in change_chunks:
                    if c["metadata"].get("source_id") != source_id:
                        graph_chunks.append(c)
            except Exception:
                pass

    # ── Step 5: Reciprocal Rank Fusion (RRF) ──────────────────────
    # RRF combines two independent rankings without letting either
    # one evict the other's results. A chunk ranked highly by RAG
    # stays competitive even if the graph disagrees.
    #
    # score(chunk) = 1/(rrf_k + rank_in_rag) + 1/(rrf_k + rank_in_graph)
    #
    # rrf_k=60 is the standard constant from the original RRF paper.
    RRF_K = 60

    # Build rank maps (chunk_id → 1-indexed rank)
    rag_rank = {}
    for rank, chunk in enumerate(vector_chunks, 1):
        if chunk["id"] not in rag_rank:
            rag_rank[chunk["id"]] = rank

    graph_rank = {}
    for rank, chunk in enumerate(graph_chunks, 1):
        if chunk["id"] not in graph_rank:
            graph_rank[chunk["id"]] = rank

    # Collect all unique chunks
    all_chunks_map = {}
    for c in vector_chunks:
        all_chunks_map[c["id"]] = c
    for c in graph_chunks:
        if c["id"] not in all_chunks_map:
            all_chunks_map[c["id"]] = c

    # Compute RRF scores
    rrf_scored = []
    for chunk_id, chunk in all_chunks_map.items():
        score = 0.0
        if chunk_id in rag_rank:
            score += 1.0 / (RRF_K + rag_rank[chunk_id])
        if chunk_id in graph_rank:
            score += 1.0 / (RRF_K + graph_rank[chunk_id])
        rrf_scored.append((score, chunk))

    # Sort by RRF score descending (higher = more relevant)
    rrf_scored.sort(key=lambda x: -x[0])

    # Deduplicate and limit
    seen_ids = set()
    merged = []
    for _score, chunk in rrf_scored:
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
        discovery = "graph" if chunk["id"] in graph_rank else "vector"

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
        "graph_change_ids": list({c["metadata"].get("change_id") for c in graph_chunks if c["metadata"].get("change_id")}),
        "discovery_method": "graph_rag",
    }


# Keep backward compatibility
def retrieve_cross_source(change_text: str, source_id: int, top_k: int = 5) -> dict:
    """Backward-compatible alias for retrieve_graph_rag."""
    return retrieve_graph_rag(change_text, source_id, top_k)


def retrieve_recent_tickets(top_k: int = 10) -> str:
    """Retrieve the most recent/critical action tickets from the DB."""
    session = get_session()
    try:
        recs = session.query(Recommendation).order_by(Recommendation.risk_score.desc()).limit(top_k).all()
        if not recs:
            return "No recent action tickets found."
        
        blocks = []
        for r in recs:
            blocks.append(f"Ticket: [{r.priority.upper()}] {r.title} (Risk: {r.risk_score})\nSummary: {r.summary}")
        return "\n\n".join(blocks)
    finally:
        session.close()


def retrieve_pipeline_stats() -> str:
    """Retrieve operational pipeline stats for DB."""
    session = get_session()
    try:
        active_sources = session.query(Source).filter_by(active=True).count()
        total_changes = session.query(Change).count()
        pending_changes = session.query(Change).filter_by(status="pending").count()
        escalated_changes = session.query(Change).filter_by(status="escalated").count()
        
        return (
            f"Active Sources Monitored: {active_sources}\n"
            f"Total Changes Detected: {total_changes}\n"
            f"Pending Changes: {pending_changes} | Escalated Changes: {escalated_changes}"
        )
    finally:
        session.close()
