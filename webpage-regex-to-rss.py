#!/usr/bin/env python3

import sys
import urllib.request
import re
import urllib
import html.parser


def format_link(base_url, link):
    link = urllib.parse.urljoin(url, d['link'])
    return html.unescape(link)


def generate_rss(entries):

    entry_template = '''
    <entry>
        <published>{date}</published>
        <id>{link}</id>
        <link href="{link}"/>
        <title type="html"><![CDATA[{title}]]></title>
        <content type="html" xml:base="{link}"><![CDATA[{content}]]></content>
    </entry>
'''

    entries = ''.join([entry_template.format(**e) for e in entries])

    return '''
<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom" xml:lang="en-us">
    <title>TODO</title>
    <updated>TODO</updated>
    <author><name><![CDATA[TODO]]></name></author>
    {}
</feed>
'''.format(entries)


if __name__ == '__main__':
    # TODO optionally pass args via environment variables
    try:
        url, regex = sys.argv[1], sys.argv[2]
    except IndexError:
        print('Usage: ./webpage-regex-to-rss.py URL REGEX')
        exit(1)

    pattern = re.compile(regex)

    with urllib.request.urlopen(url) as response:
        _html = str(response.read())
        entries = []
        for entry in pattern.finditer(_html):
            d = entry.groupdict()
            d['link'] = format_link(url, d['link'])
            d['content'] = d.get('content', '')
            # todo date format
            # print(d)
            entries.append(d)

    print(generate_rss(entries))
