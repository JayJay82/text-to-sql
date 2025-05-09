import streamlit as st
import pandas as pd
from data.logger import logs as logs_collection

# Page configuration
st.set_page_config(page_title="Metrics", layout="wide")
st.title("System Metrics Dashboard")

# Fetch logs into DataFrame
try:
    records = list(logs_collection.find())
    if not records:
        st.info("No logs available for metrics.")
    else:
        df = pd.DataFrame.from_records(records)
        df['timestamp'] = pd.to_datetime(df['timestamp'])

        # 1. Execution Time Metrics
        st.header("Execution Time Metrics")
        avg_time = df['execution_time_ms'].mean()
        median_time = df['execution_time_ms'].median()
        p90 = df['execution_time_ms'].quantile(0.9)
        st.metric("Average Execution Time (ms)", f"{avg_time:.2f}")
        st.metric("Median Execution Time (ms)", f"{median_time:.2f}")
        st.metric("90th Percentile Execution Time (ms)", f"{p90:.2f}")
        st.bar_chart(df['execution_time_ms'])

        # 2. Validation Success Rate
        st.header("Validation Success Rate")
        valid_counts = df['execution_time_ms'].notnull().sum()
        total = len(df)
        success_rate = df['execution_time_ms'].notnull().mean() * 100
        st.metric("Total Queries", total)
        st.metric("Successful Executions", valid_counts)
        st.metric("Success Rate (%)", f"{success_rate:.2f}")

        # 3. Queries per Day
        st.header("Queries Over Time")
        df['date'] = df['timestamp'].dt.date
        timeseries = df.groupby('date').size()
        st.line_chart(timeseries)

        # 4. Top User Prompts
        st.header("Top User Prompts")
        top_prompts = df['user_prompt'].value_counts().head(10)
        st.table(top_prompts)
except Exception as e:
    st.error(f"Error computing metrics: {e}")