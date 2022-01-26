#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
from datetime import date

import requests

BASE_URL = 'dallascityhall.com/government/citysecretary/Pages/'
MP3_URL = 'citysecretary2.dallascityhall.com/mp3/download.asp?'
PATTERN = re.compile(MP3_URL + r'.*\.mp3')


def get_urls(year):
    r = requests.get(f'https://{BASE_URL}/CCMeetings_{year}.aspx')
    html = r.text
    urls = PATTERN.findall(html)

    return urls


if __name__ == '__main__':
    # Get all current URLs
    min_yr = 2008  # Earliest year of available recordings
    max_yr = date.today().year
    urls = dict()

    for year in list(range(min_yr, max_yr)):
        urls[year] = get_urls(year)

    for year in urls.keys():
        for match in urls[year]:
            print(PATTERN.findall(match))

