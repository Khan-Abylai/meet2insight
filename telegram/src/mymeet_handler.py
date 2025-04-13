import httpx
import logging
import config

async def transcribe_meeting_link(meeting_link: str) -> str:
    """
    Отправляем ссылку на встречу в сервис mymeet для транскрибации.
    Возвращаем полученный из mymeet текст транскрипта.
    """
    payload = {"meeting_link": meeting_link}
    headers = {"Authorization": f"Bearer {config.MYMEET_API_KEY}"}
    async with httpx.AsyncClient() as client:
        response = await client.post(config.MYMEET_TRANSCRIBE_URL, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        transcript = data.get("transcript")
        if not transcript:
            raise ValueError("Transcript not found in response")
        logging.info("Транскрибация ссылки завершена")
        return transcript

async def transcribe_media_file(file_bytes: bytes, filename: str) -> str:
    """
    Отправляем аудио/видео (в байтах) в сервис mymeet для транскрибации.
    Возвращаем полученный текст транскрипта.
    """
    files = {"file": (filename, file_bytes, "application/octet-stream")}
    headers = {"Authorization": f"Bearer {config.MYMEET_API_KEY}"}
    async with httpx.AsyncClient() as client:
        response = await client.post(config.MYMEET_TRANSCRIBE_URL, files=files, headers=headers)
        response.raise_for_status()
        data = response.json()
        transcript = data.get("transcript")
        if not transcript:
            raise ValueError("Transcript not found in response")
        logging.info("Транскрибация медиа файла завершена")
        return transcript
