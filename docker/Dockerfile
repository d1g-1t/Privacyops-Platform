FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

FROM base AS deps
COPY pyproject.toml ./
RUN pip install --upgrade pip setuptools wheel && \
    pip install ".[dev]"

FROM deps AS runtime
COPY . .
EXPOSE 8700
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8700"]
