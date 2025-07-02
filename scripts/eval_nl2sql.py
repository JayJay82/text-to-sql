#!/usr/bin/env python
"""
Valuta nl2sql_agent sulle 20 domande di Text_to_sql.validation.
Calcola accuracy, tempi di generazione/esecuzione e salva i dettagli
in Text_to_sql.validation_results (se --store-results).
"""

import re, argparse, sys, time

import numpy as np
import pandas as pd
import sqlparse
from agents.agents import nl2sql_agent
from data.logger import validation, validation_results
from data.db import run_query


# ---------- helper -----------------------------------------------------------
def extract_sql(text: str) -> str:
    """Rimuove back-tick e prefisso 'sql', restituisce solo la query."""
    m = re.search(r"```(?:\s*sql)?\s*([\s\S]*?)```", text, flags=re.I)
    if m:
        return m.group(1).strip()
    stripped = text.strip()
    return stripped[3:].lstrip() if stripped.lower().startswith("sql") else stripped


def canonical(sql: str) -> str:
    """Solo per stampa leggibile, non usata per il match."""
    return sqlparse.format(sql, keyword_case="lower",
                           identifier_case="lower",
                           strip_comments=True,
                           reindent=False).strip().rstrip(";")


def compare_dfs(df_a: pd.DataFrame, df_b: pd.DataFrame) -> bool:
    """True se i due DataFrame contengono gli stessi valori (ignora alias)."""
    if df_a.shape != df_b.shape:
        return False

    # ordina righe per stabilità
    try:
        df_a = df_a.sort_values(list(df_a.columns)).reset_index(drop=True)
        df_b = df_b.sort_values(list(df_b.columns)).reset_index(drop=True)
    except Exception:
        pass

    for i in range(df_a.shape[1]):
        col_a, col_b = df_a.iloc[:, i], df_b.iloc[:, i]
        if (pd.api.types.is_numeric_dtype(col_a) and
                pd.api.types.is_numeric_dtype(col_b)):
            if not np.allclose(col_a.astype(float),
                               col_b.astype(float),
                               equal_nan=True):
                return False
        else:
            if not col_a.astype(str).equals(col_b.astype(str)):
                return False
    return True
# -----------------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--store-results", action="store_true",
                        help="Salva i dettagli in validation_results")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    docs = list(validation.find())
    if not docs:
        print("Collection validation vuota!", file=sys.stderr)
        sys.exit(1)

    total, ok = len(docs), 0
    results_out = []

    for i, doc in enumerate(docs, 1):
        q, gold_sql = doc["question"], doc["sql"]

        # 1⃣  Generazione SQL + timing
        t0 = time.perf_counter()
        ai_reply = nl2sql_agent.generate_reply([{"role": "user", "content": q}])
        gen_ms = round((time.perf_counter() - t0) * 1000)

        pred_sql_raw = extract_sql(ai_reply)

        # 2⃣  Esecuzione SQL + timing
        exec_ms = None
        df_pred = None
        try:
            t1 = time.perf_counter()
            df_pred = run_query(pred_sql_raw)
            exec_ms = round((time.perf_counter() - t1) * 1000)
        except Exception as e:
            if args.verbose:
                print(f"--- #{i} ✗")
                print("Q :", q)
                print("❌ Errore esecuzione pred_sql:", e, "\n")

        # 3⃣  Esegui gold SQL
        df_gold = run_query(gold_sql)

        # 4⃣  Confronto risultati
        is_match = df_pred is not None and compare_dfs(df_pred, df_gold)
        if is_match:
            ok += 1

        if args.verbose:
            status = "✓" if is_match else "✗"
            print(f"--- #{i} {status}")
            print("Q :", q)
            if not is_match and df_pred is not None:
                print("GT:", canonical(gold_sql))
                print("AI:", canonical(pred_sql_raw), "\n")

        results_out.append({
            "question": q,
            "gold_sql": gold_sql,
            "pred_sql": pred_sql_raw,
            "match": is_match,
            "gen_ms": gen_ms,
            "exec_ms": exec_ms
        })

    accuracy = ok / total
    print(f"\nAccuracy: {ok}/{total} = {accuracy:.2%}")

    if args.store_results:
        validation_results.delete_many({})
        validation_results.insert_many(results_out)
        print("Dettagli salvati in Text_to_sql.validation_results")


if __name__ == "__main__":
    main()
