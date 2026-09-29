# START HERE

SmartLogix AI — complete capstone project. Code, documentation and results in
one folder.

---

## 1. Get it running (10 minutes)

Open this folder in VS Code with **File → Open Folder** — the folder itself, not
its parent, not a single file. Then in the terminal (`Ctrl + ~`):

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Copy your 11 data files in — **one pattern per line**, PowerShell's `Copy-Item`
is not Linux `cp`:

```powershell
Copy-Item $HOME\Downloads\*.csv   data\raw\
Copy-Item $HOME\Downloads\*.json  data\raw\
Copy-Item $HOME\Downloads\*.jsonl data\raw\
```

Check everything is in place, then run:

```powershell
python check_env.py
python run_all.py
```

**If anything fails, run `python check_env.py` first.** It names the problem
directly — wrong Python, missing venv, missing package, or missing data file.

On macOS / Linux: `source .venv/bin/activate` and `cp` instead.

---

## 2. Read the explanations

Everything is in `docs/stages/`. Start with
**[docs/stages/README.md](docs/stages/README.md)** — it is the index and tells
you what order to read in.

Fifteen documents, one per stage. Each has the same seven sections: what it
does, input/output, how to run it, line-by-line code with Python syntax
explained, real output numbers, viva questions with answers, and common errors.

| Read | For |
|---|---|
| `docs/stages/00_setup_and_config.md` | VS Code, PowerShell, troubleshooting |
| `docs/stages/00b_cleaners.md` | The shared parsing toolbox |
| `docs/stages/01` … `12` | One document per pipeline stage |
| `docs/LOCAL_LLM_SETUP.md` | Ollama install and where the LLM plugs in |
| `docs/AWS_DEPLOYMENT.md` | S3, RDS, EC2, Lambda, SES, IAM |
| `scripts/aws/` | **Bash scripts that do the AWS setup for you** |
| `docs/CODE_WALKTHROUGH.md` | Condensed single-file version of the above |

Tip: open any `.md` in VS Code and press `Ctrl + Shift + V` for a formatted
preview.

---

## 3. What is in this folder

| Folder | Holds |
|---|---|
| `pipeline/` | The 11 numbered stages — the heart of the project |
| `config/settings.py` | Every path, alias and threshold, in one file |
| `data/raw/` | Where you put your 11 files (starts empty) |
| `data/interim/` | Half-cleaned tables (stages 01–02) |
| `data/processed/` | Model-ready tables (stage 03) |
| `artifacts/` | Trained `.pkl` models and `smartlogix.db` |
| `reports/` | Every metric, audit and score sheet |
| `sql/schema.sql` | Database table definitions |
| `api/main.py` | FastAPI endpoints |
| `app/dashboard.py` | Streamlit dashboard |
| `agents/` | The five AI agents |
| `rag/` | Chatbot retrieval + local LLM client |
| `cv/` | YOLO dataset config and annotation guide |
| `lambda/` | AWS notification function |
| `docs/` | All documentation |

`data/` and `artifacts/` ship empty on purpose — everything regenerates when you
run the pipeline.

---

## 4. Running individual stages

```powershell
python run_all.py                 # everything, in order
python run_all.py --only 02       # just stage 02
python run_all.py --from 05       # stage 05 onwards
python -m pipeline.p02_clean      # one stage, cleanest error messages
```

Use `-m` with dots and no `.py`. Running `python pipeline\p02_clean.py` fails
with `ModuleNotFoundError: No module named 'config'`.

---

## 5. The demo

```powershell
uvicorn api.main:app --reload      # then open http://127.0.0.1:8000/docs
streamlit run app/dashboard.py     # opens on port 8501
```

---

## 6. Results against the PDF targets

| Model | Achieved | PDF target |
|---|---|---|
| Mode classifier | accuracy 0.955, macro-F1 0.927 | ≥ 0.88 |
| ETA regressor | R² 0.992, MAPE 7.44% | ≥ 0.85, ≤ 12% |
| Predictive maintenance | recall 0.901, false alarms 0.98% | ≥ 0.90, ≤ 10% |
| Route optimisation | 81.3% distance reduction | ≥ 12% |

**Two caveats stated openly**, both explained in the relevant stage doc:

- The 15-minute ETA target is met per mode by bike (13.3 min) and drone
  (13.3 min). It cannot hold as one global figure across a 20-minute drone hop
  and a 3-day sea leg, so the per-mode table is reported instead.
- The sentiment model scores 100% because the review corpus has only 303 unique
  texts across 11,200 rows. Stage 10 detects this and warns. Raise it yourself.

**Stage 09 (YOLO) needs images you supply** — your uploads contain drone sensor
telemetry, not photographs. See `docs/stages/09_yolo.md`.

---

## 7. The four answers to memorise

1. **Leakage** — Stage 05 excludes outcome columns and asserts the build fails
   if one appears. `transport_mode` is banned there but allowed in Stage 06,
   because by then the mode is already chosen. The test is *when does this value
   exist*, not *is it in the table*.
2. **Sentiment duplication** — 97.3% of review texts are repeats of 303
   templates. Say it before you are asked.
3. **SQL vs vectors** — no orders are in the vector store, because semantic
   search would return ORD-00126 when asked about ORD-00125.
4. **Route baseline** — 81.3% is measured against first-come-first-served
   dispatch. State the baseline before quoting the number.

---

## 8. AWS from the terminal

Six scripts in `scripts/aws/` do the whole free-tier deployment. Run in order;
each asks before creating anything billable.

```bash
cd scripts/aws
./00_preflight.sh    # checks only, creates nothing
./01_s3.sh           # bucket + models        ~2 min
./02_rds.sh          # PostgreSQL + load      ~12 min
./03_ec2.sh          # instance + swap        ~3 min
./04_lambda_ses.sh   # notifications + email  ~3 min
./99_teardown.sh     # when you are finished
```

Use Git Bash or WSL on Windows. See `scripts/aws/README.md` for prerequisites.
