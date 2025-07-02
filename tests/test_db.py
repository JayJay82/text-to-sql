# tests/test_db.py
import os
import sys

# Ensure project root is in sys.path for imports
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import duckdb
import pandas as pd
import pytest

import data.db as db_module
from data.db import run_query


def test_run_query_returns_dataframe(tmp_path, monkeypatch):
    """
    Verify that run_query returns a DataFrame matching the Parquet data via the 'data' view.
    """
    # Create sample DataFrame and write to Parquet
    df_original = pd.DataFrame({'a': [1, 2, 3]})
    pq_file = tmp_path / "sample.parquet"
    df_original.to_parquet(pq_file)

    # Setup new DuckDB connection and view
    new_con = duckdb.connect()
    new_con.execute(f"CREATE VIEW data AS SELECT * FROM '{pq_file}'")

    # Monkeypatch the connection in data.db
    monkeypatch.setattr(db_module, 'con', new_con)

    # Execute query
    result_df = run_query("SELECT * FROM data")

    # Assertions
    assert isinstance(result_df, pd.DataFrame)
    pd.testing.assert_frame_equal(result_df.reset_index(drop=True), df_original)


@pytest.mark.parametrize("rows, cols", [
    ([], ['a']),          # no rows
    ([{'a': 42}], ['a']), # single row
])
def test_run_query_various_sizes(tmp_path, monkeypatch, rows, cols):
    """
    Ensure run_query handles empty and single-row DataFrames correctly.
    """
    df_test = pd.DataFrame(rows, columns=cols)
    pq_file = tmp_path / "various.parquet"
    df_test.to_parquet(pq_file)

    new_con = duckdb.connect()
    new_con.execute(f"CREATE VIEW data AS SELECT * FROM '{pq_file}'")
    monkeypatch.setattr(db_module, 'con', new_con)

    result = run_query("SELECT * FROM data")
    assert list(result.columns) == cols
    assert len(result) == len(df_test)
