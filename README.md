# 💬 Chat-to-SQL (DuckDB + AutoGen + Visualization)

This Streamlit application allows querying Parquet data using natural language, converting questions to SQL with an LLM-based AutoGen pipeline, validating queries for safety, executing them on DuckDB, and visualizing results automatically or via recommended chart types. All interactions are logged to MongoDB.

---

## 🚀 Key Features

* **Natural Language Chat Interface**: Ask questions in plain English.
* **NL → SQL Conversion**: `nl2sql_agent` translates prompts to valid DuckDB SQL.
* **SQL Safety Validation**: `guard_agent` checks for only `SELECT`, `LIMIT ≤ 200`, no destructive clauses.
* **In-Memory Execution**: DuckDB loads all `.parquet` files as the `data` view.
* **Logging**: Every prompt, generated SQL, result in Markdown, and execution time are stored in MongoDB.
* **Multi-Page UI**:

  * **Query**: Standard chat-to-SQL with table output.
  * **Visualizer**: `chart_selector_agent` recommends the best chart (BAR, LINE, SCATTER, TABLE) based on data schema.
  * **Logs**: Browse all logged interactions in a table.
  * **Metrics**: Dashboard showing execution-time metrics, success rates, query volume over time, and top prompts.

---

## 📁 Project Structure

```
text_to_sql/
├── app.py                 # Main chat-to-SQL interface
├── db.py                  # DuckDB connection & `run_query`
├── agents.py              # AutoGen agents: nl2sql, guard, chart_selector
├── logger.py              # MongoDB logging utility
├── pages/
│   ├── viz.py             # Visualization page with LLM-driven chart choice
│   ├── logs.py            # Browse interaction logs from MongoDB
│   └── metrics.py         # Execution-time & usage metrics dashboard
└── requirements.txt       # Python dependencies
```

---

## 🧩 Installation & Setup

1. **Clone repository**

   ```bash
   git clone https://github.com/your-user/chat-to-sql.git
   cd chat-to-sql
   ```

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Set environment variables**

   ```bash
   export OPENAI_API_KEY=sk-...
   ```

4. **Ensure MongoDB is running** on `mongodb://localhost:27017`.

5. **Start the app**

   ```bash
   streamlit run app.py
   ```

---

## 📋 Dependencies

* `streamlit`
* `duckdb`
* `pandas`
* `openai>=1.22`
* `autogen` (Microsoft AutoGen)
* `pymongo`
* `tabulate`

---

## 🛠️ Usage

* Navigate via the left sidebar:

  * **Query**: Chat-to-SQL and view results as a table.
  * **Visualizer**: Chat-to-chart interface, auto-rendered.
  * **Logs**: Inspect all past queries and execution details.
  * **Metrics**: View system health and usage statistics.

---

## 🧑‍💻 Author

**Costantino Cavallo**
Proof of Concept for Document Intelligence Services.
