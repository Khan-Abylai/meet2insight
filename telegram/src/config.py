import os

TOKEN = os.environ.get("TELEGRAM_TOKEN", "")

# URL для GPT API
Claude_API_URL = os.environ.get("Claude_API_URL", "http://api_llm:9001/api/generate")
