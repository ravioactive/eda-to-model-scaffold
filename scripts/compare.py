#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, os, sys
from datetime import datetime
from typing import List, Dict, Any, Tuple

METRIC_DIR = {
    # True => higher is better
    "roc_auc": True,
    "pr_auc": True,
    "r2": True,
    # False => lower is better
    "brier": False,
    "rmse": False,
    "mae": False,
}

def fmt(v, nd=4):
    if v is None:
        return "-"
    if abs(v) >= 1000:
        return f"{v:.2e}"
    return f"{v:.{nd}f}"

def load_runs(path: str) -> List[Dict[str, Any]]:
    if not os.path.exists(path):
        print(f"[compare] No file at {path}. Run training first.", file=sys.stderr); sys.exit(1)
    data = json.loads(open(path).read())
    if isinstance(data, dict):
        data = [data]
    return data

def pick_metric(task: str, metric: str|None) -> str:
    if metric: return metric
    return "roc_auc" if task == "classification" else "rmse"

def group_key(run: Dict[str, Any], by: str) -> str:
    if by == "config":
        return str(run.get("config", "unknown"))
    elif by == "task":
        return str(run.get("task", "unknown"))
    return "all"

def extract_value(run: Dict[str, Any], metric: str):
    test = run.get("test", {})
    return test.get(metric, None)

def best_in_group(values: List[float], higher_is_better: bool) -> float|None:
    vals = [v for v in values if v is not None]
    if not vals: return None
    return max(vals) if higher_is_better else min(vals)

def sort_key(v: float|None, higher_is_better: bool):
    if v is None: return float("-inf") if higher_is_better else float("inf")
    return v

def main():
    ap = argparse.ArgumentParser(description="Pretty-print model run comparisons from results/compare.json")
    ap.add_argument("--path", type=str, default="results/compare.json", help="Path to compare.json")
    ap.add_argument("--task", type=str, default="classification", choices=["classification","regression","all"], help="Filter by task")
    ap.add_argument("--metric", type=str, default=None, help="Metric to compare (roc_auc, pr_auc, brier, rmse, mae, r2). Defaults by task.")
    ap.add_argument("--by", type=str, default="task", choices=["task","config","all"], help="Group results by this key")
    ap.add_argument("--top", type=int, default=10, help="Top N rows per group")
    args = ap.parse_args()

    runs = load_runs(args.path)

    # Filter by task if specified
    if args.task != "all":
        runs = [r for r in runs if r.get("task") == args.task]
        if not runs:
            print(f"[compare] No runs for task='{args.task}'")
            sys.exit(0)

    # Determine default metric if not provided
    task_for_default = runs[0].get("task","classification") if args.task=="all" else args.task
    metric = pick_metric(task_for_default, args.metric)
    if metric not in METRIC_DIR:
        print(f"[compare] Unknown metric '{metric}'. Choose from: {list(METRIC_DIR.keys())}")
        sys.exit(1)

    hib = METRIC_DIR[metric]

    # Build groups
    groups: Dict[str, List[Dict[str, Any]]] = {}
    for r in runs:
        k = group_key(r, args.by)
        groups.setdefault(k, []).append(r)

    # Print per-group tables
    for g, items in groups.items():
        # Compute best
        values = [extract_value(r, metric) for r in items]
        best = best_in_group(values, hib)

        # Sort
        items_sorted = sorted(items, key=lambda r: sort_key(extract_value(r, metric), hib), reverse=hib)

        print("="*80)
        print(f"Group: {args.by} = {g} | Metric: {metric} ({'higher' if hib else 'lower'} is better)")
        print("-"*80)
        print(f"{'rank':>4}  {'metric':>10}  {'Δ vs best':>10}  {'calib':>5}  {'tuned':>5}  {'mono':>4}  {'model':<28}  {'config':<40}  {'timestamp'}")
        print("-"*80)
        for i, r in enumerate(items_sorted[:args.top], 1):
            val = extract_value(r, metric)
            if best is None or val is None:
                delta = None
            else:
                delta = (val - best) if hib else (best - val)
            test = r.get("test", {})
            calibrated = test.get("calibrated", False)
            tuned = r.get("tuned", False)
            mono = r.get("monotone", False)
            model = r.get("model","?")
            cfg = str(r.get("config","-"))
            ts = r.get("timestamp","-")
            print(f"{i:>4}  {fmt(val):>10}  {fmt(delta):>10}  {str(calibrated):>5}  {str(tuned):>5}  {str(mono):>4}  {model:<28}  {cfg:<40}  {ts}")
        print()

if __name__ == "__main__":
    main()
