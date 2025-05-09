from autogen.agentchat import AssistantAgent, UserProxyAgent
from config import llm_config

user_agent = UserProxyAgent("user")

nl2sql_agent_template = """-Sei un assistente che deve trasformare il linguaggio naturale in query duckdb\n'
                         '-La view sulla quale lavorerai si chiama data\n'
                         '-i file sui quali eseguirai le query sono file parquet\n'
                         'Restituisci **solo** lo statement SQL nel primo blocco ```sql``` senza commenti.\n'
                         'Se devi manipolare il campo InvoiceDate, considera che è nel formato 'MM/DD/YYYY HH:MM'. Usa STRPTIME(InvoiceDate, '%m/%d/%Y %H:%M') per convertirlo in TIMESTAMP.\n'
                         '-la view è cosi composta:\n'
                         '-- InvoiceNo , questo campo corrisponde al numero invoice ed è di tipo stringa\n'
                         '-- StockCode , questo campo descrive identificativo del prodotto ed è di tipo stringa\n'
                         '-- Description , descrizione del prodotto ed è di tipo stringa\n'
                         '-- Quantity , descrive la quantità del prodotto acquistata ed è di tipo i64\n'
                         '-- InvoiceDate , descrive la data dell acquisto ed è di tipo stringa\n'
                         '-- UnitPrice , descrive la quantità ed è di tipo f64\n'
                         '-- CustomerID , descrive id del cliente ed è di tipo f64\n'
                         '-- Country , descrive il luogo del negozio ed è di tipo stringa\n'
                         'questo è un esempio di record:[InvoiceNo=536365,StockCode=85123A,Description=WHITE HANGING HEART T-LIGHT HOLDER,Quantity=6,InvoiceDate=12/1/2010 8:26,UnitPrice=2.55,CustomerID=17850.0,Country=United Kingdom')
                         """
nl2sql_agent = AssistantAgent(
    "nl2sql",
    llm_config=llm_config,
    system_message=nl2sql_agent_template
)

guard_agent_template = """
    Verifica che lo SQL sia sicuro
    Se non valido, rispondi con ERRORE.
    Se la query NON è sicura, spiega nel campo "reason" perché.
    Rispondi con un JSON con due campi:
    - "valid": true/false
    - "reason": spiegazione della valutazione
    """

guard_agent = AssistantAgent(
    "guard",
    llm_config=llm_config,
    system_message=guard_agent_template
)
