#!/usr/bin/env python
"""
Valuta la capacità di nl2sql_agent di rendere correttamente le 20 query
presenti in Text_to_sql.validation.  Stampa accuracy e salva i dettagli
in Mongo (collection validation_results).
"""
import re, argparse, sys             # per eventuali check output
from agents.agents import nl2sql_agent
from data.logger import validation, validation_results # se hai già helper, altrimenti usa MongoClient
from data.db import  run_query
import numpy as np, pandas as pd
import sqlparse


def extract_sql(text: str) -> str:
    """
    Restituisce la query nuda, senza back-tick e
    senza eventuale keyword 'sql' di prefisso.
    """
    # 1️⃣  Blocco ```sql ... ```
    m = re.search(r"```(?:\s*sql)?\s*([\s\S]*?)```", text, flags=re.I)
    if m:
        return m.group(1).strip()

    # 2️⃣  Stringa che inizia con 'sql '
    stripped = text.strip()
    if stripped.lower().startswith("sql"):
        return stripped[3:].lstrip()   # rimuove i primi 3 caratteri 'sql'

    # 3️⃣  Già pulita
    return stripped

def canonical(sql: str) -> str:
    """Normalizza spazi, case, ; finale."""
    return sqlparse.format(sql, keyword_case="lower", identifier_case="lower",
                           strip_comments=True, reindent=False).strip().rstrip(";")

def same_result(sql_a: str, sql_b: str) -> bool:
    """
    Confronta i risultati di due query.
    Se una delle due va in errore → match = False.
    Il confronto ignora nomi colonna.
    """
    try:
        df_a = run_query(sql_a).reset_index(drop=True)
        df_b = run_query(sql_b).reset_index(drop=True)
    except Exception as e:
        # qualsiasi errore di esecuzione ⇒ risposta considerata errata
        return False

    if df_a.shape != df_b.shape:
        return False

    # ordina righe per stabilità (se possibile)
    try:
        df_a = df_a.sort_values(list(df_a.columns)).reset_index(drop=True)
        df_b = df_b.sort_values(list(df_b.columns)).reset_index(drop=True)
    except Exception:
        pass

    n_cols = df_a.shape[1]
    for i in range(n_cols):
        col_a = df_a.iloc[:, i]
        col_b = df_b.iloc[:, i]
        if pd.api.types.is_numeric_dtype(col_a) and pd.api.types.is_numeric_dtype(col_b):
            if not np.allclose(col_a.astype(float),
                               col_b.astype(float),
                               equal_nan=True):
                return False
        else:
            if not col_a.astype(str).equals(col_b.astype(str)):
                return False
    return True




def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--store-results", action="store_true",
                    help="Persisti outcome in validation_results")
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()
    val_col = validation
    res_col = validation_results

    docs = list(val_col.find())   # 20 docs
    if not docs:
        print("Collection validation vuota!", file=sys.stderr)
        sys.exit(1)

    total = len(docs)
    ok = 0
    results = []

    for i, doc in enumerate(docs, 1):
        q, gold_sql = doc["question"], doc["sql"]
        # 1. chiedi al modello
        ai_reply = nl2sql_agent.generate_reply([{"role": "user", "content": q}])
        pred_sql_raw = extract_sql(ai_reply)
        pred_sql = canonical(pred_sql_raw)
        gold_sql_norm = canonical(gold_sql)

        is_match = same_result(pred_sql_raw, gold_sql)
        if is_match:
            ok += 1

        if args.verbose or not is_match:
            print(f"--- #{i} {'✓' if is_match else '✗'}")
            print("Q :", q)
            if not is_match:
                print("GT:", gold_sql_norm)
                print("AI:", pred_sql, "\n")

        results.append({
            "question": q,
            "gold_sql": gold_sql,
            "pred_sql": pred_sql_raw,
            "match": is_match
        })

    accuracy = ok / total
    print(f"Accuracy: {ok}/{total} = {accuracy:.2%}")

    if args.store_results:
        res_col.delete_many({})
        res_col.insert_many(results)
        print("Dettagli salvati in Text_to_sql.validation_results")

if __name__ == "__main__":
    main()
