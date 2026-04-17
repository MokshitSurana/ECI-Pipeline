"""Ablation Study: Evaluate Vanilla RAG vs Graph-Only vs DeltaRAG.

Runs 50 golden queries across 5 query types and 10 sources.
Computes per-query IR metrics, aggregates by query type with mean/std,
and reports paired significance tests with bootstrap confidence intervals.

Statistical methodology:
    - Confirmatory family (Holm-Bonferroni corrected): 6 overall tests
      (3 metrics x 2 comparisons: RAG-vs-DeltaRAG, Graph-vs-DeltaRAG).
    - Exploratory: per-type tests reported with raw p-values and 95% CIs.
    - Bootstrap: 10,000 resamples on paired deltas, percentile CIs, seeded.
"""
import argparse
import math
import random
from typing import List, Tuple, Dict
from collections import defaultdict

from scipy.stats import wilcoxon

from utils.db import get_session, Source, Change
from rag.embedder import query_similar
from rag.entity_extractor import extract_entities
from rag.knowledge_graph import KnowledgeGraph
from rag.retriever import retrieve_graph_rag

from evaluation.golden_queries import GOLDEN_QUERIES, QUERY_TYPE_LABELS

# ── Constants ────────────────────────────────────────────────────

BOOTSTRAP_N = 10_000
BOOTSTRAP_SEED = 42
ALPHA = 0.05
EXPECTED_SOURCE_COUNT = 10
EXPECTED_PENDING_CHANGES = 10

# ── Dedup + Metrics ──────────────────────────────────────────────

def dedup_preserve_order(ids: List[int]) -> List[int]:
    """Remove duplicate source_ids while preserving first-occurrence order."""
    seen = set()
    result = []
    for sid in ids:
        if sid not in seen:
            seen.add(sid)
            result.append(sid)
    return result


def prepare_top_k(retrieved_source_ids: List[int], k: int) -> List[int]:
    """Canonical retrieval list: deduplicate preserving order, then slice to k.

    Every metric consumes the output of this function. This is the fix for the
    original bug where Recall deduped-after-slice while Precision/NDCG
    deduped-before-slice, producing inconsistent answers for the same retrieval.
    """
    return dedup_preserve_order(retrieved_source_ids)[:k]


def compute_recall(top_k_sids: List[int], expected: set, k: int) -> float:
    """Recall = |expected ∩ top_k| / |expected|. Empty expected → 1.0."""
    if not expected:
        return 1.0
    found = sum(1 for sid in top_k_sids if sid in expected)
    return found / float(len(expected))


def compute_precision(top_k_sids: List[int], expected: set, k: int) -> float:
    """Precision = |expected ∩ top_k| / k.

    Denominator is static k, not len(top_k_sids). If the retriever returned
    duplicates that shrank top_k below k, that is penalized as noise — which
    is the intended behavior for cross-source correlation.
    """
    if k <= 0:
        return 0.0
    found = sum(1 for sid in top_k_sids if sid in expected)
    return found / float(k)


def compute_ndcg(top_k_sids: List[int], expected: set, k: int) -> float:
    """NDCG for binary relevance. IDCG uses min(k, |expected|)."""
    dcg = sum(
        1.0 / math.log2(idx + 2)
        for idx, sid in enumerate(top_k_sids)
        if sid in expected
    )
    ideal_count = min(k, len(expected))
    idcg = sum(1.0 / math.log2(idx + 2) for idx in range(ideal_count))
    if idcg == 0:
        return 1.0 if dcg == 0 else 0.0
    return dcg / idcg

# ── Retrieval Algorithms ─────────────────────────────────────────

def run_vanilla_rag(query_text: str, source_id: int, top_k: int) -> List[int]:
    """Pure Vector Similarity. Loops with increasing fetch size until we
    have top_k distinct cross-source results or exhaust the store."""
    multiplier = 5
    max_multiplier = 40
    while multiplier <= max_multiplier:
        all_chunks = query_similar(query_text, top_k=top_k * multiplier)
        filtered_sids = [
            c["metadata"].get("source_id")
            for c in all_chunks
            if c["metadata"].get("source_id") != source_id
        ]
        distinct = dedup_preserve_order(filtered_sids)
        if len(distinct) >= top_k or len(all_chunks) < top_k * multiplier:
            # Got enough OR the store returned fewer than requested (exhausted).
            return filtered_sids
        multiplier *= 2
    return filtered_sids


