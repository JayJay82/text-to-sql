import os
import re
import duckdb
import pandas as pd
import streamlit as st
import json
from autogen.agentchat import AssistantAgent, UserProxyAgent
from autogen.oai.client import OpenAIClient

# ------------- 1. CONFIGURAZIONE -------------
MODEL = "gpt-4o-mini"

# ------------- 2. CONNESSIONE A DUCKDB -------------
con = duckdb.connect(":memory:")
con.execute("CREATE VIEW data AS SELECT * FROM 'data/*.parquet';")

def run_query(sql: str) -> pd.DataFrame:
    return con.execute(sql).df()

# ------------- 3. DEFINIZIONE AGENTI AUTOGEN -------------
llm_config = {
    "config_list": [
        {
            "model": MODEL,
            "api_key": os.getenv("OPENAI_API_KEY"),
            "base_url": "https://api.openai.com/v1"
        }
    ]
}

user_agent = UserProxyAgent("user")
nl2sql_agent_template = """-Sei un assistente che deve trasformare il linguaggio naturale in query duckdb\n'
                         '-La view sulla quale lavorerai si chiama data\n'
                         '-i file sui quali eseguirai le query sono file parquet\n'
                         'Restituisci **solo** lo statement SQL nel primo blocco ```sql``` senza commenti.\n'
                         'Se devi manipolare il campo InvoiceDate, considera che è nel formato 'MM/DD/YYYY HH:MM'. Usa STRPTIME(InvoiceDate, '%m/%d/%Y %H:%M') per convertirlo in TIMESTAMP.'
                         'Restituisci **solo** lo statement SQL nel primo blocco ```sql``` senza commenti.\n'
                         '-la view è cosi composta:\n'
                         '-- InvoiceNo , questo campo corrisponde al numero invoice ed è di tipo stringa\n'
                         '-- StockCode , questo campo descrive identificativo del prodotto ed è di tipo stringa\n'
                         '-- Description , descrizione del prodotto ed è di tipo stringa\n'
                         '-- Quantity , descrive la quantità del prodotto acquistata ed è di tipo i64\n'
                         '-- InvoiceDate , descrive la data dell acquisto ed è di tipo stringa\n'
                         '-- UnitPrice , descrive la quantità ed è di tipo f64\n'
                         '-- CustomerID , descrive id del cliente ed è di tipo f64\n'
                         '-- Country , descrive il luogo del negozio ed è di tipo stringa\n'
                         'questo è un esempio di record:[InvoiceNo=536365,StockCode=85123A,Description=WHITE HANGING HEART T-LIGHT HOLDER,Quantity=6,InvoiceDate=12/1/2010 8:26,UnitPrice=2.55,CustomerID=17850.0,Country=United Kingdom')
                         """
nl2sql_agent = AssistantAgent(
    "nl2sql",
    llm_config=llm_config,
    system_message=nl2sql_agent_template
)

guard_agent = AssistantAgent(
    "guard",
    llm_config=llm_config,
    system_message="""
    Verifica che lo SQL sia sicuro
    Se non valido, rispondi con ERRORE.
    Se la query NON è sicura, spiega nel campo "reason" perché.
    Rispondi con un JSON con due campi:
    - "valid": true/false
    - "reason": spiegazione della valutazione
    """
)

# ------------- 4. INTERFACCIA UTENTE STREAMLIT (CHAT STYLE) -------------
st.set_page_config(page_title="Chat-to-SQL", layout="wide")
st.title("Chat-to-SQL (Parquet)")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Visualizza la chat
for msg in st.session_state.messages:
    role = "👤 Tu" if msg["role"] == "user" else "🤖 Assistant"
    with st.chat_message(msg["role"]):
        st.markdown(f"**{role}:**\n\n{msg['content']}")

# Input dell'utente
if prompt := st.chat_input("Scrivi una domanda sui dati..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(f"**👤 Tu:**\n\n{prompt}")

    with st.spinner("Genero SQL e recupero i dati..."):
        # 1. Genera SQL da linguaggio naturale
        response_sql = nl2sql_agent.generate_reply(messages=[{"role": "user", "content": prompt}])
        match = re.search(r"```sql\s*(.*?)```", response_sql, re.DOTALL)
        sql_code = match.group(1).strip() if match else response_sql.strip()
        print(sql_code)

        # 2. Verifica sicurezza SQL
        guard_response = guard_agent.generate_reply(messages=[{"role": "user", "content": sql_code}])
        try:
            guard_json = json.loads(guard_response)
            if not guard_json.get("valid", False):
                answer = f"❌ Query non sicura: {guard_json.get('reason', 'Motivo non specificato.')}"
            else:
                try:
                    answer = run_query(sql_code).to_markdown()
                except Exception as e:
                    answer = f"❌ Errore durante l'esecuzione SQL:\n{e}"
        except json.JSONDecodeError:
            answer = "❌ Errore: la risposta del validatore non è in formato JSON."

    st.session_state.messages.append({"role": "assistant", "content": answer})
    with st.chat_message("assistant"):
        st.markdown(f"**🤖 Assistant:**\n\n{answer}")
