./webpage-regex-to-rss.py https://www.bogleheads.org/forum/viewforum.php?f=2 "row bg1.*?(?P<link>./viewtopic.php.*?t=[0-9]+).*?topictitle\">(?P<title>.*?)</a>.*? (?P<date>[A-Za-z]{3} [A-Za-z]{3} [0-9]{1,2}, [0-9]{4} [0-9]{1,2}:[0-9]{2} ..).*?Replies: <strong>(?P<replies>[5-9]\d|\d{3,})" > output.xml
./upload_s3.py output.xml rsscombine test.xml
