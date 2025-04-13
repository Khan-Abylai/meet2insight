import logging
import anthropic
import config

logger = logging.getLogger(__name__)

class ClaudeService:
    def __init__(self, model_name: str = "claude-3-opus-20240229"):
        self.client = anthropic.Client(api_key=config.Claude_API_KEY)
        self.model_name = model_name

    def predict(self, prompt: str) -> str:
        try:
            response = self.client.messages.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1024
            )
            logger.info(f"Anthropic raw response: {response}")

            # Берём текст из атрибута .completion
            completion = response.content[0].text
            return completion.strip()
        except Exception as e:
            logger.error(f"Ошибка при генерации ответа через Claude: {e}", exc_info=True)
            raise e
