import duckdb

con = duckdb.connect()
con.execute("CREATE VIEW data AS SELECT * FROM 'data/*.parquet';")
df = con.execute("SELECT * FROM data LIMIT 3").fetchdf()
print(df)
