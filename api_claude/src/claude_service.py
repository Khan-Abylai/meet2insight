import logging
import anthropic
import config

logging.basicConfig(level=logging.INFO)

class ClaudeService:
    def __init__(self, model_name: str = "claude-3-haiku-20240307"):  # Изменили название модели
        self.client = anthropic.Client(api_key=config.Claude_API_KEY)
        self.model_name = model_name

    def predict(self, prompt: str) -> str:
        try:
            response = self.client.messages.create(
                model=self.model_name,
                max_tokens=1024,
                temperature=0.7,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return response.content[0].text.strip()
        except Exception as e:
            logging.error(f"Ошибка при генерации ответа через Claude: {e}")
            return f"Ошибка: {str(e)}"
