# 💬 Chat-to-SQL (with DuckDB and AutoGen)

This is a Streamlit-based app that allows users to query `.parquet` datasets using natural language. It leverages LLMs (e.g., GPT-4o-mini) via Microsoft AutoGen to generate, validate, and execute SQL queries in DuckDB.

---

## 🚀 Features

- Natural language chat interface powered by Streamlit
- Automatic NL → SQL generation using LLMs
- Security validation of SQL statements before execution
- In-memory SQL execution via DuckDB (no external database required)
- Markdown-formatted result tables for clean display
- Modular multi-agent architecture:
  - `nl2sql_agent`: generates SQL from user input
  - `guard_agent`: validates SQL for safety
  - DuckDB executor: runs the query if approved

---

## 📦 Requirements

- Python ≥ 3.9
- A valid OpenAI API key (`OPENAI_API_KEY`)
- Docker **not required**

---

## 🧪 Getting Started

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-user/chat-to-sql.git
   cd chat-to-sql
