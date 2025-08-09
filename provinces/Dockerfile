FROM python:3.12-slim AS base
RUN apt-get update && apt-get install git -y && apt-get install -y g++ && apt-get install ffmpeg libsm6 libxext6 gcc  -y


FROM base AS builder
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /build
COPY . .
RUN uv sync --frozen

CMD ["uv", "run", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "9090"]