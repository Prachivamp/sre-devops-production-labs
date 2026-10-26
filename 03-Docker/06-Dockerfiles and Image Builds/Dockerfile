FROM python:3.12-slim

WORKDIR /app

COPY app/app.py ./app.py

ENV APP_PORT=8000

EXPOSE 8000

USER 10001:10001

CMD ["python", "-u", "app.py"]
