import re
import json
import streamlit as st
import pandas as pd
from data.db import run_query
from agents.agents import nl2sql_agent, guard_agent, chart_selector_agent

st.set_page_config(page_title="Visualizer", layout="wide")
st.title("Chat-to-SQL Visualizer")

if "history_viz" not in st.session_state:
    st.session_state.history_viz = []

for msg in st.session_state.history_viz:
    with st.chat_message(msg['role']):
        st.markdown(f"**{msg['label']}** {msg['content']}")

if prompt := st.chat_input("Ask a question for visualization..."):
    st.session_state.history_viz.append({"role":"user","label":"👤 You:","content":prompt})
    with st.chat_message("user"):
        st.markdown(f"**👤 You:** {prompt}")

    with st.spinner("Generating chart..."):
        # SQL gen & guard as before
        response_sql = nl2sql_agent.generate_reply(messages=[{"role":"user","content":prompt}])
        m = re.search(r"```(?:sql)?\s*(.*?)```", response_sql, re.DOTALL)
        sql_code = m.group(1).strip() if m else response_sql.strip()

        resp_guard = guard_agent.generate_reply(messages=[{"role":"user","content":sql_code}])
        mj = re.search(r"```json\s*(\{.*?\})\s*```", resp_guard, re.DOTALL)
        guard_text = mj.group(1) if mj else resp_guard
        guard_json = json.loads(guard_text) if guard_text else {"valid":False}

        if not guard_json.get("valid",False):
            chart = None; label_message = f"❌ Query not safe: {guard_json.get('reason')}"
        else:
            df = run_query(sql_code)
            # Build schema metadata
            schema = []
            for col in df.columns:
                dtype = str(df[col].dtype)
                schema.append({"name":col,"dtype":dtype})
            meta = json.dumps({"columns":schema,"n_rows":len(df)})
            # Chart recommendation
            rec = chart_selector_agent.generate_reply(messages=[{"role":"user","content":meta}])
            rec_json = json.loads(rec)
            ctype = rec_json.get("chart_type")
            x = rec_json.get("x"); y = rec_json.get("y")
            # Render chart
            if ctype=="BAR":
                chart = st.bar_chart(df.set_index(x)[y])
                label_message = f"Bar chart of {y} by {x}"
            elif ctype=="LINE":
                df[x] = pd.to_datetime(df[x])
                df_sorted = df.sort_values(x)
                chart = st.line_chart(df_sorted.set_index(x)[y])
                label_message = f"Line chart of {y} over {x}"
            elif ctype=="SCATTER":
                import matplotlib.pyplot as plt
                fig, ax = plt.subplots()
                ax.scatter(df[x],df[y])
                ax.set_xlabel(x); ax.set_ylabel(y)
                st.pyplot(fig)
                chart = "scatter"
                label_message = f"Scatter plot of {y} vs {x}"
            else:
                st.dataframe(df)
                chart = None; label_message = "Table view"

    st.session_state.history_viz.append({"role":"assistant","label":"📊 VizBot:","content":label_message})
    with st.chat_message("assistant"):
        st.markdown(label_message)
        if chart is not None:
            pass  # chart already rendered