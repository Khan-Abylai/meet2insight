import logging
import httpx
from io import BytesIO
from telegram import Update
from telegram.ext import (
    Application, CommandHandler, MessageHandler, filters, CallbackContext
)
import config
import mymeet_handler

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

async def start(update: Update, context: CallbackContext):
    await update.message.reply_text(
        "Привет! Я бот на базе Claude.\n"
        "Отправьте ссылку на встречу, аудио/видео файл или готовый транскрипт (.txt, .json, .docx и т.п.)."
    )

async def help_command(update: Update, context: CallbackContext):
    help_text = (
        "*Как пользоваться:*\n"
        "1) Отправьте ссылку на встречу — я получу транскрипт через mymeet и передам на Claude API.\n"
        "2) Отправьте аудио/видео/voice — я транскрибирую через mymeet и передам на Claude API.\n"
        "3) Отправьте готовый файл (.txt, .json, .docx, .doc, .pdf) — я сразу отправлю его на Claude API.\n"
        "• /help — показать это сообщение\n"
    )
    await update.message.reply_text(help_text, parse_mode="Markdown")

async def process_media(update: Update, context: CallbackContext):
    """
    Обработка входящих сообщений:
    1) Если это текст, начинающийся с http(s), считаем это ссылкой на встречу – транскрибируем через mymeet.
    2) Если это voice/audio/video/document с MIME типом audio/video – транскрибируем через mymeet.
    3) Иначе - пробуем передать файл напрямую (process_transcript_file).
    """
    text = update.message.text

    # (1) Ссылка на встречу
    if text and text.startswith("http"):
        try:
            transcript = await mymeet_handler.transcribe_meeting_link(text)
            async with httpx.AsyncClient() as client:
                files = {"file": ("transcript.txt", transcript, "text/plain")}
                # Отправляем результат на Claude API
                resp = await client.post(config.Claude_API_URL, files=files,   timeout=60.0)
                resp.raise_for_status()
                response_text = resp.json().get("response", "Ошибка: пустой ответ от API")
            await update.message.reply_text(response_text)
        except Exception as e:
            logging.error(f"Ошибка при транскрибации ссылки: {e}", exc_info=True)
            await update.message.reply_text("Ошибка при транскрибации ссылки через mymeet.")
        return

    # (2) Медиа-файлы (voice/audio/video)
    file_obj = None
    filename = "media_file"
    if update.message.voice:
        file_obj = update.message.voice
        filename += ".ogg"
    elif update.message.audio:
        file_obj = update.message.audio
        filename = file_obj.file_name or "audio.mp3"
    elif update.message.video:
        file_obj = update.message.video
        filename += ".mp4"
    elif update.message.document and update.message.document.mime_type.startswith(("audio/", "video/")):
        file_obj = update.message.document
        filename = file_obj.file_name

    if file_obj:
        # (2a) Скачиваем & транскрибируем
        try:
            file_info = await file_obj.get_file()
            file_bytes = await file_info.download_as_bytearray()
            transcript = await mymeet_handler.transcribe_media_file(file_bytes, filename)
            async with httpx.AsyncClient() as client:
                files = {"file": ("transcript.txt", transcript, "text/plain")}
                resp = await client.post(config.Claude_API_URL, files=files, timeout=60.0)
                resp.raise_for_status()
                response_text = resp.json().get("response", "Ошибка: пустой ответ от API")
            await update.message.reply_text(response_text)
        except Exception as e:
            logging.error(f"Ошибка при обработке медиа файла: {e}", exc_info=True)
            await update.message.reply_text("Ошибка при транскрибации медиа через mymeet.")
    else:
        # (3) Иначе, пробуем документ напрямую
        await process_transcript_file(update, context)

async def process_transcript_file(update: Update, context: CallbackContext):
    """
    Пересылает документ (txt, json, doc, docx, pdf, etc.) напрямую в Claude API.
    """
    if not update.message.document:
        await unsupported_message(update, context)
        return

    try:
        file_obj = update.message.document
        file_info = await file_obj.get_file()
        file_bytes = await file_info.download_as_bytearray()
        file_name = file_obj.file_name
        mime_type = file_obj.mime_type or "application/octet-stream"

        file_to_send = BytesIO(file_bytes)
        async with httpx.AsyncClient() as client:
            files = {"file": (file_name, file_to_send, mime_type)}
            try:
                resp = await client.post(config.Claude_API_URL, files=files, timeout=60.0)
                resp.raise_for_status()
                response_text = resp.json().get("response", "Ошибка: пустой ответ от API")
                await update.message.reply_text(response_text)
            except httpx.HTTPStatusError as err:
                logging.error(
                    f"HTTP error при отправке файла в Claude API. "
                    f"Status={err.response.status_code}, text={err.response.text}"
                )
                await update.message.reply_text("HTTP error при пересылке файла на Claude API.")
            except httpx.ReadTimeout:
                logging.error("Timeout при обращении к Claude API (увеличьте таймаут).")
                await update.message.reply_text("Claude API слишком долго не отвечает.")
            except Exception as e:
                logging.error(f"Ошибка при пересылке документа: {e}", exc_info=True)
                await update.message.reply_text("Ошибка при пересылке документа на Claude API.")
    except Exception as e:
        logging.error(f"Ошибка при пересылке документа: {e}", exc_info=True)
        await update.message.reply_text("Ошибка при пересылке документа на Claude API.")

async def unsupported_message(update: Update, context: CallbackContext):
    await update.message.reply_text(
        "Пожалуйста, отправьте ссылку, файл аудио/видео или готовый транскрипт."
    )

def main():
    app = Application.builder().token(config.TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))

    # Универсальный MessageHandler
    app.add_handler(MessageHandler(filters.ALL, process_media))

    logging.info("Бот запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()
