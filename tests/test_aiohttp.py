import asyncio
import concurrent
import logging
import unittest
from logging import FileHandler
import requests

import aiohttp
import sys

from run_scrapper import parse_html


class AsyncioHelloWordTest(unittest.TestCase):
    def setUp(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(None)

    def tearDown(self):
        self.loop.close()

    def test_dumb(self):
        loop = self.loop
        site_map = {}
        self.i = 0
        thread_pool = concurrent.futures.ThreadPoolExecutor(max_workers=256)

        async def fetch_page(session, url):
            # log = logging.getLogger('fetch_page')
            async with session.get(url) as response:
                # log.info('begin')
                r = await response.text()
                # log.info('end')
                return r

        async def fetch_request(executor, url):
            r = await loop.run_in_executor(executor, requests.get, url)
            return r.content

        # async def test():
        #     print("TEST")
        #     # log = logging.getLogger('test')
        #     # log.debug('test')
        #     r = 1

        async def parse_page(executor, base_url, html_doc):

            # log_parse_page.info('starting')
            r = await loop.run_in_executor(executor, parse_html, base_url, html_doc)
            #r = await loop.run_in_executor(executor, test)
            # log_parse_page.info('ending')
            return r

        async def spy(executor, session, url):

            if url in site_map:
                return
            if self.i > 100:
                return
            self.i += 1
            site_map[url] = None
            # log_spy.info(str(self.i) + " " + url)
            # html_doc = await fetch_page(session, url)
            html_doc = await fetch_request(thread_pool, url)
            links, assets = await parse_page(executor, url, html_doc)
            site_map[url] = assets
            await asyncio.gather(*[spy(executor, session, link) for link in links])

        async def main():
            with concurrent.futures.ProcessPoolExecutor(max_workers=32) as executor:
                async with aiohttp.ClientSession(loop=loop) as session:
                    base_url = 'http://python.org'
                    await spy(executor, session, base_url)
                    # html_doc = await fetch_page(session, base_url)
                    # links_assets = await parse_page(executor, base_url, html_doc)
                    # print(links_assets[0])
                    #
                    # # print(html)
                    # return links_assets[0]
                    return site_map

        html = loop.run_until_complete(main())
        # print(html)
        self.assertIsNotNone(html, "python.org returns null")
        print(html.keys())
        print(html[list(html.keys())[10]])
