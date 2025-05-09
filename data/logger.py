from pymongo import MongoClient
from datetime import datetime

# Inizializza il client una volta sola
client = MongoClient("mongodb://localhost:27017")
db = client["Text_to_sql"]
logs = db["logs"]

def log_interaction(prompt: str,
                    sql: str,
                    result_md: str,
                    exec_time_ms: int):
    """
    Inserisce un documento di log:
      - timestamp UTC
      - prompt utente
      - SQL generato
      - risultato in Markdown
      - tempo di esecuzione in ms
    """
    logs.insert_one({
        "timestamp": datetime.utcnow(),
        "user_prompt": prompt,
        "generated_sql": sql,
        "execution_result": result_md,
        "execution_time_ms": exec_time_ms
    })