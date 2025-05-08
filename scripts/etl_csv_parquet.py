import pandas as pd

df = pd.read_csv("../data/encoded-data.csv")      # legge il CSV
df.to_parquet(
    "../data/dati.parquet",
    engine="pyarrow",             # o "fastparquet"
    compression="snappy",         # snappy = default; zstd e gzip sono alternative
    index=False                   # esclude l’indice pandas
)