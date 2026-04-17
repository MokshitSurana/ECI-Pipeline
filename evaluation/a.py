from evaluation.ablation_study import prepare_top_k, compute_recall, compute_precision, compute_ndcg
top = prepare_top_k([1, 1, 1, 2, 2], k=5)  # → [1, 2]
assert compute_recall(top, {1, 2}, 5) == 1.0
assert compute_precision(top, {1, 2}, 5) == 0.4  # 2/5, not 2/2
assert abs(compute_ndcg(top, {1, 2}, 5) - 1.0) < 1e-9  #