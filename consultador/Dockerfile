FROM python:3.11-slim

WORKDIR /app

COPY Consultador.py .
COPY requirements.txt .
COPY Transformador.py .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["sh", "-c", "python cache.py"]

