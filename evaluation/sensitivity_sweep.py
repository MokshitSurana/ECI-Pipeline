"""Sensitivity / robustness sweep for DeltaRAG.

Sweeps two retrieval knobs against the deterministic synthetic benchmark and
reports how DeltaRAG's overall metrics — and its trade-off against Vanilla RAG —
move across the grid:

    - k      (retrieval depth)      ∈ {3, 5, 10}
    - rrf_k  (RRF fusion constant)  ∈ {10, 30, 60, 100}

The point is robustness, not tuning: if DeltaRAG's numbers barely move across
rrf_k, the reported result is not an artifact of a hand-picked fusion constant.

Runs entirely against the isolated local eval DB (ECI_EVAL=1), so it never
touches the live Supabase. Seed once with --seed; subsequent runs can reuse it.
"""
import os
# Isolation: force the separate local eval DB before any config-reading import.
os.environ["ECI_EVAL"] = "1"

import argparse
from collections import defaultdict
from typing import Dict, List, Tuple

from utils.db import get_session, Source, Change
from rag.knowledge_graph import KnowledgeGraph
from evaluation.golden_queries import GOLDEN_QUERIES

from evaluation.ablation_study import (
    run_vanilla_rag,
    run_graph_only,
    run_deltarag,
    prepare_top_k,
    compute_recall,
    compute_precision,
    compute_ndcg,
    compute_p_at_1,
    compute_mrr,
    compute_map,
    paired_bootstrap_ci,
    safe_wilcoxon,
    assert_expected_db_state,
)

# ── Sweep grid ───────────────────────────────────────────────────
K_VALUES = [3, 5, 10]
RRF_K_VALUES = [10, 30, 60, 100]
BASELINE = (5, 60)  # (k, rrf_k) — must reproduce evaluation_matrix.md


def _mean(xs: List[float]) -> float:
    return sum(xs) / len(xs) if xs else 0.0


def evaluate_config(
    k: int, rrf_k: int, name_to_id: Dict[str, int],
    id_to_category: Dict[int, str], changes_by_source: Dict[int, Change],
    kg: KnowledgeGraph,
) -> Dict[str, Dict[str, List[float]]]:
    """Run all golden queries at one (k, rrf_k) config.

    Returns {algo: {metric: [per-query values]}} for RAG and DeltaRAG.
    """
    metrics = ["Recall", "Precision", "NDCG", "P@1", "MRR", "MAP"]
    acc = {algo: {m: [] for m in metrics} for algo in ("RAG", "DeltaRAG")}

    for gq in GOLDEN_QUERIES:
        source_id = name_to_id.get(gq["source"])
        if not source_id:
            continue

        if gq["query"] is None:
            change = changes_by_source.get(source_id)
            if not change or not change.diff_text:
                continue
            query_text = change.diff_text
        else:
            query_text = gq["query"]

        expected_ids = {
            name_to_id[n] for n in gq["expected"] if n in name_to_id
        }
        if not expected_ids:
            continue

        rag_topk = prepare_top_k(run_vanilla_rag(query_text, source_id, k), k)
        delta_topk = prepare_top_k(
            run_deltarag(query_text, source_id, k, rrf_k=rrf_k), k
        )

        for algo, topk in (("RAG", rag_topk), ("DeltaRAG", delta_topk)):
            acc[algo]["Recall"].append(compute_recall(topk, expected_ids, k))
            acc[algo]["Precision"].append(compute_precision(topk, expected_ids, k))
            acc[algo]["NDCG"].append(compute_ndcg(topk, expected_ids, k))
            acc[algo]["P@1"].append(compute_p_at_1(topk, expected_ids))
            acc[algo]["MRR"].append(compute_mrr(topk, expected_ids))
            acc[algo]["MAP"].append(compute_map(topk, expected_ids))

    return acc


