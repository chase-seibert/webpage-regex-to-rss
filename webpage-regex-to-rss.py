#!/usr/bin/env python3

import argparse
import sys
import urllib.request
import re
import urllib
import html.parser
import io
import pytz

from bs4 import BeautifulSoup
import boto3
from feedgen.feed import FeedGenerator
import dateutil

import settings


def format_link(base_url, link):
    link = urllib.parse.urljoin(base_url, link)
    return link


def generate_rss(entries, options):
    fg = FeedGenerator()
    fg.id(options.get('id'))
    fg.title(options.get('title'))
    # fg.author( {'name':'John Doe','email':'john@example.de'} )
    # fg.link( href='http://example.com', rel='alternate' )
    # fg.logo('http://ex.com/logo.jpg')
    # fg.subtitle('This is a cool feed!')
    # fg.link( href='http://larskiesow.de/test.atom', rel='self' )
    fg.language('en')

    for entry in entries:
        fe = fg.add_entry()
        fe.id(entry.get('link'))
        fe.title(entry.get('title'))
        # TODO hack
        fe.link(href=html.unescape(entry.get('link')))
        fe.published(entry.get('date'))
        # date, content

    return fg.atom_str(pretty=True)


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
    s3_client = boto3.client('s3')
    response = s3_client.put_object(
        Body=xml_data,
        Bucket=options.get('bucket'),
        Key=options.get('object_name'),
        ContentType='text/xml',
        ACL='public-read',
    )


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Scrape webpages to make an RSS feed using just regex')
    parser.add_argument('feed', help='Feed key in settings.py')
    parser.add_argument('--s3', dest='upload_s3', action='store_true', help='Upload to S3')
    parser.add_argument('--debug', dest='debug', action='store_true')
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
            d['date'] = dateutil.parser.parse(d['date'])
            if options.get('timezone'):
                d['date'] = d['date'].replace(tzinfo=pytz.timezone(options.get('timezone')))
            if exclude(d):
                continue
            entries.append(d)
            print_entry(d)

    rss = generate_rss(entries, options)
    if args.debug:
        print(rss.decode())
    if args.upload_s3:
        upload_s3(rss, options.get('s3'))
        print('Success %s' % options.get('id'))
