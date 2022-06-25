import re


FEEDS = {
    'bogleheads2': {
        'source_url': 'https://www.bogleheads.org/forum/viewforum.php?f=2',
        'id': 'https://s3-us-west-2.amazonaws.com/rsscombine/bogleheads2.xml',
        'title': 'Bogleheads Personal Finance, topics with over 50 replies',
        'parse': {
            'entry': lambda x: x.find_all('li', class_='row'),
            'title': lambda x: x.find('a', class_='topictitle').text,
            'link': r'./viewtopic.php.*?t=[0-9]+',
            'date': r'([A-Za-z]{3} [A-Za-z]{3} [0-9]{1,2}, [0-9]{4} [0-9]{1,2}:[0-9]{2} ..)',
            'content': lambda x: '',
            # extra
            'replies': r'Replies: <strong>([0-9]+)'
        },
        # exclude anything that doesn't have 50 or more replies
        'exclude': lambda d: int(d.get('replies') or 0) < 50,
        'timezone': 'Etc/GMT-5',  # footer says "All times are UTC-05:00"
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

FEEDS['thelawnforum9'] = FEEDS['bogleheads2'].copy()
FEEDS['thelawnforum9'].update({
    'source_url': 'https://thelawnforum.com/viewforum.php?f=9',
    'id': 'https://s3-us-west-2.amazonaws.com/rsscombine/thelawnforum9.xml',
    'title': 'The Lawn Forum -- Cool Season Lawns, topics with over 15 replies',
    's3': {
        'bucket': 'rsscombine',
        'object_name': 'thelawnforum9.xml',
    },
    # exclude anything that doesn't have 50 or more replies
    'exclude': lambda d: int(d.get('replies') or 0) < 15,
})

FEEDS['thelawnforum24'] = FEEDS['thelawnforum9'].copy()
FEEDS['thelawnforum24'].update({
    'source_url': 'https://thelawnforum.com/viewforum.php?f=24',
    'id': 'https://s3-us-west-2.amazonaws.com/rsscombine/thelawnforum24.xml',
    'title': 'The Lawn Forum -- Nutrients & Soil Fertility, topics with over 15 replies',
    's3': {
        'bucket': 'rsscombine',
        'object_name': 'thelawnforum24.xml',
    }
})

FEEDS['thelawnforum5'] = FEEDS['thelawnforum9'].copy()
FEEDS['thelawnforum5'].update({
    'source_url': 'https://thelawnforum.com/viewforum.php?f=5',
    'id': 'https://s3-us-west-2.amazonaws.com/rsscombine/thelawnforum5  .xml',
    'title': 'The Lawn Forum -- Irrigation, topics with over 15 replies',
    's3': {
        'bucket': 'rsscombine',
        'object_name': 'thelawnforum5.xml',
    }
})