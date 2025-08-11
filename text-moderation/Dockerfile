FROM python:3.12-slim-bullseye AS builder

RUN apt-get update && apt-get install git -y && apt-get install -y g++ && apt-get install ffmpeg libsm6 libxext6 gcc  -y
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app
RUN apt-get update && apt-get install -y gcc
RUN mkdir -p /app/data
COPY app/core/data/vn_offensive_words.txt /app/data/
COPY . .
RUN uv sync --frozen
RUN uv run pyinstaller --onefile --add-data "app/core/data/vn_offensive_words.txt:app/core/data" app/main.py


FROM debian:bookworm-slim AS deploy
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libsm6 \
    libxext6 \
    && rm -rf /var/lib/apt/lists/* \
WORKDIR /app
COPY --from=builder /app/dist/main /app/main
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
CMD ["/app/main"]
