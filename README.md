# 💬 Chat-to-SQL (DuckDB + AutoGen + Visualization)

Natural-language questions ➜ **DuckDB SQL** ➜ instant answers & charts.
This Streamlit application uses a multi-agent AutoGen pipeline to translate plain-English queries into safe SQL, executes them in-memory on Parquet files, visualises results, and logs every interaction to MongoDB.

---

## 🚀 Key Features

* **Chat interface** – ask in English or Italian, get answers and charts.
* **LLM NL→SQL conversion** – `nl2sql_agent` generates DuckDB-compatible SQL.
* **SQL guard** – validates that queries are read-only and auto-limit ≤ 200 rows.
* **Zero-setup analytics** – DuckDB mounts all `.parquet` files as the view `data`.
* **Auto-visualisation** – `chart_selector_agent` suggests BAR / LINE / SCATTER / TABLE.
* **Observability** – MongoDB stores prompts, SQL, markdown results, latency.
* **Multi-page UI** – Query • Visualizer • Logs • Metrics dashboards.

---

## 📁 Project Structure

```
text_to_sql/
├── app.py                 # Streamlit entry-point
├── agents/                # nl2sql, guard, chart_selector (AutoGen)
├── data/
│   ├── db.py              # DuckDB connection + view `data`
│   └── logger.py          # Mongo client, log & validation helpers
├── pages/                 # extra Streamlit pages (viz, logs, metrics)
├── scripts/
│   └── generate_validation_set.py  # seed 20 Q&A pairs into Mongo
├── config.py              # global settings (OpenAI model, paths)
└── requirements.txt       # Python deps
```

---

## 🧩 Installation & Setup

```bash
# 1 – clone & enter
$ git clone https://github.com/your-user/chat-to-sql.git
$ cd chat-to-sql

# 2 – create virtualenv & install deps
$ python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
$ pip install -r requirements.txt

# 3 – environment
$ cp .env.example .env      # edit OPENAI_API_KEY, MONGO_URI, DATA_PARQUET

# 4 – run Streamlit
$ streamlit run app.py      # http://localhost:8501
```

> **MongoDB** must be reachable at `MONGO_URI`.
> On first launch DuckDB creates the view **`data`** over the Parquet file defined in `DATA_PARQUET`.

---

## ✅ Validation-set (20 domande / SQL)

Genera e semina nel database le coppie domanda→query per i test automatizzati:

```bash
# verifica che le query girino su DuckDB e poi inseriscile in Text_to_sql.validation
$ python -m scripts.generate_validation_set

# skip della verifica (più veloce)
$ python -m scripts.generate_validation_set --skip-check
```

La collection risultante è `Text_to_sql.validation`.

---

## 🐞 Debug con PyCharm

1. **Run ▶ Edit Configurations…** → **+ Python**.
2. Imposta:

   * **Name:** `generate_validation_set`
   * **Module name:** `scripts.generate_validation_set`
   * **Parameters:** *(opz.)* `--skip-check`
   * **Working directory:** `$ProjectFileDir$`
3. (Facolt.) in **Environment variables** aggiungi `MONGO_URI` e l’eventuale `OPENAI_API_KEY` se non usi `.env`.
4. Assicurati che “Add content/source roots to PYTHONPATH” sia spuntato.
5. **Apply → OK**, poi ▶ Run o 🐞 Debug.

Con “Module name” PyCharm lancia `python -m scripts.generate_validation_set`, includendo la root del progetto nel `sys.path`, quindi gli import `from data...` funzionano senza hack.

### Debug Streamlit

Crea una seconda configurazione:

| Campo           | Valore                   |
| --------------- | ------------------------ |
| **Module name** | `streamlit.cli.main_run` |
| **Parameters**  | `app.py`                 |
| **Working dir** | `$ProjectFileDir$`       |

Esegui in debug per mettere breakpoint dentro agenti, DuckDB, ecc.

---

## 📋 Dependencies

* `streamlit`  •  `duckdb`  •  `pandas`  •  `openai>=1.22`  •  `autogen`
* `pymongo`  •  `tabulate`  •  *(dev)* `pytest` • `ruff`

---

## 🛠️ Usage

* **Query** – chat-to-SQL, risposte tabellari.
* **Visualizer** – chat-to-chart con suggerimento tipo grafico.
* **Logs** – cronologia completa con prompt, SQL, durata, successo/fallimento.
* **Metrics** – dashb
