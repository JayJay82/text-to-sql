# 💬 Chat-to-SQL (DuckDB + AutoGen + Visualization)

Ask in natural language → get SQL, tables & charts.
Multi‑agent AutoGen pipeline, in‑memory DuckDB on Parquet, Streamlit UI, Mongo‑backed observability.

---

## 🚀 Key Features

* **Chat interface** (EN/IT) → LLM generates SQL, guard enforces read‑only, results shown.
* **Auto‑Charts** – a second agent suggests BAR / LINE / SCATTER / TABLE.
* **Zero‑setup analytics** – DuckDB mounts all `.parquet` files as view **`data`**.
* **Observability** – every prompt/SQL/result/latency stored in MongoDB.
* **Validation & Benchmark suite** – 20 gold Q↔SQL pairs, accuracy + latency vs multiple OpenAI models.
* **Streamlit multi‑page UI** – Query • Visualizer • Logs • Metrics.

---

## 📁 Project Structure

````
text_to_sql/
├─ app.py                       # Streamlit entry‑point
├─ agents/                      # nl2sql, guard, chart selector
├─ data/
│  ├─ db.py                     # DuckDB connection + view `data`
│  └─ logger.py                 # Mongo clients: logs, validation sets
├─ scripts/
│  ├─ generate_validation_set.py   # seed 20 gold pairs
│  ├─ eval_nl2sql.py               # accuracy + timings (single model)
│  └─ eval_nl2sql_multi.py         # benchmark many models
├─ utils/
│  ├─ sql_extract.py            # strips ```sql … ``` wrappers
│  └─ eval_helpers.py           # compare_dfs (alias‑agnostic result match)
├─ pages/                       # viz, logs, metrics tabs
├─ config.py                    # settings (OpenAI key/model, paths)
└─ requirements.txt
````

---

## 🧩 Installation & Setup

```bash
# clone & enter
$ git clone https://github.com/your-user/chat-to-sql.git
$ cd chat-to-sql

# create & activate venv
$ python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate

# install deps
$ pip install -r requirements.txt

# copy env template & fill OPENAI_API_KEY, MONGO_URI, DATA_PARQUET
$ cp .env.example .env

# run Streamlit
$ streamlit run app.py   # http://localhost:8501
```

> DuckDB crea automaticamente la vista **`data`** sul Parquet indicato.

---

## ✅ Validation & Evaluation

### 1. Semina validation‑set (20 domande / SQL)

```bash
python -m scripts.generate_validation_set          # verifica + insert
python -m scripts.generate_validation_set --skip-check   # solo insert
```

Popola `Text_to_sql.validation`.

### 2. Valuta un singolo modello

```bash
python -m scripts.eval_nl2sql --verbose --store-results
```

* Accuracy, gen\_ms, exec\_ms salvati in `Text_to_sql.validation_results`.

### 3. Confronta più modelli OpenAI

```bash
python -m scripts.eval_nl2sql_multi \
       --models gpt-3.5-turbo,gpt-4o-mini,gpt-4o \
       --verbose --store-results
```

Risultati con campo `model` per KPI modell‑wise.

---

## 🐞 Debug & Run Configs (PyCharm)

### A. Generate validation set

| Field           | Value                             |
| --------------- | --------------------------------- |
| **Type**        | *Python*                          |
| **Module name** | `scripts.generate_validation_set` |
| **Parameters**  | *(opz.)* `--skip-check`           |
| **Working dir** | `$ProjectFileDir$`                |

### B. Benchmark multi‑model (eval\_script)

| Field           | Value                                                                              |
| --------------- | ---------------------------------------------------------------------------------- |
| **Module name** | `scripts.eval_nl2sql_multi`                                                        |
| **Parameters**  | `--models gpt-4o-mini,gpt-4o --verbose --store-results`                            |
| **Working dir** | `$ProjectFileDir$`                                                                 |
| **Env vars**    | `OPENAI_API_KEY=sk-…;MONGO_URI=mongodb://localhost:27017;AUTOGEN_USE_DOCKER=false` |

*(In PyCharm: Run ▶ Edit Configurations… → + Python → set **module** mode, paste the values above. Separate multiple env vars with semicolons.)*

### C. Streamlit live Debug Streamlit live Debug

| Field           | Value                    |
| --------------- | ------------------------ |
| **Module name** | `streamlit.cli.main_run` |
| **Parameters**  | `app.py`                 |
| **Working dir** | `$ProjectFileDir$`       |

---

## 📋 Dependencies (core)

`streamlit` • `duckdb` • `pandas` • `openai>=1.22` • `autogen` • `pymongo` • `sqlparse` • `numpy` • `tabulate`

---

## 🛠️ Usage walkthrough

1. **Query** – chat, tabella, SQL mostrata nei log.
2. **Visualizer** – chat‑to‑chart (automated chart type).
3. **Logs** – ricostruisci ogni turno, con SQL & durata.
4. **Metrics** – KPI di latenza, success‑rate, top query, accuracy per modello.

---

## 🧑‍💻 Author & License

**Costantino Cavallo**  — Proof‑of‑Concept for Document Intelligence Services.
MIT License.
