import re


FEEDS = {
    'bogleheads2': {
        'source_url': 'https://www.bogleheads.org/forum/viewforum.php?f=2',
        'id': 'https://s3-us-west-2.amazonaws.com/rsscombine/bogleheads2.xml',
        'title': 'Bogleheads Personal Finance, topics with over 50 replies',
        'parse': {
            'entry': lambda x: x.find_all('li', class_='row bg1'),
            'title': lambda x: x.find('a', class_='topictitle').text,
            'link': r'./viewtopic.php.*?t=[0-9]+',
            'date': r'» ([A-Za-z]{3} [A-Za-z]{3} [0-9]{1,2}, [0-9]{4} [0-9]{1,2}:[0-9]{2} ..)',
            'content': lambda x: '',
            # extra
            'replies': r'Replies: <strong>([0-9]+)'
        },
        # exclude anything that doesn't have 50 or more replies
        'exclude': lambda d: int(d.get('replies') or 0) < 50,
        'timezone': 'Etc/GMT-7',  # footer says "All times are UTC-07:00"
        's3': {
            'bucket': 'rsscombine',
            'object_name': 'bogleheads2.xml',
        }
    },
}

FEEDS['bogleheads11'] = FEEDS['bogleheads2'].copy()
FEEDS['bogleheads11'].update({
    'source_url': 'https://www.bogleheads.org/forum/viewforum.php?f=11',
    'id': 'https://s3-us-west-2.amazonaws.com/rsscombine/bogleheads11.xml',
    'title': 'Bogleheads Personal Consumer Issues, topics with over 50 replies',
    's3': {
        'bucket': 'rsscombine',
        'object_name': 'bogleheads11.xml',
    }
})

FEEDS['bogleheads1'] = FEEDS['bogleheads2'].copy()
FEEDS['bogleheads1'].update({
    'source_url': 'https://www.bogleheads.org/forum/viewforum.php?f=1',
    'id': 'https://s3-us-west-2.amazonaws.com/rsscombine/bogleheads1.xml',
    'title': 'Bogleheads Personal Investments, topics with over 50 replies',
    's3': {
        'bucket': 'rsscombine',
        'object_name': 'bogleheads1.xml',
    }
})

FEEDS['bogleheads10'] = FEEDS['bogleheads2'].copy()
FEEDS['bogleheads10'].update({
    'source_url': 'https://www.bogleheads.org/forum/viewforum.php?f=10',
    'id': 'https://s3-us-west-2.amazonaws.com/rsscombine/bogleheads10.xml',
    'title': 'Bogleheads Investing - Theory, News & General, topics with over 50 replies',
    's3': {
        'bucket': 'rsscombine',
        'object_name': 'bogleheads10.xml',
    }
})
