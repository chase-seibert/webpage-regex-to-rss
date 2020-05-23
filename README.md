# webpage-regex-to-rss

Scrape webpages to make an RSS feed using just regex

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
./webpage-regex-to-rss.py https://www.bogleheads.org/forum/viewforum.php?f=2 "row bg1.*?(?P<link>./viewtopic.php.*?t=[0-9]+).*?topictitle\">(?P<title>.*?)</a>.*? (?P<date>[A-Za-z]{3} [A-Za-z]{3} [0-9]{1,2}, [0-9]{4} [0-9]{1,2}:[0-9]{2} ..).*?Replies: <strong>(?P<replies>[5-9]\d|\d{3,})" > output.xml
./upload_s3.py output.xml rsscombine test.xml
```

This script is pretty fragile. You need to do all of the following:

- Extract link, title, date groups with your regex
- Your regex must match something
- You need to have your AWS credentials set via environment variables (AWS_ACCESS_KEY_ID, AWS_REGION, AWS_SECRET_ACCESS_KEY)

TODO:
- Don't fail on regex not matching
- Populate feed title, entity author
- Optionally passing url, regex by environment variable
