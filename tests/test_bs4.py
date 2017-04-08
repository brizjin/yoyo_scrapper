import unittest

import os
from bs4 import BeautifulSoup, SoupStrainer
from tld import get_tld
from urllib.parse import urljoin, urldefrag

from run_scrapper import parse_html


def read_data(file_name):
    return open(os.path.join(os.path.dirname(__file__), 'data', file_name), 'r').read()


class Bs4Test(unittest.TestCase):
    def setUp(self):
        self.py_file = read_data("python.org.html")
        self.py_url = 'http://python.org'
        self.yoyo_file = read_data("yoyowallet.html")
        self.yoyo_url = 'http://yoyowallet.com'

    def test_py_get_links(self):
        soup = BeautifulSoup(self.py_file, 'lxml', parse_only=SoupStrainer('a'))
        links = [link.get('href') for link in soup.find_all('a')]  # find all a-tags and get href of it
        links = [urljoin(self.py_url, link) for link in links]  # convert relative links to absolute
        links = [link for link in links if get_tld(link, fail_silently=True) == get_tld(self.py_url)]
        links = sorted(set(urldefrag(link)[0].strip('/') for link in links))
        # print("\n".join(links))
        self.assertIsNotNone(links)

    def test_py_get_links_func(self):
        links = parse_html(self.py_url, self.py_file)[0]
        self.assertEqual(links[0], "http://blog.python.org")
        self.assertEqual(links[74], "https://wiki.python.org/moin/PythonEventsCalendar")

    def test_yoyo_get_links_func(self):
        html_doc = read_data("yoyowallet.html")
        links = parse_html('http://yoyowallet.com', html_doc)[0]
        self.assertEqual(links[0], "http://blog.yoyowallet.com")
        self.assertEqual(links[11], "https://support.yoyowallet.com/hc/en-gb/categories/201132913-Legal-and-T-Cs")

    def test_yoyo_get_asserts(self):
        # <a href="*" />, <link rel="*" />, <img src="*" />, <script src="*" />
        soup = BeautifulSoup(self.yoyo_file, 'lxml', parse_only=SoupStrainer(['a', 'link', 'img', 'script']))
        assets = [tag.get('href') for tag in soup.find_all(['a', 'link'])]
        assets += [tag.get('src') for tag in soup.find_all(['img', 'script'])]
        assets = sorted(set(urljoin(self.yoyo_url, asset.strip('/')) for asset in assets if asset is not None))
        # print("\n".join(assets))
        self.assertIsNotNone(assets)
        self.assertEqual(assets[0], "http://blog.yoyowallet.com")
        self.assertEqual(assets[70], "https://support.yoyowallet.com/hc/en-gb/categories/201132913-Legal-and-T-Cs")

    def test_yoyo_get_asserts_by_func(self):
        assets = parse_html(self.yoyo_url, self.yoyo_file)[1]
        # print("\n".join(assets))
        # for asset in assets:
        #     print(get_tld(asset, fail_silently=True), asset)
        self.assertIsNotNone(assets)
        self.assertEqual(assets[0], "http://blog.yoyowallet.com")
        self.assertEqual(assets[70], "https://support.yoyowallet.com/hc/en-gb/categories/201132913-Legal-and-T-Cs")

    def test_py_get_asserts_by_func(self):
        assets = parse_html(self.py_url, self.py_file)[1]
        #print("\n".join(assets))
        # for asset in assets:
        #     print(get_tld(asset, fail_silently=True), asset)
        self.assertIsNotNone(assets)
        self.assertEqual(len(assets), 134)
        self.assertEqual(assets[0], "http://blog.python.org")
        self.assertEqual(assets[133], "https://www.openstack.org")


