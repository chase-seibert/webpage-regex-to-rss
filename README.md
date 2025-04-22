# webpage-regex-to-rss

Scrape webpages to make an RSS feed using just regex

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
./webpage-regex-to-rss.py bogleheads2 --s3
```

## Docker 

```bash
docker build -t webpage-regex-to-rss .
docker run --rm webpage-regex-to-rss
```