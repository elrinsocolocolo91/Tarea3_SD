FROM python:3.9-slim
WORKDIR /app
COPY . .
RUN pip install requests pymongo

CMD ["sh", "-c", "python scraper.py && python consultador.py"]

