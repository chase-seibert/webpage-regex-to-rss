.PHONY: install run

install:
	python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt

run:
	set -a && source .env && set +a && source .venv/bin/activate && ./webpage-regex-to-rss.py all --s3