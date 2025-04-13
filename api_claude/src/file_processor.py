import logging
import io
import zipfile
import json
from fastapi import HTTPException, UploadFile
import docx
from config import SYSTEM_PROMPT
from claude_service import ClaudeService

logger = logging.getLogger(__name__)

def split_text_into_chunks(text: str, max_chars: int = 15000) -> list[str]:
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + max_chars, len(text))
        chunks.append(text[start:end])
        start = end
    return chunks

class TranscriptProcessorService:
    def __init__(self, claude_service: ClaudeService):
        self.claude_service = claude_service
        self.config = SYSTEM_PROMPT

    def read_file_content(self, uploaded_file: UploadFile) -> str:
        try:
            ct = uploaded_file.content_type

            # TXT
            if ct == "text/plain":
                raw = uploaded_file.file.read()
                return raw.decode("utf-8")

            # JSON
            if ct == "application/json":
                raw = uploaded_file.file.read().decode("utf-8")
                data = json.loads(raw)
                # Если есть прямое поле transcript
                if isinstance(data, dict) and "transcript" in data:
                    return data["transcript"]
                # Иначе — собрать все строки рекурсивно
                texts: list[str] = []
                def extract(o):
                    if isinstance(o, str):
                        texts.append(o)
                    elif isinstance(o, dict):
                        for v in o.values():
                            extract(v)
                    elif isinstance(o, list):
                        for i in o:
                            extract(i)
                extract(data)
                return "\n".join(texts)

            # DOCX
            if ct == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                file_bytes = uploaded_file.file.read()
                stream = io.BytesIO(file_bytes)
                if not zipfile.is_zipfile(stream):
                    raise HTTPException(400, "Invalid DOCX file.")
                stream.seek(0)
                doc = docx.Document(stream)
                return "\n".join(p.text for p in doc.paragraphs)

            # Не поддерживается
            raise HTTPException(400, f"Unsupported content type: {ct}")

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error reading file: {e}", exc_info=True)
            raise HTTPException(500, "Failed to read file.")

    def summarize_chunk(self, text_chunk: str) -> str:
        prompt = self.config.replace("{FILE_CONTENT}", text_chunk)
        return self.claude_service.predict(prompt)

    def process_transcript_file(self, uploaded_file: UploadFile) -> str:
        content = self.read_file_content(uploaded_file)
        chunks = split_text_into_chunks(content, max_chars=15000)

        summaries = []
        for idx, chunk in enumerate(chunks, 1):
            logger.info(f"Chunk {idx}/{len(chunks)}: {len(chunk)} chars")
            summaries.append(self.summarize_chunk(chunk))

        combined = "\n\n".join(summaries)
        if len(chunks) > 1:
            logger.info("Final summary of combined text")
            return self.summarize_chunk(combined)
        return summaries[0]
