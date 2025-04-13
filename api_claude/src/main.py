from fastapi import FastAPI, Form, UploadFile, File, HTTPException, Depends
from fastapi.concurrency import run_in_threadpool
from claude_service import ClaudeService
from file_processor import TranscriptProcessorService

app = FastAPI()

def get_claude_service():
    return ClaudeService()

def get_processor_service(
    claude_service: ClaudeService = Depends(get_claude_service)
):
    return TranscriptProcessorService(claude_service)

ALLOWED_MIME_TYPES = [
    "text/plain",
    "application/json",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
]

@app.get("/")
def root():
    return {"message": "Claude API Service"}

@app.post("/api/generate")
async def generate(
    prompt: str = Form(...),
    claude_service: ClaudeService = Depends(get_claude_service)
):
    response_text = await run_in_threadpool(claude_service.predict, prompt)
    return {"response": response_text}

@app.post("/api/process_file")
async def process_file(
    file: UploadFile = File(...),
    processor_service: TranscriptProcessorService = Depends(get_processor_service)
):
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type. Only TXT, JSON, DOC, and DOCX files are allowed."
        )

    # Запускаем синхронную работу в пуле потоков
    result = await run_in_threadpool(
        processor_service.process_transcript_file, file
    )
    return {"response": result}
