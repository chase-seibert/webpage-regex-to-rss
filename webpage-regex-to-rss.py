#!/usr/bin/env python3

import argparse
import sys
import urllib.request
import re
import urllib
import html.parser
import io

from bs4 import BeautifulSoup
import boto3

import settings


def format_link(base_url, link):
    link = urllib.parse.urljoin(base_url, link)
    return link


def generate_rss(entries, options):

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

    return '''<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom" xml:lang="en-us">
    <title>{title}</title>
    <updated>TODO</updated>
    <author><name><![CDATA[TODO]]></name></author>
    {entries}
</feed>
'''.format(entries=entries, **options)


def get_entries(_html, parse_options):
    # pattern.finditer(_html):
    selector = parse_options.get('entry')
    if callable(selector):
        soup = BeautifulSoup(_html, 'html.parser')
        return [str(e) for e in selector(soup)]
    else:
        raise NotImplementedError(type(selector))


def parse_field(_html, selector):
    if type(selector) == str:
        match = re.findall(selector, _html)
        try:
            return match[0]
        except IndexError:
            return None
    elif callable(selector):
        soup = BeautifulSoup(_html, 'html.parser')
        return str(selector(soup))
    else:
        raise NotImplementedError(type(selector))


def parse_entry(_html, parse_options):
    d = {}
    for field in parse_options.keys():
        d[field] = parse_field(_html, parse_options.get(field))
    return d


def print_entry(d):
    # print(d['title'])
    print(html.unescape(d['link']))
    # print('\t', d['date'])
    # print('\t', d['replies'])
    pass


def upload_s3(xml_data, options):
    contents = io.StringIO(xml_data)
    s3_client = boto3.client('s3')
    contents_bytes = io.BytesIO(contents.getvalue().encode())
    response = s3_client.put_object(
        Body=contents_bytes,
        Bucket=options.get('bucket'),
        Key=options.get('object_name'),
        ContentType='text/xml',
        ACL='public-read',
    )
    print('Success %r' % response)


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Scrape webpages to make an RSS feed using just regex')
    parser.add_argument('feed', help='Feed key in settings.py')
    parser.add_argument('--s3', dest='upload_s3', action='store_true', help='Upload to S3')
    args = parser.parse_args()
    options = settings.FEEDS[args.feed]

    source_url = options.get('source_url')
    with urllib.request.urlopen(source_url) as response:
        _html = str(response.read())
        parse_options = options.get('parse')
        exclude = options.get('exclude')
        entries = []
        for entry in get_entries(_html, parse_options):
            d = parse_entry(entry, parse_options)
            d['link'] = format_link(source_url, d['link'])
            if exclude(d):
                continue
            entries.append(d)
            print_entry(d)

    rss = generate_rss(entries, options)
    # if args.debug:
    #    print(rss)
    if args.upload_s3:
        upload_s3(rss, options.get('s3'))
