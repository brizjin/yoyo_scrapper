import unittest

import os
import re
from bs4 import BeautifulSoup, SoupStrainer
from urllib.parse import urljoin, urldefrag


def read_data(file_name):
    return open(os.path.join(os.path.dirname(__file__), 'data', file_name), 'r').read()


class Bs4Test(unittest.TestCase):
    def test_from_data(self):
        base_url = 'http://python.org'
        html_doc = read_data("python.org.html")
        soup = BeautifulSoup(html_doc, 'lxml', parse_only=SoupStrainer('a'))
        links = [link.get('href') for link in soup.find_all('a')]           # find all a-tags and get href of it
        absolute_links = [urljoin(base_url, link) for link in links]        # convert relative links to absolute
        self.assertIsNotNone(absolute_links, "absolute links should not be null")
        # remove external links, remove fragment from url, distinct links
        r = re.compile('^' + base_url)
        # noinspection PyTypeChecker
        links = set(urldefrag(link)[0].strip('/') for link in filter(r.match, absolute_links))
        # f = []

        print("\n".join(sorted(links)))
        print(links)
