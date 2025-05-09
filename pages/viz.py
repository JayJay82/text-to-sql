import re
import json
import time
import streamlit as st
import pandas as pd
from data.db import run_query
from agents.agents import nl2sql_agent, guard_agent, chart_selector_agent
from data.logger import log_interaction

# Page configuration
st.set_page_config(page_title="Visualizer", layout="wide")
st.title("Chat-to-SQL Visualizer")

# Chat history in session
if "history_viz" not in st.session_state:
    st.session_state.history_viz = []

for msg in st.session_state.history_viz:
    with st.chat_message(msg["role"]):
        st.markdown(f"**{msg['label']}** {msg['content']}")

if prompt := st.chat_input("Ask a question for visualization..."):
    st.session_state.history_viz.append({"role":"user","label":"👤 You:","content":prompt})
    with st.chat_message("user"):
        st.markdown(f"**👤 You:** {prompt}")

    with st.spinner("Generating visualization..."):
        # 1. Generate SQL
        response_sql = nl2sql_agent.generate_reply(messages=[{"role":"user","content":prompt}])
        m = re.search(r"```(?:sql)?\s*(.*?)```", response_sql, re.DOTALL)
        sql_code = m.group(1).strip() if m else response_sql.strip()

        # 2. Validate SQL
        resp_guard = guard_agent.generate_reply(messages=[{"role":"user","content":sql_code}])
        mj = re.search(r"```json\s*(\{.*?\})\s*```", resp_guard, re.DOTALL)
        guard_text = mj.group(1) if mj else resp_guard
        try:
            guard_json = json.loads(guard_text)
        except json.JSONDecodeError:
            guard_json = {"valid": False, "reason": "Invalid guard response."}

        # Defaults
        df = None
        exec_time = None
        chart_rendered = False
        label_message = None

        if not guard_json.get("valid", False):
            label_message = f"❌ Query not safe: {guard_json.get('reason')}"
        else:
            # 3. Execute and time
            start = time.time()
            try:
                df = run_query(sql_code)
            except Exception as e:
                label_message = f"❌ Error executing SQL: {e}"
            finally:
                exec_time = int((time.time() - start) * 1000)

            # 4. Chart recommendation
            if df is not None:
                schema = [{"name": c, "dtype": str(df[c].dtype)} for c in df.columns]
                meta = json.dumps({"columns": schema, "n_rows": len(df)})
                rec = chart_selector_agent.generate_reply(messages=[{"role":"user","content":meta}])
                rec_json = json.loads(rec)
                ctype = rec_json.get("chart_type")
                x = rec_json.get("x"); y = rec_json.get("y")

                if ctype == "BAR" and x in df.columns and y in df.columns:
                    st.bar_chart(df.set_index(x)[y])
                    label_message = f"Bar chart of {y} by {x}"
                    chart_rendered = True
                elif ctype == "LINE" and x in df.columns and y in df.columns:
                    df[x] = pd.to_datetime(df[x])
                    st.line_chart(df.sort_values(x).set_index(x)[y])
                    label_message = f"Line chart of {y} over {x}"
                    chart_rendered = True
                elif ctype == "SCATTER" and x in df.columns and y in df.columns:
                    import matplotlib.pyplot as plt
                    fig, ax = plt.subplots()
                    ax.scatter(df[x], df[y])
                    ax.set_xlabel(x); ax.set_ylabel(y)
                    st.pyplot(fig)
                    label_message = f"Scatter plot of {y} vs {x}"
                    chart_rendered = True
                else:
                    st.dataframe(df)
                    label_message = "Table view"
                    chart_rendered = True

        # 5. Log to MongoDB
        result_md = df.to_markdown() if df is not None else ""
        log_interaction(prompt, sql_code, result_md, exec_time)

    # Show VizBot response
    st.session_state.history_viz.append({
        "role":"assistant",
        "label":"📊 VizBot:",
        "content": label_message or "No visualization generated."
    })
    with st.chat_message("assistant"):
        st.markdown(label_message or "No visualization generated.")
        # chart already rendered above if chart_rendered is True
