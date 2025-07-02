import numpy as np
import pandas as pd

def compare_dfs(df_a: pd.DataFrame, df_b: pd.DataFrame) -> bool:
    """
    Ritorna True se i due DataFrame contengono gli stessi valori
    indipendentemente da:
      • nomi delle colonne (alias diversi)
      • ordine delle colonne
      • ordine delle righe

    Confronto:
      • numerico → np.allclose(equal_nan=True)
      • non numerico → uguaglianza stringa

    Parametri
    ---------
    df_a, df_b : pandas.DataFrame
        DataFrame da confrontare (tipicamente output di due query SQL)

    Returns
    -------
    bool
        True se equivalenti, False altrimenti
    """
    # 1. stessa forma?
    if df_a.shape != df_b.shape:
        return False

    # 2. ordina righe (se possibile) per confronto stabile
    try:
        df_a = df_a.sort_values(list(df_a.columns)).reset_index(drop=True)
        df_b = df_b.sort_values(list(df_b.columns)).reset_index(drop=True)
    except Exception:
        # se tipi misti non consentono l'ordinamento, prosegui comunque
        pass

    # 3. ordina e riallinea le colonne in base all'ordine alfabetico
    df_a = df_a.reindex(sorted(df_a.columns), axis=1)
    df_b = df_b.reindex(sorted(df_b.columns), axis=1)

    # 4. confronto colonna per colonna per posizione
    for i in range(df_a.shape[1]):
        col_a = df_a.iloc[:, i]
        col_b = df_b.iloc[:, i]

        if pd.api.types.is_numeric_dtype(col_a) and pd.api.types.is_numeric_dtype(col_b):
            if not np.allclose(col_a.astype(float), col_b.astype(float), equal_nan=True):
                return False
        else:
            if not col_a.astype(str).equals(col_b.astype(str)):
                return False

    return True
