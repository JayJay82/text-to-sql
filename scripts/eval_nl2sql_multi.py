#!/usr/bin/env python
import argparse, time, re, sys
import numpy as np, pandas as pd
from autogen import AssistantAgent

from data.logger import validation, validation_results
from data.db import run_query
from utils.sql_extract import extract_sql           # tua funzione
from utils.eval_helpers import compare_dfs                # confronto DataFrame
from agents.agents import nl2sql_agent_template     # stesso prompt
from config import OPENAI_API_KEY                   # stessa chiave

# ----------------------------------------------------------------------
def build_agent(model_name: str) -> AssistantAgent:
    """Costruisce un nl2sql_agent con il modello indicato."""
    llm_config = {
        "config_list": [{
            "model": model_name,
            "api_key": OPENAI_API_KEY,
            "base_url": "https://api.openai.com/v1"
        }]
    }
    return AssistantAgent(
        name=f"nl2sql_{model_name}",
        llm_config=llm_config,
        system_message=nl2sql_agent_template
    )

# ----------------------------------------------------------------------
def bench(model, docs, verbose=False):
    agent = build_agent(model)
    rows, ok = [], 0

    for d in docs:
        q, gold = d["question"], d["sql"]

        t0 = time.perf_counter()
        reply = agent.generate_reply([{"role": "user", "content": q}])
        gen_ms = round((time.perf_counter() - t0) * 1000)

        pred_sql = extract_sql(reply)

        exec_ms, df_pred = None, None
        try:
            t1 = time.perf_counter()
            df_pred = run_query(pred_sql)
            exec_ms = round((time.perf_counter() - t1) * 1000)
        except Exception as e:
            if verbose:
                print(f"[{model}] exec error:", e)

        df_gold = run_query(gold)
        match = df_pred is not None and compare_dfs(df_pred, df_gold)
        ok += int(match)

        rows.append({
            "model": model,
            "question": q,
            "pred_sql": pred_sql,
            "match": match,
            "gen_ms": gen_ms,
            "exec_ms": exec_ms
        })

    acc = ok / len(docs)
    print(f"→ {model}: {ok}/{len(docs)} = {acc:.2%}")
    return rows
# ----------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", default="gpt-3.5-turbo,gpt-4o-mini",
                    help="Modelli separati da virgola")
    ap.add_argument("--store-results", action="store_true")
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()

    docs = list(validation.find())
    if not docs:
        print("validation collection vuota", file=sys.stderr); sys.exit(1)

    all_rows = []
    for m in [s.strip() for s in args.models.split(",") if s.strip()]:
        all_rows.extend(bench(m, docs, verbose=args.verbose))

    if args.store_results:
        validation_results.insert_many(all_rows)
        print("Salvati", len(all_rows), "record in validation_results")

if __name__ == "__main__":
    main()
