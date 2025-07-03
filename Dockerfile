# Используем официальный образ Python 3.10
FROM python:3.10-slim

# Установим необходимые утилиты
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        curl \
        ca-certificates \
        gnupg && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Установка Poetry через официальный скрипт
RUN curl -sSL https://install.python-poetry.org  | python3 -

# Добавляем Poetry в PATH
ENV PATH="/root/.local/bin:${PATH}"

# Проверяем версию Poetry
RUN poetry --version

# Копируем минимальные файлы
COPY pyproject.toml .
COPY poetry.lock .
COPY README.md .

# Устанавливаем зависимости
RUN poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi

# Копируем исходники приложения
COPY app/ /app/app/

# Запуск приложения
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]