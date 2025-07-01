FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
COPY cache.py .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["sh", "-c", "python cache.py"]

