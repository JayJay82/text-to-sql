import re
import textwrap

def extract_sql(text: str) -> str:
    """
    Restituisce solo la query, senza ``` delimiters e senza la parola 'sql'.
    Funziona con:
        ```sql
        SELECT ...
        ```
        sql SELECT ...
        SELECT ...
    """
    # ⇢ ① blocco ```sql ... ```
    m = re.search(r"```\\s*sql\\s*([\\s\\S]*?)```", text, flags=re.I)
    if m:
        return textwrap.dedent(m.group(1)).strip()

    # ⇢ ② blocco ``` ... ``` senza 'sql'
    m = re.search(r"```([\\s\\S]*?)```", text)
    if m:
        return textwrap.dedent(m.group(1)).strip()

    # ⇢ ③ stringa che inizia con 'sql'
    stripped = text.strip()
    if stripped.lower().startswith('sql'):
        return stripped[3:].lstrip()

    # ⇢ ④ stringa già pulita
    return stripped
