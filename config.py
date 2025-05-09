import os

MODEL = "gpt-4o-mini"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

llm_config = {
    "config_list": [
        {
            "model": MODEL,
            "api_key": OPENAI_API_KEY,
            "base_url": "https://api.openai.com/v1"
        }
    ]
}