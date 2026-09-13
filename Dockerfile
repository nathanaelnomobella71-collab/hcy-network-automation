# Étape 1 : Build
FROM python:3.11-slim AS builder

WORKDIR /app
COPY requirements.txt .

RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --prefix=/install --no-warn-script-location --default-timeout=1000 -r requirements.txt

# Étape 2 : Image finale légère
FROM python:3.11-slim

WORKDIR /app
COPY --from=builder /install /usr/local
COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]