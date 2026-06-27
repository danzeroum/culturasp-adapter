# Single image used by both the `api` and `scraper` services.
# Based on the official Playwright image so Chromium + system deps are ready.
FROM mcr.microsoft.com/playwright/python:v1.43.0-jammy

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

# System deps for OCR (Tesseract + Poppler for pdf2image). Portuguese language pack.
RUN apt-get update && apt-get install -y --no-install-recommends \
        tesseract-ocr \
        tesseract-ocr-por \
        poppler-utils \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install dependencies first (better layer caching).
COPY pyproject.toml README.md ./
COPY src ./src
RUN pip install --upgrade pip && pip install -e ".[ocr]"

# App code (kept after install so source edits don't bust the dep layer in dev).
COPY . .

EXPOSE 8000

# Default command runs the API; the scraper service overrides this in compose.
CMD ["uvicorn", "culturasp.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
