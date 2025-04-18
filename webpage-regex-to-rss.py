#!/usr/bin/env python3

import argparse
import urllib.request
import re
import urllib
import pytz
import http.cookiejar
import time
import random
import cloudscraper

from bs4 import BeautifulSoup
import boto3
from feedgen.feed import FeedGenerator
import dateutil

import settings


def get_entries(_html, parse_options):
    # pattern.finditer(_html):
    selector = parse_options.get('entry')
    if callable(selector):
        soup = BeautifulSoup(_html, 'html.parser')
        return [e.decode(formatter=None) for e in selector(soup)]
    else:
        raise NotImplementedError(type(selector))


def parse_entry(_html, parse_options):
    d = {}
    for field in parse_options.keys():
        if field == 'entry':
            # TODO hack
            continue
        d[field] = parse_field(_html, parse_options.get(field), field=field)
    return d


def parse_field(_html, selector, field=None):
    if type(selector) == str:
        match = re.findall(selector, _html)
        try:
            return match[0]
        except IndexError:
            return None
    elif callable(selector):
        soup = BeautifulSoup(_html, 'html.parser')
        result = selector(soup)
        if type(result) == str:
            return str(result)
        return result.decode(formatter=None)
    else:
        raise NotImplementedError(type(selector))


def format_link(base_url, link):
    link = urllib.parse.urljoin(base_url, link)
    return link


def format_date(date, timezone=None):
    if not date:
        return None
    date = dateutil.parser.parse(date)
    if timezone:
        date = date.replace(tzinfo=pytz.timezone(timezone))
    return date


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
        fe.link(href=entry.get('link'))
        fe.published(entry.get('date'))
        # date, content

    return fg.atom_str(pretty=True)


def print_entry(d):
    print('{date} {replies:4} {link} {title}'.format(**d))


def upload_s3(xml_data, options):
    s3_client = boto3.client('s3')
    response = s3_client.put_object(
        Body=xml_data,
        Bucket=options.get('bucket'),
        Key=options.get('object_name'),
        ContentType='text/xml',
        ACL='public-read',
    )


def get_scraper():
    return cloudscraper.create_scraper(browser={
        "browser": "chrome",
        "platform": "windows",
    })


def robust_get(url, retries=5, backoff=2):
    scraper = get_scraper()
    for attempt in range(retries):
        try:
            response = scraper.get(url, timeout=10)
            if response.status_code == 200:
                return response.text
            else:
                print(f"[{response.status_code}] on attempt {attempt + 1}")
        except Exception as ex:
            print(f"[Error] {ex} on attempt {attempt + 1}")
        time.sleep(backoff * (attempt + 1))
    raise Exception("Failed to retrieve URL after retries.")


def process_feed(feed):

    source_url = options.get('source_url')
    _html = robust_get(source_url)
    # _html = response.read().decode('utf-8')  # TODO: base on charset of doc
    parse_options = options.get('parse')
    exclude = options.get('exclude')
    entries = []
    for entry in get_entries(_html, parse_options):
        d = parse_entry(entry, parse_options)
        d['link'] = format_link(source_url, d['link'])
        d['date'] = format_date(d['date'], options.get('timezone'))
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


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Scrape webpages to make an RSS feed using just regex')
    parser.add_argument('feed', help='Feed key in settings.py')
    parser.add_argument('--s3', dest='upload_s3', action='store_true', help='Upload to S3')
    parser.add_argument('--debug', dest='debug', action='store_true')
    args = parser.parse_args()

    if args.feed == 'all':
        for options in settings.FEEDS.values():
            process_feed(options)
    else:
        options = settings.FEEDS[args.feed]
        process_feed(options)
