"""
check_env.py — run this FIRST if anything fails.

It tells you, in plain English:
  * which Python is running
  * whether you are inside the virtual environment
  * which required packages are missing
  * whether your data files are in the right place

Run:  python check_env.py
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

CORE = [
    ("pandas", "pandas"), ("numpy", "numpy"), ("pyarrow", "pyarrow"),
    ("scipy", "scipy"), ("sklearn", "scikit-learn"), ("joblib", "joblib"),
    ("sqlalchemy", "SQLAlchemy"), ("fastapi", "fastapi"), ("uvicorn", "uvicorn"),
    ("pydantic", "pydantic"), ("streamlit", "streamlit"), ("plotly", "plotly"),
    ("matplotlib", "matplotlib"), ("requests", "requests"),
    ("dotenv", "python-dotenv"), ("tqdm", "tqdm"), ("rank_bm25", "rank-bm25"),
]

OPTIONAL = [
    ("xgboost", "xgboost", "sklearn HistGradientBoosting is used instead"),
    ("lightgbm", "lightgbm", "not required"),
    ("ortools", "ortools", "nearest-neighbour + 2-opt is used instead"),
    ("ultralytics", "ultralytics", "only needed for Stage 09 (YOLO)"),
    ("torch", "torch", "only needed for Stage 09 / BERT"),
    ("transformers", "transformers", "only needed for Stage 10 --bert"),
    ("faiss", "faiss-cpu", "BM25 retrieval is used instead"),
    ("psycopg2", "psycopg2-binary", "only needed for PostgreSQL / RDS"),
    ("boto3", "boto3", "only needed for AWS deployment"),
]

RAW_EXPECTED = [
    "orders.csv", "customers.csv", "delivery_logs.csv", "drone_telemetry.csv",
    "fleet_vehicles.csv", "maintenance_history.csv", "traffic_data.csv",
    "weather_data.csv", "customer_reviews.jsonl", "product_catalog.json",
    "gps_routes.json",
]


def have(mod: str) -> bool:
    try:
        return importlib.util.find_spec(mod) is not None
    except (ImportError, ValueError):
        return False


def main() -> int:
    print("=" * 68)
    print("SMARTLOGIX AI — ENVIRONMENT CHECK")
    print("=" * 68)

    # ---------------------------------------------------------- 1. interpreter
    print("\n[1] Python interpreter")
    print(f"    version    : {sys.version.split()[0]}")
    print(f"    executable : {sys.executable}")

    in_venv = sys.prefix != sys.base_prefix
    exe = sys.executable.lower()

    if in_venv:
        print("    venv       : YES — you are inside the virtual environment")
    else:
        print("    venv       : NO  <-- THIS IS ALMOST CERTAINLY YOUR PROBLEM")
        print()
        print("    Fix (PowerShell, from the smartlogix-ai folder):")
        print("        python -m venv .venv")
        print("        .venv\\Scripts\\Activate.ps1")
        print("        pip install -r requirements.txt")
        print()
        print("    Your prompt should then start with (.venv)")

    if "windowsapps" in exe:
        print()
        print("    ! You are using the Microsoft Store build of Python.")
        print("      It works, but it has restricted file access and causes")
        print("      odd permission errors. If you hit trouble, install")
        print("      Python 3.12 from python.org instead and tick")
        print("      'Add python.exe to PATH' during setup.")

    major, minor = sys.version_info[:2]
    if (major, minor) >= (3, 13):
        print(f"\n    ! Python {major}.{minor} is very new. Some wheels may not")
        print("      exist yet. Python 3.10-3.12 is the tested range.")

    # ---------------------------------------------------------- 2. core packages
    print("\n[2] Core packages")
    missing = [pip for mod, pip in CORE if not have(mod)]
    for mod, pip_name in CORE:
        print(f"    {'OK  ' if have(mod) else 'MISS'}  {pip_name}")

    # ---------------------------------------------------------- 3. optional
    print("\n[3] Optional packages (all have fallbacks)")
    for mod, pip_name, note in OPTIONAL:
        state = "OK  " if have(mod) else "--  "
        print(f"    {state}  {pip_name:<22} {'' if have(mod) else note}")

    # ---------------------------------------------------------- 4. data files
    print("\n[4] Data files in data/raw/")
    raw = ROOT / "data" / "raw"
    if not raw.exists():
        print("    folder does not exist yet — it is created on first run")
        found, absent = [], RAW_EXPECTED
    else:
        found = [f for f in RAW_EXPECTED if (raw / f).exists()]
        absent = [f for f in RAW_EXPECTED if not (raw / f).exists()]
        for f in RAW_EXPECTED:
            print(f"    {'OK  ' if (raw / f).exists() else 'MISS'}  {f}")

    # ---------------------------------------------------------- 5. verdict
    print("\n" + "=" * 68)
    print("VERDICT")
    print("=" * 68)

    ok = True
    if not in_venv:
        ok = False
        print("  X  Not in a virtual environment — see [1] above.")
    if missing:
        ok = False
        print(f"  X  {len(missing)} core package(s) missing: {', '.join(missing)}")
        print("     Fix:  pip install -r requirements.txt")
    if absent:
        print(f"  !  {len(absent)} data file(s) not in data/raw/: {', '.join(absent)}")
        print("     Copy them in, then re-run this check.")
    if ok and not absent:
        print("  OK  Everything is in place. Run:  python run_all.py")
    elif ok:
        print("  OK  Environment is fine — just add the data files.")

    print()
    return 0 if (ok and not absent) else 1


if __name__ == "__main__":
    sys.exit(main())
