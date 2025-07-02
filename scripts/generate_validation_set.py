#!/usr/bin/env python
"""
Popola la collection `Text_to_sql.validation` con 20 coppie
{question, sql}.  Facoltativamente verifica che ogni query giri
su DuckDB contro il parquet indicato.

Uso:
    export MONGO_URI="mongodb://user:pass@localhost:27017"
    python scripts/generate_validation_set.py --parquet data/online_retail.parquet
"""

import os
import argparse
from data.db import con
from data.logger import validation

VALIDATION_PAIRS = [
    # 1
    ("Qual è il fatturato totale?",
     "SELECT SUM(Quantity * UnitPrice) AS total_revenue FROM data;"),

    # 2
    ("I 5 prodotti più venduti per quantità?",
     "SELECT Description, SUM(Quantity) AS total_qty "
     "FROM data GROUP BY Description "
     "ORDER BY total_qty DESC LIMIT 5;"),

    # 3
    ("Quanti clienti distinti ci sono?",
     "SELECT COUNT(DISTINCT CustomerID) AS num_customers FROM data;"),

    # 4
    ("I 10 paesi con più fatturato?",
     "SELECT Country, SUM(Quantity * UnitPrice) AS revenue "
     "FROM data GROUP BY Country "
     "ORDER BY revenue DESC LIMIT 10;"),

    # 5
    ("Prezzo medio del prodotto con StockCode = '85123A'?",
     "SELECT AVG(UnitPrice) AS avg_price "
     "FROM data WHERE StockCode = '85123A';"),

    # 6
    ("Quanti articoli sono stati venduti a dicembre 2010?",
     "SELECT SUM(Quantity) AS dec_items_sold "
     "FROM data WHERE InvoiceDate LIKE '12/%/2010%';"),

    # 7  – trend mensile (timestamp fix)
    ("Trend mensile del fatturato nel tempo",
     "SELECT strftime(strptime(InvoiceDate, '%m/%d/%Y %H:%M'), '%Y-%m') AS month, "
     "       SUM(Quantity * UnitPrice) AS revenue "
     "FROM data GROUP BY month ORDER BY month;"),

    # 8  – ultima fattura (timestamp fix)
    ("Data dell’ultima fattura presente",
     "SELECT MAX(strptime(InvoiceDate, '%m/%d/%Y %H:%M')) AS latest_invoice "
     "FROM data;"),

    # 9
    ("Numero medio di articoli per fattura",
     "SELECT AVG(items_per_invoice) AS avg_items "
     "FROM (SELECT InvoiceNo, SUM(Quantity) AS items_per_invoice "
     "      FROM data GROUP BY InvoiceNo);"),

    # 10
    ("Quale cliente ha speso di più?",
     "SELECT CustomerID, SUM(Quantity * UnitPrice) AS total_spent "
     "FROM data GROUP BY CustomerID "
     "ORDER BY total_spent DESC LIMIT 1;"),

    # 11 – righe fattura cliente (timestamp fix)
    ("Tutte le righe di fattura del cliente 17850",
     "SELECT * FROM data "
     "WHERE CustomerID = 17850 "
     "ORDER BY strptime(InvoiceDate, '%m/%d/%Y %H:%M') DESC;"),

    # 12
    ("Quante fatture contengono la voce “POSTAGE”?",
     "SELECT COUNT(DISTINCT InvoiceNo) AS postage_orders "
     "FROM data WHERE UPPER(Description) LIKE '%POSTAGE%';"),

    # 13
    ("Il prodotto più venduto nel Regno Unito",
     "SELECT Description, SUM(Quantity) AS total_qty "
     "FROM data WHERE Country = 'United Kingdom' "
     "GROUP BY Description "
     "ORDER BY total_qty DESC LIMIT 1;"),

    # 14
    ("I 5 paesi con più clienti distinti",
     "SELECT Country, COUNT(DISTINCT CustomerID) AS customer_count "
     "FROM data GROUP BY Country "
     "ORDER BY customer_count DESC LIMIT 5;"),

    # 15 – giornaliero Francia (DATE cast fix)
    ("Fatturato giornaliero verso la Francia",
     "SELECT CAST(strptime(InvoiceDate, '%m/%d/%Y %H:%M') AS DATE) AS day, "
     "       SUM(Quantity * UnitPrice) AS revenue "
     "FROM data WHERE Country = 'France' "
     "GROUP BY day ORDER BY day;"),

    # 16
    ("Quanti StockCode diversi esistono?",
     "SELECT COUNT(DISTINCT StockCode) AS unique_products FROM data;"),

    # 17
    ("I 10 prodotti col prezzo medio più alto",
     "SELECT Description, AVG(UnitPrice) AS avg_price "
     "FROM data GROUP BY Description "
     "ORDER BY avg_price DESC LIMIT 10;"),

    # 18
    ("Quante fatture risultano annullate (iniziano per “C”)?",
     "SELECT COUNT(DISTINCT InvoiceNo) AS cancelled_invoices "
     "FROM data WHERE InvoiceNo LIKE 'C%';"),

    # 19 – giorno top revenue (DATE cast fix)
    ("Il giorno con fatturato più alto",
     "SELECT day, revenue FROM ("
     "  SELECT CAST(strptime(InvoiceDate, '%m/%d/%Y %H:%M') AS DATE) AS day, "
     "         SUM(Quantity * UnitPrice) AS revenue "
     "  FROM data GROUP BY day"
     ") ORDER BY revenue DESC LIMIT 1;"),

    # 20
    ("Quantità media per riga d’ordine",
     "SELECT AVG(Quantity) AS avg_qty_per_line FROM data;")
]







def verify_queries() -> None:
    """Esegue ogni SQL per assicurarsi che sia sintatticamente e
    semanticamente corretto.  Solleva eccezione alla prima query che fallisce."""
    for idx, (question, sql) in enumerate(VALIDATION_PAIRS, 1):
        try:
            # Limitiamo il fetch a 1 riga così è velocissimo
            con.execute(sql).fetch_df()
        except Exception as exc:
            raise RuntimeError(
                f"Errore nella query #{idx}:\n"
                f"Domanda: {question}\n"
                f"SQL: {sql}\n{exc}"
            ) from exc


def seed_mongo() -> None:
    """Svuota e riempie la collection con le 20 coppie."""
    col = validation

    # Per evitare duplicati se lanci lo script più volte:
    col.delete_many({})

    docs = [{"question": q, "sql": s} for q, s in VALIDATION_PAIRS]
    col.insert_many(docs)
    print(f"Inserite {len(docs)} coppie in {validation} ")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--skip-check", action="store_true",
                        help="Salta l'esecuzione di prova delle query")
    args = parser.parse_args()

    if not args.skip_check:
        verify_queries()
        print("✓ Tutte le query eseguite con successo su DuckDB\n")

    seed_mongo()


if __name__ == "__main__":
    main()
