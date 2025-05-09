import streamlit as st
import pandas as pd
from data.logger import logs as logs_collection

st.set_page_config(page_title="Chat Logs", layout="wide")
st.title("Chat Interaction Logs")

# Fetch all logs as a list of dicts and convert to DataFrame
try:
    cursor = logs_collection.find().sort("timestamp", -1)
    logs = list(cursor)
    if logs:
        # Use from_records for proper handling of list of dicts
        df_logs = pd.DataFrame.from_records(logs)
        # Convert ObjectId and datetime for display
        df_logs["_id"] = df_logs["_id"].astype(str)
        df_logs["timestamp"] = pd.to_datetime(df_logs["timestamp"])
        st.dataframe(df_logs)
    else:
        st.info("No logs found.")
except Exception as e:
    st.error(f"Error fetching logs: {e}")