def run_sweep(do_seed: bool, output_path: str):
    if do_seed:
        print("Seeding deterministic test data into the isolated eval DB...")
        from evaluation.test_data import seed_test_data
        seed_test_data()
    else:
        print("Verifying isolated eval DB state (use --seed to reseed)...")
        assert_expected_db_state()
        print("DB state OK.")

    session = get_session()
    sources = session.query(Source).all()
    name_to_id = {s.name: s.id for s in sources}
    id_to_category = {s.id: s.category for s in sources}
    changes_by_source = {}
    for change in session.query(Change).filter_by(status="pending").all():
        changes_by_source[change.source_id] = change
    session.close()

    print("Loading knowledge graph...")
    kg = KnowledgeGraph.load_or_create()

    configs: List[Tuple[int, int]] = [
        (k, rrf_k) for k in K_VALUES for rrf_k in RRF_K_VALUES
    ]
    rows = []
    n_scored = None

    for k, rrf_k in configs:
        print(f"  config k={k:<2} rrf_k={rrf_k:<3} ...", end=" ", flush=True)
        acc = evaluate_config(
            k, rrf_k, name_to_id, id_to_category, changes_by_source, kg
        )
        delta = acc["DeltaRAG"]
        rag = acc["RAG"]
        n = len(delta["Recall"])
        n_scored = n

        d_recall = paired_bootstrap_ci(delta["Recall"], rag["Recall"])
        p_recall = safe_wilcoxon(delta["Recall"], rag["Recall"])
        d_ndcg = paired_bootstrap_ci(delta["NDCG"], rag["NDCG"])
        p_ndcg = safe_wilcoxon(delta["NDCG"], rag["NDCG"])

        rows.append({
            "k": k, "rrf_k": rrf_k, "n": n,
            "d_recall": _mean(delta["Recall"]),
            "d_prec": _mean(delta["Precision"]),
            "d_ndcg": _mean(delta["NDCG"]),
            "d_p1": _mean(delta["P@1"]),
            "d_mrr": _mean(delta["MRR"]),
            "d_map": _mean(delta["MAP"]),
            "r_recall": _mean(rag["Recall"]),
            "r_ndcg": _mean(rag["NDCG"]),
            "delta_recall_vs_rag": d_recall[0],
            "ci_recall": (d_recall[1], d_recall[2]),
            "p_recall": p_recall,
            "delta_ndcg_vs_rag": d_ndcg[0],
            "ci_ndcg": (d_ndcg[1], d_ndcg[2]),
            "p_ndcg": p_ndcg,
        })
        print(
            f"DeltaRAG R={_mean(delta['Recall']):.3f} "
            f"nDCG={_mean(delta['NDCG']):.3f} "
            f"P@1={_mean(delta['P@1']):.3f}"
        )

    _write_markdown(rows, n_scored, output_path)
    print(f"\nResults written to {output_path}")
    return rows


def _write_markdown(rows, n_scored, output_path):
    md = [
        "# DeltaRAG Sensitivity / Robustness Sweep",
        "",
        f"**{n_scored} scored queries** | grid: "
        f"k ∈ {{{', '.join(map(str, K_VALUES))}}} × "
        f"rrf_k ∈ {{{', '.join(map(str, RRF_K_VALUES))}}} | "
        f"bootstrap n=10000, seed=42",
        "",
        "All metrics are DeltaRAG overall means at the given config. "
        "`Δrecall` and `ΔnDCG` are paired mean differences (DeltaRAG − Vanilla RAG) "
        "with 95% bootstrap CIs and raw paired-Wilcoxon p (uncorrected).",
        "",
        "## Full Grid",
        "",
        "| k | rrf_k | Recall | Prec | nDCG | P@1 | MRR | MAP | Δrecall vs RAG (95% CI) | p | ΔnDCG vs RAG (95% CI) | p |",
        "| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |",
    ]
    for r in rows:
        baseline_mark = " ⟵ baseline" if (r["k"], r["rrf_k"]) == BASELINE else ""
        md.append(
            f"| {r['k']}{baseline_mark} | {r['rrf_k']} | "
            f"{r['d_recall']:.3f} | {r['d_prec']:.3f} | {r['d_ndcg']:.3f} | "
            f"{r['d_p1']:.3f} | {r['d_mrr']:.3f} | {r['d_map']:.3f} | "
            f"{r['delta_recall_vs_rag']:+.3f} "
            f"[{r['ci_recall'][0]:+.3f}, {r['ci_recall'][1]:+.3f}] | "
            f"{r['p_recall']:.3f} | "
            f"{r['delta_ndcg_vs_rag']:+.3f} "
            f"[{r['ci_ndcg'][0]:+.3f}, {r['ci_ndcg'][1]:+.3f}] | "
            f"{r['p_ndcg']:.3f} |"
        )

    # Robustness summary across the fusion constant at the baseline depth.
    at_k5 = [r for r in rows if r["k"] == 5]
    if at_k5:
        recalls = [r["d_recall"] for r in at_k5]
        ndcgs = [r["d_ndcg"] for r in at_k5]
        p1s = [r["d_p1"] for r in at_k5]
        md += [
            "",
            "## Robustness to the Fusion Constant (k=5)",
            "",
            f"Varying `rrf_k` across {{{', '.join(map(str, RRF_K_VALUES))}}} at k=5 "
            f"moves DeltaRAG Recall over a range of "
            f"{max(recalls) - min(recalls):.3f} "
            f"(min {min(recalls):.3f}, max {max(recalls):.3f}), "
            f"nDCG over {max(ndcgs) - min(ndcgs):.3f}, and "
            f"P@1 over {max(p1s) - min(p1s):.3f}. "
            f"A near-flat response indicates the reported result is not an "
            f"artifact of a hand-tuned fusion constant.",
        ]
    md.append("")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md))


def main():
    parser = argparse.ArgumentParser(
        description="DeltaRAG sensitivity/robustness sweep (k × rrf_k)."
    )
    parser.add_argument(
        "--seed", action="store_true",
        help="Reseed the isolated eval DB before running.",
    )
    parser.add_argument(
        "--output", type=str, default="sensitivity_analysis.md",
        help="Path to write the markdown results (default: sensitivity_analysis.md).",
    )
    args = parser.parse_args()
    run_sweep(do_seed=args.seed, output_path=args.output)


if __name__ == "__main__":
    main()
