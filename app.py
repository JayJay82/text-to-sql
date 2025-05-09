import re
import json
import time
import streamlit as st

from data.db import run_query
from agents.agents import nl2sql_agent, guard_agent
from data.logger import log_interaction

st.set_page_config(page_title="Chat-to-SQL", layout="wide")
st.title("Chat-to-SQL (Parquet)")

# Chat history in session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display existing messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        label = "👤 You:" if msg["role"] == "user" else "🤖 Assistant:"
        st.markdown(f"**{label}** {msg['content']}")

# Handle new user input
if prompt := st.chat_input("Ask a question about the data..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(f"**👤 You:** {prompt}")

    with st.spinner("Generating SQL and executing..."):
        # 1. Generate SQL
        response_sql = nl2sql_agent.generate_reply(
            messages=[{"role": "user", "content": prompt}]
        )
        match_sql = re.search(r"```(?:sql)?\s*(.*?)```", response_sql, re.DOTALL)
        sql_code = match_sql.group(1).strip() if match_sql else response_sql.strip()

        # 2. Validate SQL
        guard_resp = guard_agent.generate_reply(
            messages=[{"role": "user", "content": sql_code}]
        )
        # Extract JSON from fenced code block if present
        match_json = re.search(r"```json\s*(\{.*?\})\s*```", guard_resp, re.DOTALL)
        guard_text = match_json.group(1) if match_json else guard_resp
        try:
            guard_json = json.loads(guard_text)
        except json.JSONDecodeError:
            guard_json = {"valid": False, "reason": "Invalid guard response format."}

        # Initialize defaults
        df = None
        exec_time = None
        error_msg = None

        if not guard_json.get("valid", False):
            error_msg = f"❌ Query not safe: {guard_json.get('reason')}"
        else:
            # 3. Execute and time the query
            start = time.time()
            try:
                df = run_query(sql_code)
            except Exception as e:
                error_msg = f"❌ Error executing SQL: {e}"
            finally:
                end = time.time()
                exec_time = int((end - start) * 1000)

        # 4. Log interaction
        result_md = df.to_markdown() if df is not None else ""
        log_interaction(prompt, sql_code, result_md, exec_time)

    # Display assistant response
    st.session_state.messages.append({"role": "assistant", "content": error_msg or "[Table displayed]"})
    with st.chat_message("assistant"):
        if error_msg:
            st.markdown(error_msg)
        else:
            st.dataframe(df)
            st.markdown(f"_Executed in {exec_time} ms_")
