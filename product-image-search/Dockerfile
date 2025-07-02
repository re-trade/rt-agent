FROM ultralytics/ultralytics:latest-cpu

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1


COPY . .

RUN pip install  -r requirements.txt

EXPOSE 9090


CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "9090"]