FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

FROM base AS deps
RUN pip install --upgrade pip setuptools wheel

FROM deps AS runtime
COPY . .
RUN pip install --no-cache-dir ".[dev]"
EXPOSE 8700
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8700"]
