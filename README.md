# SmartLogix AI

**Intelligent Multi-Modal Logistics & Autonomous Delivery Platform**
ML · Computer Vision · NLP · LLM + RAG · AI Agents · AWS

HCL GUVI Capstone — Logistics & Supply Chain

---

## What this is

An end-to-end platform that decides **how** to ship a parcel (drone / bike / van
/ truck / air cargo / ship), **when** it will arrive, **which route** to take,
**whether the vehicle is safe to fly**, and answers customer questions about all
of it through a local LLM with retrieval.

Every number below was produced by running this code on the supplied dataset.

| Model | Metric | Achieved | PDF target | |
|---|---|---|---|---|
| Logistics mode classifier | Accuracy | **0.955** | ≥ 0.88 | PASS |
| | Macro F1 | **0.927** | ≥ 0.88 | PASS |
| | ROC-AUC | **0.989** | — | |
| | CV F1 (5-fold) | 0.926 ± 0.011 | — | |
| ETA regressor | R² | **0.992** | ≥ 0.85 | PASS |
| | MAPE | **7.44%** | ≤ 12% | PASS |
| | MAE (bike / drone) | **13.3 / 13.5 min** | ≤ 15 min | PASS |
| | MAE (all modes) | 48.9 min | ≤ 15 min | see note |
| Predictive maintenance | Accuracy | **0.980** | ≥ 0.90 | PASS |
| | Recall | **0.901** | ≥ 0.90 | PASS |
| | F1 | **0.911** | ≥ 0.90 | PASS |
| | False-alarm rate | **0.98%** | ≤ 10% | PASS |
| Route optimisation | Distance reduction | **81.3%** vs FCFS baseline | ≥ 12% | PASS |
| Sentiment | Accuracy | 1.00 | — | see note |
| YOLO damage detection | — | needs your image dataset | — | — |

**ETA note:** the 15-minute target is not achievable as a single global number
across modes spanning a 20-minute drone hop to a 3-day sea leg. Bike and drone
both clear it. Report the per-mode table (`reports/06_eta_error_by_mode.csv`).

**Sentiment note:** the reviews file contains only **303 unique texts across
11,200 rows** (97.3% duplication) generated from a fixed sentence bank, each
template mapping to one label. Any model scores 100%. Stage 10 detects this
automatically, switches to a grouped split, and prints a warning. Report the
limitation — catching it is worth more than the score.

---

## Quickstart

```bash
# 1. environment
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 2. data
cp /path/to/your/*.csv /path/to/your/*.json* data/raw/

# 3. run everything (~4 minutes on a laptop)
python run_all.py

# 4. local LLM  (see docs/LOCAL_LLM_SETUP.md)
curl -fsSL https://ollama.com/install.sh | sh
ollama serve &
ollama pull qwen2.5:7b-instruct
python -m rag.llm_client                    # health check

# 5. serve
uvicorn api.main:app --port 8000            # http://localhost:8000/docs
streamlit run app/dashboard.py              # http://localhost:8501
```

Computer vision needs an image dataset you supply:
```bash
python -m pipeline.p09_train_yolo --init    # scaffold + annotation guide
# drop annotated images into cv/dataset/{train,valid,test}/
python -m pipeline.p09_train_yolo
```

---

## Repository layout

```
smartlogix-ai/
├── config/settings.py            paths, vocabularies, constraints, thresholds
├── pipeline/
│   ├── cleaners.py               messy-value parsers (dates, units, currency)
│   ├── io_utils.py               parquet with csv.gz fallback
│   ├── model_utils.py            model factory, preprocessing, metric gates
│   ├── p01_ingest.py             read raw, profile, land
│   ├── p02_clean.py              type, canonicalise, dedupe, validate
│   ├── p03_features.py           joins + engineered features
│   ├── p04_load_sql.py           SQLite / RDS load, views, indexes
│   ├── p05_train_mode_classifier.py
│   ├── p06_train_eta_regressor.py
│   ├── p07_train_maintenance.py
│   ├── p08_route_optimizer.py    VRP: OR-Tools + NN/2-opt fallback
│   ├── p09_train_yolo.py         drone damage detection
│   ├── p10_sentiment.py          TF-IDF + BERT + aspect mining
│   └── p11_build_rag_index.py    FAISS + BM25 knowledge base
├── rag/
│   ├── llm_client.py             Ollama / llama.cpp / Bedrock
│   ├── retriever.py              hybrid dense+sparse with RRF
│   └── knowledge/*.md            policy corpus (editable)
├── agents/agent_system.py        5 agents + router, tool-first
├── api/main.py                   FastAPI, 11 endpoints
├── app/dashboard.py              Streamlit, 6 pages
├── cv/                           YOLO dataset + annotation guide
├── sql/schema.sql                PostgreSQL DDL
├── docs/
│   ├── CODE_WALKTHROUGH.md       ← line-by-line explanation of every stage
│   ├── LOCAL_LLM_SETUP.md        ← which model, where, how
│   └── AWS_DEPLOYMENT.md         ← S3, RDS, EC2, Lambda, SES, Bedrock
├── run_all.py                    orchestrator
└── requirements.txt
```

