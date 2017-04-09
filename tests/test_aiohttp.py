import concurrent
import unittest
import asyncio
import aiohttp

from run_scrapper import parse_html


class AsyncioHelloWordTest(unittest.TestCase):
    def setUp(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(None)

    def tearDown(self):
        self.loop.close()

    def test_dumb(self):
        loop = self.loop
        async def fetch_page(session, url):
            async with session.get(url) as response:
                return await response.text()

        async def parse_page(executor, base_url, html_doc):
            return await loop.run_in_executor(executor, parse_html, base_url, html_doc)

        #async def spy(executor, base_url, html_doc):




        async def main():
            with concurrent.futures.ProcessPoolExecutor(max_workers=3) as executor:
                async with aiohttp.ClientSession(loop=loop) as session:
                    base_url = 'http://python.org'
                    html_doc = await fetch_page(session, base_url)
                    links_assets = await parse_page(executor, base_url, html_doc)
                    print(links_assets[0])

                    # print(html)
                    return links_assets[0]
        html = loop.run_until_complete(main())
        self.assertIsNotNone(html, "python.org returns null")
        # print(html)

