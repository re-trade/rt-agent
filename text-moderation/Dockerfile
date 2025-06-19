FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

# Create weights directory
RUN mkdir -p /app/data

# Copy weights file specifically
COPY app/core/data/vn_offensive_words.txt /app/data/

# Copy rest of application
COPY . .

EXPOSE 8888

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8888"]
