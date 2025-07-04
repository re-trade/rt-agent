FROM python:3.12-slim-bullseye

RUN apt-get update && apt-get install git -y && apt-get install -y g++ && apt-get install ffmpeg libsm6 libxext6  -y
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app
RUN apt-get update && apt-get install -y gcc
RUN mkdir -p /app/data
COPY app/core/data/vn_offensive_words.txt /app/data/
COPY . .
RUN uv sync
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8888"]