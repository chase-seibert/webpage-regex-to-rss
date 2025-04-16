#!/usr/bin/env python3

import argparse
import urllib.request
import re
import urllib
import pytz
import http.cookiejar
import time
import random

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


def resilient_request(source_url, retries=3):
    # Set up headers to mimic a modern browser
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }

    # Use a cookie jar to maintain session state
    cookie_jar = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(
        urllib.request.HTTPCookieProcessor(cookie_jar),
        urllib.request.HTTPRedirectHandler()
    )
    urllib.request.install_opener(opener)

    for attempt in range(retries):
        try:
            return urllib.request.urlopen(urllib.request.Request(source_url, headers=headers), timeout=10)
        except urllib.error.HTTPError as e:
            if e.code == 403:
                wait = random.uniform(2, 6)
                print(f"403 Forbidden. Retrying in {wait:.2f} seconds... (attempt {attempt+1}/{retries})")
                time.sleep(wait)
            else:
                raise

    raise Exception(f"Failed to fetch {source_url} after {retries} retries.")


def process_feed(feed):

    source_url = options.get('source_url')
    response = resilient_request(source_url)
    _html = response.read().decode('utf-8')  # TODO: base on charset of doc
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
