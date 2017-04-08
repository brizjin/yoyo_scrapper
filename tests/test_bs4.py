import unittest

import os
import re
from bs4 import BeautifulSoup, SoupStrainer
from urllib.parse import urljoin, urldefrag, urlparse
from run_scrapper import parse_html
from tld import get_tld


def read_data(file_name):
    return open(os.path.join(os.path.dirname(__file__), 'data', file_name), 'r').read()


class Bs4Test(unittest.TestCase):
    def test_get_links(self):
        html_doc = read_data("python.org.html")
        base_url = 'http://python.org'
        soup = BeautifulSoup(html_doc, 'lxml', parse_only=SoupStrainer('a'))
        links = [link.get('href') for link in soup.find_all('a')]  # find all a-tags and get href of it
        links = [urljoin(base_url, link) for link in links]  # convert relative links to absolute
        links = [link for link in links if get_tld(link, fail_silently=True) == get_tld(base_url)]
        links = sorted(set(urldefrag(link)[0].strip('/') for link in links))
        # print("\n".join(links))
        self.assertIsNotNone(links)

    def test_python_org(self):
        html_doc = read_data("python.org.html")
        links = parse_html('http://python.org', html_doc)
        self.assertEqual(links[0], "http://blog.python.org")
        self.assertEqual(links[74], "https://wiki.python.org/moin/PythonEventsCalendar")

    def test_yoyowallet_com(self):
        html_doc = read_data("yoyowallet.html")
        links = parse_html('http://yoyowallet.com', html_doc)
        self.assertEqual(links[0], "http://blog.yoyowallet.com")
        self.assertEqual(links[11], "https://support.yoyowallet.com/hc/en-gb/categories/201132913-Legal-and-T-Cs")
