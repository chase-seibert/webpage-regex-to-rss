import re


FEEDS = {
    'bogleheads2': {
        'source_url': 'https://www.bogleheads.org/forum/viewforum.php?f=2',
        'title': 'Bogleheads Personal Finance, topics with over 50 replies',
        'parse': {
            'entry': lambda x: x.find_all('li', class_='row'),
            'title': lambda x: x.find('a', class_='topictitle').text,
            'link': r'./viewtopic.php.*?t=[0-9]+',
            'date': r'topic-poster.*?([A-Za-z]{3} [A-Za-z]{3} [0-9]{1,2}, [0-9]{4} [0-9]{1,2}:[0-9]{2} ..)',
            'content': lambda x: '',
            # extra
            'replies': r'Replies: <strong>([0-9]+)'
        },
        # exclude anything that doesn't have 50 or more replies
        'exclude': lambda d: int(d.get('replies') or 0) < 50,
    },
}