def run_graph_only(query_text: str, source_id: int, top_k: int, kg: KnowledgeGraph,
                   source_category: str) -> List[int]:
    """Pure Knowledge Graph Traversal — NO vector search.

    Takes pre-loaded graph and pre-fetched source category to avoid per-query I/O.
    """
    entities = extract_entities(query_text)
    entity_ids = [e.value for e in entities.entities]
    if not entity_ids:
        return []
    ranked_changes = kg.get_ranked_change_ids(
        entity_ids, max_hops=2, query_source_category=source_category
    )
    gathered = []
    for cid, _score in ranked_changes:
        node_data = kg.graph.nodes.get(f"change_{cid}", {})
        sid = node_data.get("source_id")
        if sid and sid != source_id:
            gathered.append(sid)
            if len(dedup_preserve_order(gathered)) >= top_k:
                return gathered
    return gathered


def run_deltarag(query_text: str, source_id: int, top_k: int) -> List[int]:
    """The full Graph-RAG pipeline (RRF fusion of RAG + Graph)."""
    res = retrieve_graph_rag(query_text, source_id, top_k=top_k)
    return [c["metadata"].get("source_id") for c in res["chunks"]]

# ── Statistics ───────────────────────────────────────────────────

def paired_bootstrap_ci(
    a: List[float], b: List[float], n_boot: int = BOOTSTRAP_N,
    seed: int = BOOTSTRAP_SEED
) -> Tuple[float, float, float]:
    """Percentile bootstrap 95% CI on mean(a - b). Returns (mean_delta, lo, hi)."""
    if len(a) != len(b) or not a:
        return (0.0, 0.0, 0.0)
    deltas = [ai - bi for ai, bi in zip(a, b)]
    n = len(deltas)
    rng = random.Random(seed)
    means = []
    for _ in range(n_boot):
        sample = [deltas[rng.randrange(n)] for _ in range(n)]
        means.append(sum(sample) / n)
    means.sort()
    lo = means[int(0.025 * n_boot)]
    hi = means[int(0.975 * n_boot) - 1]
    return (sum(deltas) / n, lo, hi)


def safe_wilcoxon(a: List[float], b: List[float]) -> float:
    """Paired Wilcoxon signed-rank p-value. Returns 1.0 on degenerate input."""
    if len(a) != len(b) or len(a) < 2:
        return 1.0
    deltas = [ai - bi for ai, bi in zip(a, b)]
    if all(d == 0 for d in deltas):
        return 1.0
    try:
        _stat, p = wilcoxon(a, b, zero_method="wilcox")
        return float(p)
    except ValueError:
        return 1.0


def holm_bonferroni(pvals: List[float], alpha: float = ALPHA) -> List[bool]:
    """Holm-Bonferroni step-down. Returns rejected[i] for each pvals[i]."""
    m = len(pvals)
    indexed = sorted(enumerate(pvals), key=lambda x: x[1])
    rejected = [False] * m
    for rank, (orig_idx, p) in enumerate(indexed):
        threshold = alpha / (m - rank)
        if p <= threshold:
            rejected[orig_idx] = True
        else:
            break
    return rejected

# ── DB Safety Check ──────────────────────────────────────────────

def assert_expected_db_state():
    """Verify DB contains exactly the expected seeded test state.

    Catches two failure modes:
      1. DB is empty (user forgot --seed)
      2. DB has unrelated data (e.g. production content, or stale reseed
         with different source names)
    """
    session = get_session()
    try:
        sources = session.query(Source).all()
        source_names = {s.name for s in sources}
        pending = session.query(Change).filter_by(status="pending").count()

        expected_names = {gq["source"] for gq in GOLDEN_QUERIES}
        missing = expected_names - source_names

        errors = []
        if len(sources) != EXPECTED_SOURCE_COUNT:
            errors.append(
                f"Expected {EXPECTED_SOURCE_COUNT} sources, found {len(sources)}."
            )
        if missing:
            errors.append(f"Missing expected source names: {sorted(missing)}")
        if pending != EXPECTED_PENDING_CHANGES:
            errors.append(
                f"Expected {EXPECTED_PENDING_CHANGES} pending changes, "
                f"found {pending}."
            )

        if errors:
            msg = "\n  - ".join(errors)
            raise SystemExit(
                f"\nDB state check FAILED:\n  - {msg}\n\n"
                f"Run with --seed to reset and populate the DB with test data.\n"
            )
    finally:
        session.close()

