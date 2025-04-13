from fastapi import FastAPI, Form
from claude_service import ClaudeService

app = FastAPI()
claude_service = ClaudeService()

@app.get("/")
def root():
    return {"message": "Claude API Service"}

@app.post("/api/generate")
async def generate(prompt: str = Form(...)):
    """
    Эндпоинт для генерации ответа модели.
    prompt передаётся в теле запроса в формате form-data.
    """
    response_text = claude_service.predict(prompt)
    return {"response": response_text}
