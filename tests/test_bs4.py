import asyncio
import unittest

import os
from bs4 import BeautifulSoup, SoupStrainer
from urllib.parse import urljoin


def read_data(file_name):
    return open(os.path.join(os.path.dirname(__file__), 'data', file_name), 'r').read()


class Bs4Test(unittest.TestCase):
    def test_from_data(self):
        base_url = 'http://python.org'
        html_doc = read_data("python.org.html")
        soup = BeautifulSoup(html_doc, 'lxml', parse_only=SoupStrainer('a'))
        links = [link.get('href') for link in soup.find_all('a')]
        absolute_links = [urljoin(base_url, link) for link in links]
        print("\n".join(sorted(absolute_links)))
        self.assertIsNotNone(absolute_links, "absolute links should not be null")