# ── The Evaluation Runner ────────────────────────────────────────

def run_ablation_study(k: int = 5, do_seed: bool = False,
                       output_path: str = "evaluation_matrix.md"):
    if do_seed:
        print("Seeding deterministic test data...")
        from evaluation.test_data import seed_test_data
        seed_test_data()
    else:
        print("Verifying DB state (use --seed to reseed)...")
        assert_expected_db_state()
        print("DB state OK.")

    session = get_session()

    sources = session.query(Source).all()
    name_to_id = {s.name: s.id for s in sources}
    id_to_category = {s.id: s.category for s in sources}

    changes_by_source = {}
    for change in session.query(Change).filter_by(status="pending").all():
        changes_by_source[change.source_id] = change

    # Load the graph ONCE. All 50 Graph-Only queries share this instance.
    print("Loading knowledge graph...")
    kg = KnowledgeGraph.load_or_create()

    all_results = []
    skipped = 0

    print(f"\nRunning {len(GOLDEN_QUERIES)} queries (k={k})...\n")

    for gq in GOLDEN_QUERIES:
        source_name = gq["source"]
        source_id = name_to_id.get(source_name)
        if not source_id:
            print(f"  SKIP {gq['id']}: source '{source_name}' not found")
            skipped += 1
            continue

        # Resolve query text (Type A uses the actual diff_text)
        if gq["query"] is None:
            change = changes_by_source.get(source_id)
            if not change or not change.diff_text:
                print(f"  SKIP {gq['id']}: no diff for '{source_name}'")
                skipped += 1
                continue
            query_text = change.diff_text
        else:
            query_text = gq["query"]

        expected_ids = {
            name_to_id[name] for name in gq["expected"] if name in name_to_id
        }
        if not expected_ids:
            print(f"  SKIP {gq['id']}: no valid expected source IDs")
            skipped += 1
            continue

        # Run all three algorithms
        rag_raw = run_vanilla_rag(query_text, source_id, k)
        graph_raw = run_graph_only(
            query_text, source_id, k, kg,
            id_to_category.get(source_id, "")
        )
        delta_raw = run_deltarag(query_text, source_id, k)

        # Canonical top-K lists — all metrics consume these.
        rag_topk = prepare_top_k(rag_raw, k)
        graph_topk = prepare_top_k(graph_raw, k)
        delta_topk = prepare_top_k(delta_raw, k)

        result = {
            "id": gq["id"], "type": gq["type"],
            "source": source_name, "expected": expected_ids,
        }
        for algo_name, topk in [
            ("RAG", rag_topk), ("Graph", graph_topk), ("DeltaRAG", delta_topk)
        ]:
            result[algo_name] = {
                "Recall": compute_recall(topk, expected_ids, k),
                "Precision": compute_precision(topk, expected_ids, k),
                "NDCG": compute_ndcg(topk, expected_ids, k),
                "IDs": topk,
            }
        all_results.append(result)

        r, g, d = result["RAG"], result["Graph"], result["DeltaRAG"]
        print(
            f"  {gq['id']} ({gq['type']}) | "
            f"RAG R={r['Recall']:.2f} | "
            f"Graph R={g['Recall']:.2f} | "
            f"Delta R={d['Recall']:.2f}"
        )

    session.close()

    if skipped:
        print(f"\n({skipped} queries skipped)")

    # ── Aggregation ──────────────────────────────────────────────
    by_type = defaultdict(list)
    for r in all_results:
        by_type[r["type"]].append(r)

    def mean(values): return sum(values) / len(values) if values else 0.0

    def std(values):
        if len(values) < 2:
            return 0.0
        m = mean(values)
        return (sum((v - m) ** 2 for v in values) / len(values)) ** 0.5

    # ── Confirmatory tests: overall, Holm-corrected ──────────────
    print("\n" + "=" * 90)
    print("  CONFIRMATORY TESTS (overall, n={0}, Holm-Bonferroni corrected)".format(
        len(all_results)))
    print("=" * 90)

    confirmatory_pvals = []
    confirmatory_labels = []
    confirmatory_effects = []  # (mean_delta, lo, hi)

    for metric in ["Recall", "Precision", "NDCG"]:
        delta_vals = [r["DeltaRAG"][metric] for r in all_results]
        for baseline in ["RAG", "Graph"]:
            base_vals = [r[baseline][metric] for r in all_results]
            p = safe_wilcoxon(delta_vals, base_vals)
            effect = paired_bootstrap_ci(delta_vals, base_vals)
            confirmatory_pvals.append(p)
            confirmatory_labels.append(f"DeltaRAG vs {baseline} ({metric})")
            confirmatory_effects.append(effect)

    rejected = holm_bonferroni(confirmatory_pvals, alpha=ALPHA)

    for label, p, eff, rej in zip(
        confirmatory_labels, confirmatory_pvals, confirmatory_effects, rejected
    ):
        md, lo, hi = eff
        marker = " ***" if rej else ""
        print(f"  {label:40s} Δ={md:+.4f} [{lo:+.4f}, {hi:+.4f}] "
              f"p={p:.4f}{marker}")

    # ── Markdown Output ──────────────────────────────────────────
    md_lines = [
        "# DeltaRAG Retrieval Ablation Study",
        "",
        f"**{len(all_results)} queries** across {len(by_type)} query types | "
        f"k={k} | bootstrap n={BOOTSTRAP_N}, seed={BOOTSTRAP_SEED}",
        "",
        "## Confirmatory Tests (Holm-Bonferroni corrected, α=0.05)",
        "",
        "Six tests: 3 metrics × 2 comparisons (DeltaRAG vs RAG, DeltaRAG vs Graph). ",
        "Effect size = mean paired delta (DeltaRAG minus baseline) with 95% bootstrap CI. ",
        "`***` marks comparisons that reject the null after Holm correction.",
        "",
        "| Comparison | Δ (mean) | 95% CI | p (raw) | Significant |",
        "| :--- | :--- | :--- | :--- | :--- |",
    ]
    for label, p, eff, rej in zip(
        confirmatory_labels, confirmatory_pvals, confirmatory_effects, rejected
    ):
        md, lo, hi = eff
        sig = "***" if rej else ""
        md_lines.append(
            f"| {label} | {md:+.4f} | [{lo:+.4f}, {hi:+.4f}] | "
            f"{p:.4f} | {sig} |"
        )

    # ── Per-type summary (exploratory: raw p + CIs, no correction) ──
    md_lines += [
        "",
        "## Per-Type Summary (exploratory)",
        "",
        "Per-type tests are **not** corrected for multiple comparisons. ",
        "Report effect sizes and CIs alongside raw p-values. ",
        "With n=10 per type and Wilcoxon ties common, expect low statistical power.",
        "",
        "| Query Type | N | Metric | Vanilla RAG | Graph-Only | DeltaRAG | "
        "Δ vs RAG (95% CI) | p |",
        "| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |",
    ]

    for qtype in sorted(by_type.keys()):
        results = by_type[qtype]
        label = QUERY_TYPE_LABELS.get(qtype, qtype)
        n = len(results)

        print(f"\n  Type {qtype}: {label} (n={n})")
        for metric in ["Recall", "Precision", "NDCG"]:
            cells = {}
            for algo in ["RAG", "Graph", "DeltaRAG"]:
                v = [r[algo][metric] for r in results]
                cells[algo] = (mean(v), std(v))
                print(f"    {algo:10s} {metric}: {cells[algo][0]:.3f} "
                      f"+/- {cells[algo][1]:.3f}")

            delta_vals = [r["DeltaRAG"][metric] for r in results]
            rag_vals = [r["RAG"][metric] for r in results]
            p_type = safe_wilcoxon(delta_vals, rag_vals)
            md_eff, lo_eff, hi_eff = paired_bootstrap_ci(delta_vals, rag_vals)

            best_algo = max(cells, key=lambda a: cells[a][0])
            def fmt(algo):
                m, s = cells[algo]
                text = f"{m:.3f} ± {s:.3f}"
                return f"**{text}**" if algo == best_algo else text

            md_lines.append(
                f"| **{qtype}: {label}** | {n} | {metric}@{k} | "
                f"{fmt('RAG')} | {fmt('Graph')} | {fmt('DeltaRAG')} | "
                f"{md_eff:+.3f} [{lo_eff:+.3f}, {hi_eff:+.3f}] | {p_type:.3f} |"
            )

    # ── Overall aggregates ───────────────────────────────────────
    md_lines += [
        "",
        "## Overall Aggregates",
        "",
        "| Metric | Vanilla RAG | Graph-Only | DeltaRAG |",
        "| :--- | :--- | :--- | :--- |",
    ]
    print(f"\n{'=' * 90}\n  OVERALL (all {len(all_results)} queries)")
    for metric in ["Recall", "Precision", "NDCG"]:
        cells = {}
        for algo in ["RAG", "Graph", "DeltaRAG"]:
            v = [r[algo][metric] for r in all_results]
            cells[algo] = (mean(v), std(v))
            print(f"    {algo:10s} {metric}: {cells[algo][0]:.3f} "
                  f"+/- {cells[algo][1]:.3f}")
        best_algo = max(cells, key=lambda a: cells[a][0])
        def fmt_o(algo):
            m, s = cells[algo]
            text = f"{m:.3f} ± {s:.3f}"
            return f"**{text}**" if algo == best_algo else text
        md_lines.append(
            f"| {metric}@{k} | {fmt_o('RAG')} | {fmt_o('Graph')} | "
            f"{fmt_o('DeltaRAG')} |"
        )

    # ── Per-query detail ─────────────────────────────────────────
    md_lines += [
        "",
        "## Per-Query Detail",
        "",
        "| ID | Type | Source | RAG R | RAG P | RAG N | Graph R | Graph P | "
        "Graph N | Delta R | Delta P | Delta N |",
        "| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | "
        ":--- | :--- | :--- |",
    ]
    abbreviations = {
        "Android Security Bulletin - Latest": "Bulletin",
        "Play Integrity API Overview": "Integrity",
        "CISA Known Exploited Vulnerabilities": "CISA HTML",
        "CISA KEV JSON Feed": "KEV JSON",
        "Google Play Developer Policy Center": "Policy",
        "Android API Differences Report": "API Diff",
        "NVD CVE Feed (Android)": "NVD",
        "Android CTS/CDD Changes": "CTS/CDD",
        "Samsung Mobile Security Bulletin": "Samsung",
        "Pixel Update Bulletin": "Pixel",
    }
    for r in all_results:
        ra, gr, dr = r["RAG"], r["Graph"], r["DeltaRAG"]
        src_short = abbreviations.get(r["source"], r["source"])
        md_lines.append(
            f"| {r['id']} | {r['type']} | {src_short} | "
            f"{ra['Recall']:.2f} | {ra['Precision']:.2f} | {ra['NDCG']:.2f} | "
            f"{gr['Recall']:.2f} | {gr['Precision']:.2f} | {gr['NDCG']:.2f} | "
            f"{dr['Recall']:.2f} | {dr['Precision']:.2f} | {dr['NDCG']:.2f} |"
        )

    md_text = "\n".join(md_lines) + "\n"
    with open(output_path, "w") as f:
        f.write(md_text)
    print(f"\n{'=' * 90}\nResults written to {output_path}")


# ── CLI ──────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Run the DeltaRAG retrieval ablation study."
    )
    parser.add_argument(
        "--seed", action="store_true",
        help="Wipe and reseed the DB with deterministic test data before running. "
             "Required on a fresh DB. Destructive — skip if the DB is already in "
             "the expected test state.",
    )
    parser.add_argument(
        "--output", type=str, default="evaluation_matrix.md",
        help="Path to write the markdown results (default: evaluation_matrix.md).",
    )
    parser.add_argument(
        "--k", type=int, default=5,
        help="Top-k for retrieval (default: 5).",
    )
    args = parser.parse_args()
    run_ablation_study(k=args.k, do_seed=args.seed, output_path=args.output)


if __name__ == "__main__":
    main()