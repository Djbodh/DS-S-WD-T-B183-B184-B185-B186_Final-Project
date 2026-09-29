"""
run_all.py — execute the whole pipeline in dependency order.

    python run_all.py                 # stages 01-08, 10, 11 (everything runnable)
    python run_all.py --from 05       # resume from the mode classifier
    python run_all.py --only 02 03    # re-run just cleaning and features
    python run_all.py --with-cv       # include YOLO training (needs a dataset)

Each stage is a separate module with a `main()`. That is deliberate: when
Stage 06 fails at 2 a.m. you re-run Stage 06, not the whole four-hour chain.
"""
from __future__ import annotations

import argparse
import importlib
import json
import sys
import time
from datetime import datetime

from config.settings import REPORTS

STAGES = [
    ("01", "pipeline.p01_ingest", "Ingest raw files"),
    ("02", "pipeline.p02_clean", "Clean & standardise"),
    ("03", "pipeline.p03_features", "Feature engineering"),
    ("04", "pipeline.p04_load_sql", "Load SQL database"),
    ("05", "pipeline.p05_train_mode_classifier", "Train mode classifier"),
    ("06", "pipeline.p06_train_eta_regressor", "Train ETA regressor"),
    ("07", "pipeline.p07_train_maintenance", "Train maintenance model"),
    ("08", "pipeline.p08_route_optimizer", "Route optimisation"),
    ("10", "pipeline.p10_sentiment", "Sentiment analysis"),
    ("11", "pipeline.p11_build_rag_index", "Build RAG index"),
]
CV_STAGE = ("09", "pipeline.p09_train_yolo", "Train YOLO damage detector")


def run(stage_id: str, module: str, label: str) -> dict:
    print(f"\n{'#' * 68}\n### [{stage_id}] {label}\n{'#' * 68}")
    t0 = time.time()
    try:
        mod = importlib.import_module(module)
        code = mod.main() if hasattr(mod, "main") else 0
        status = "ok" if code == 0 else "failed"
    except Exception as exc:
        import traceback
        traceback.print_exc()
        status, code = "error", 1
        print(f"\n  !! stage {stage_id} raised: {exc}")
    dt = round(time.time() - t0, 1)
    print(f"\n  [{stage_id}] {status} in {dt}s")
    return {"stage": stage_id, "label": label, "status": status,
            "exit_code": code, "seconds": dt}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--from", dest="start", default=None, help="resume from this stage id")
    ap.add_argument("--only", nargs="+", default=None, help="run only these stage ids")
    ap.add_argument("--with-cv", action="store_true", help="include YOLO training")
    ap.add_argument("--stop-on-error", action="store_true")
    args = ap.parse_args()

    stages = STAGES[:]
    if args.with_cv:
        stages.insert(8, CV_STAGE)
    if args.only:
        stages = [s for s in stages if s[0] in set(args.only)]
    elif args.start:
        ids = [s[0] for s in stages]
        if args.start in ids:
            stages = stages[ids.index(args.start):]

    print("=" * 68)
    print("SMARTLOGIX AI — FULL PIPELINE")
    print(f"started {datetime.now():%Y-%m-%d %H:%M:%S}")
    print(f"stages: {', '.join(s[0] for s in stages)}")
    print("=" * 68)

    results, t0 = [], time.time()
    for sid, mod, label in stages:
        r = run(sid, mod, label)
        results.append(r)
        if r["status"] != "ok" and args.stop_on_error:
            print(f"\n  stopping: stage {sid} did not succeed")
            break

    total = round(time.time() - t0, 1)
    print("\n" + "=" * 68)
    print("PIPELINE SUMMARY")
    print("=" * 68)
    for r in results:
        mark = "PASS" if r["status"] == "ok" else "FAIL"
        print(f"  [{r['stage']}] {r['label']:<32} {mark:<5} {r['seconds']:>7.1f}s")
    print(f"\n  total: {total}s")

    (REPORTS / "pipeline_run.json").write_text(json.dumps(
        {"run_at": datetime.now().isoformat(timespec="seconds"),
         "total_seconds": total, "stages": results}, indent=2), encoding="utf-8")
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
