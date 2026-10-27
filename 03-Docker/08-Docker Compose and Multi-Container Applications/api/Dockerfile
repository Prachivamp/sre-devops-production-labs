
FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir --timeout=180 --retries=5 -r requirements.txt
COPY app.py .

EXPOSE 5001

CMD ["python", "app.py"]
