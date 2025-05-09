import duckdb
import pandas as pd

con = duckdb.connect(":memory:")
con.execute("CREATE VIEW data AS SELECT * FROM 'data/*.parquet';")

def run_query(sql: str) -> pd.DataFrame:
    return con.execute(sql).df()