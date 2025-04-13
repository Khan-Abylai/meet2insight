FROM python:3.10-slim

# Устанавливаем временную зону
ENV TZ=Asia/Almaty
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Устанавливаем локаль
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8
ENV LANGUAGE=C.UTF-8

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Обновляем pip
RUN pip install --no-cache-dir --upgrade pip

# Устанавливаем зависимости Python
RUN pip install --no-cache-dir \
    fastapi \
    uvicorn \
    python-multipart \
    requests \
    openai \
    "anthropic>=0.25.0" \
    python-docx

# Проверяем установленную версию библиотеки anthropic
RUN python -c "import anthropic; print('Anthropic version:', anthropic.__version__)"

# Копируем исходный код
ADD src/ /opt/api/
WORKDIR /opt/api/

# Запуск через скрипт
ENTRYPOINT ["sh", "entrypoint.sh"]
