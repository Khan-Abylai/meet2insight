import os

TOKEN = os.environ.get("TELEGRAM_TOKEN", "7700535045:AAGD_pTIgbtS_rE2i9H2SFrCncgLilaoHuA")

# URL для GPT API
Claude_API_URL = os.environ.get("Claude_API_URL", "http://api_llm:9001/api/process_file")

# Mymeet
MYMEET_TRANSCRIBE_URL = os.environ.get("MYMEET_TRANSCRIBE_URL", "http://backend.mymeet.ai/api/undo_clear_transcript")
MYMEET_API_KEY = os.environ.get("MYMEET_API_KEY", "1fb4030a-46bd-4e03-bf37-4c0a28ae5147")