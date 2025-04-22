FROM python:3.11-slim

WORKDIR /usr/local/etc/webpage-regex-to-rss

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY webpage-regex-to-rss.py .
COPY settings.py .

CMD ["python", "webpage-regex-to-rss.py", "all", "--s3"]