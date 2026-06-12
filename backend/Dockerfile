# API Dockerfile
FROM python:3.12-alpine
WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .

RUN pip --no-cache-dir install -r requirements.txt

COPY ./backend .

EXPOSE 5000

ENV PYTHONPATH="/app"

CMD ["python", "app.py"]