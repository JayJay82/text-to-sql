"""Streamlit page: Model Comparison
Add this file to `pages/` to get a new tab in the sidebar.
"""

import os
import altair as alt
import pandas as pd
import streamlit as st
from data.logger import validation_results

################################################################################
# Config & Data
################################################################################
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = "Text_to_sql"
COLL = "validation_results"


col = validation_results

df_raw = pd.DataFrame(col.find())
if df_raw.empty:
    st.warning("La collection validation_results è vuota. Esegui gli script di benchmark prima di aprire questa pagina.")
    st.stop()

################################################################################
# Page layout
################################################################################
st.set_page_config(page_title="Model Metrics", layout="wide")
st.title("📊 Model Comparison")

# ---------- aggregated summary ----------
summary = (
    df_raw.groupby("model", as_index=False)
          .agg(
              accuracy=("match", "mean"),
              avg_gen_ms=("gen_ms", "mean"),
              p95_gen_ms=("gen_ms", lambda x: x.quantile(0.95)),
              avg_exec_ms=("exec_ms", "mean"),
              p95_exec_ms=("exec_ms", lambda x: x.quantile(0.95)),
              n=("match", "size"),
          )
          .sort_values("accuracy", ascending=False)
)

################################################################################
# Tabs
################################################################################

tab1, tab2, tab3, tab4 = st.tabs(["📋 Summary", "🎻 Latency", "🟩 Heat‑map", "⚖️ Trade‑off"])

# ----------------------------------------------------------------------------
with tab1:
    st.subheader("Metrics summary per model")
    st.dataframe(summary, hide_index=True)

    st.markdown("### Accuracy")
    st.bar_chart(summary.set_index("model")["accuracy"])

    st.markdown("### Average latencies (ms)")
    st.bar_chart(summary.set_index("model")[["avg_gen_ms", "avg_exec_ms"]])

# ----------------------------------------------------------------------------
with tab2:
    st.subheader("Latency distribution (Violin plot)")

    vdata = df_raw.melt(id_vars=["model"], value_vars=["gen_ms", "exec_ms"],
                        var_name="phase", value_name="ms")

    violin = (
        alt.Chart(vdata)
        .transform_density("ms", as_=["ms", "density"], groupby=["model", "phase"])
        .mark_area(opacity=0.5)
        .encode(
            y=alt.Y("ms:Q", title="latency (ms)"),
            x=alt.X("density:Q", stack="center"),
            color="model:N",
            column="phase:N",
            tooltip=["model", "phase", "ms"]
        )
        .properties(width=200, height=200)
    )
    st.altair_chart(violin, use_container_width=True)

# ----------------------------------------------------------------------------
with tab3:
    st.subheader("Accuracy per question / model")

    # pivot → long format (question, model, acc)
    heat_long = (
        df_raw.assign(acc=df_raw["match"].astype(int))
              .pivot_table(index="question", columns="model", values="acc", aggfunc="mean")
              .reset_index()
              .melt(id_vars="question", var_name="model", value_name="acc")
    )

    heat = (
        alt.Chart(heat_long)
        .mark_rect()
        .encode(
            x=alt.X("model:N", title="model"),
            y=alt.Y("question:N", title="question"),
            color=alt.Color("acc:Q", title="accuracy", scale=alt.Scale(domain=[0,1], range=["#ec7063", "#27ae60"])),
            tooltip=["question", "model", alt.Tooltip("acc:Q", format=".2f")]
        )
        .properties(height=400)
    )
    st.altair_chart(heat, use_container_width=True)

# ----------------------------------------------------------------------------
with tab4:
    st.subheader("Speed vs Accuracy trade‑off")

    scatter = (
        alt.Chart(summary)
        .mark_circle(size=200)
        .encode(
            x=alt.X("avg_gen_ms:Q", title="Avg generation latency (ms)"),
            y=alt.Y("accuracy:Q", title="Accuracy"),
            size=alt.Size("avg_exec_ms:Q", title="Avg exec latency (ms)"),
            color="model:N",
            tooltip=["model", alt.Tooltip("accuracy:Q", format=".2f"), "avg_gen_ms", "avg_exec_ms", "n"]
        )
    )
    st.altair_chart(scatter, use_container_width=True)
