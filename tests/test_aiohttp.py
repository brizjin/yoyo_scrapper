import unittest
import asyncio
import aiohttp


class AsyncioHelloWordTest(unittest.TestCase):
    def setUp(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(None)

    def tearDown(self):
        self.loop.close()

    def test_dumb(self):
        async def fetch(session, url):
            with aiohttp.Timeout(10, loop=session.loop):
                async with session.get(url) as response:
                    return await response.text()

        async def main(loop):
            async with aiohttp.ClientSession(loop=loop) as session:
                html = await fetch(session, 'http://python.org')
                self.assertIsNotNone(html, "python.org returns null")
                print(html)

        # loop = asyncio.get_event_loop()
        # loop.run_until_complete(main(loop))
        self.loop.run_until_complete(main(self.loop))

