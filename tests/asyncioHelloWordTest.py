import unittest
import asyncio


class AsyncioHelloWordTest(unittest.TestCase):
    def setUp(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(None)

    def tearDown(self):
        self.loop.close()

    def test_dumb(self):
        async def func():
            self.assertEqual(42, 42)
        self.loop.run_until_complete(func())
