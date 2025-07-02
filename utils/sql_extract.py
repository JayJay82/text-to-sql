import re

def extract_sql(text: str) -> str:
    """
    Restituisce la query nuda, senza blocchi ``` e senza prefisso 'sql '.
    Gestisce i casi:
        ```sql
        SELECT ...
        ```
        ```SELECT ...```
        sql SELECT ...
        SELECT ...
    """
    # 1) blocco ```sql ...```  o ``` ...```
    m = re.search(r"```(?:\s*sql)?\s*([\s\S]*?)```", text, flags=re.I)
    if m:
        return m.group(1).strip()

    # 2) stringa che inizia con 'sql '
    stripped = text.strip()
    if stripped.lower().startswith("sql"):
        stripped = stripped[3:].lstrip()

    # 3) rimuovi qualunque back-tick residuo
    return stripped.replace("`", "").strip()