---

## PDF requirement coverage

| Phase | Requirement | Where |
|---|---|---|
| 1 | Data collection (11 sources) | `p01_ingest.py` |
| 2 | Cleaning, feature engineering, missing values | `p02_clean.py`, `p03_features.py`, `cleaners.py` |
| 2 | SQL database design | `sql/schema.sql`, `p04_load_sql.py` |
| 2 | AWS S3 image storage | `docs/AWS_DEPLOYMENT.md` §1 |
| 3 | Logistics mode classification | `p05_train_mode_classifier.py` |
| 3 | ETA prediction | `p06_train_eta_regressor.py` |
| 3 | Predictive maintenance | `p07_train_maintenance.py` |
| 4 | VRP, battery constraints, payload, scheduling | `p08_route_optimizer.py` |
| 5 | YOLO — 6 damage classes | `p09_train_yolo.py`, `cv/ANNOTATION_GUIDE.md` |
| 6 | RAG chatbot: orders, delivery, products, reviews, FAQs | `p11_build_rag_index.py`, `rag/`, `agents/` |
| 6 | Multi-agent system | `agents/agent_system.py` |
| 7 | EC2, RDS, S3, Lambda, email | `docs/AWS_DEPLOYMENT.md` |
| 7 | REST APIs (FastAPI) | `api/main.py` |
| 8 | Dashboards: delivery, fleet, drone health, orders, analytics | `app/dashboard.py` |

---
## Data quality findings

Documented in `reports/02_dedupe_audit.csv` and `reports/02_null_report.csv`:

| Issue | Scale | Handling |
|---|---|---|
| Mixed date formats (5, incl. epoch) | all timestamp columns | `cleaners.to_datetime` |
| Mixed weight units (`16.89KG`, `87540 g`) | 14,009 orders | `cleaners.weight_to_kg` |
| Currency noise (`₹`, `INR `, commas) | orders, maintenance | `cleaners.to_float` |
| Categorical variants (`Air Cargo`/`AIR CARGO`/`air_cargo`) | every categorical | alias maps in `settings.py` |
| Booleans in 6 forms | orders, customers, traffic | `cleaners.to_bool` |
| Sentinel `99999` in distance | orders | `cleaners.mask_sentinels` |
| Missing temperature unit | 2,738 weather rows | inferred from magnitude |
| Duplicate business keys | 650 orders, 120 customers, 400 weather | two-stage dedupe with audit |
| Missing sentiment labels | 4,035 reviews | derived from rating, provenance tracked |
| Template-duplicated review text | 97.3% | leakage audit + grouped split |

---

## Testing

```bash
python -m rag.llm_client                                    # LLM health
python -m agents.agent_system "Where is my order ORD-007410?"
curl localhost:8000/health
curl -X POST localhost:8000/predict/mode -H 'Content-Type: application/json' \
     -d '{"distance_km":18.5,"package_weight_kg":2.4,"delivery_priority":"EXPRESS"}'
sqlite3 artifacts/smartlogix.db "SELECT * FROM v_delivery_kpi;"
```

---

## Known limitations

State these in your report — an examiner respects a documented limitation more
than a hidden one.

1. **ETA target is per-mode, not global.** Explained above.
2. **Sentiment benchmark is saturated.** The dataset cannot distinguish a good
   model from a memorising one. Run `--bert` to compare, but expect the same 1.00.
3. **CV stage needs external data.** No drone images were supplied.
4. **Route reduction of 81% is against a first-come-first-served baseline**, not
   against a production planner. It is a real improvement, but say what the
   baseline was.
5. **Sentiment labels are 35% derived from star ratings.** `sentiment_source`
   tracks which; an ablation on `GIVEN`-only rows is a good extra experiment.
6. **SES sandbox** requires verified recipients unless you request production
   access.
