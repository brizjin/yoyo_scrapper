import asyncio
import concurrent
import logging
import unittest

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
        logging.basicConfig(level=logging.INFO, format='PID %(process)5s %(threadName)10s %(name)18s: %(message)s', stream=sys.stderr)

        async def fetch_page(session, url):
            log = logging.getLogger('fetch_page')
            async with session.get(url) as response:
                log.info('begin')
                r = await response.text()
                log.info('end')
                return r

        async def parse_page(executor, base_url, html_doc):
            log = logging.getLogger('parse_page')
            log.info('starting')
            r = await loop.run_in_executor(executor, parse_html, base_url, html_doc)
            log.info('ending')
            return r

        async def spy(executor, session, url):
            if self.i > 100:
                return
            self.i += 1
            if url in site_map:
                return

            print(self.i, url)
            html_doc = await fetch_page(session, url)
            links, assets = await parse_page(executor, url, html_doc)
            site_map[url] = assets
            for link in await asyncio.gather(*[spy(executor, session, link) for link in links]):
                pass

        async def main():
            with concurrent.futures.ProcessPoolExecutor(max_workers=8) as executor:
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
        # print(html)
