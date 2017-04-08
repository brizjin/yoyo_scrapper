import unittest


class FirstTest(unittest.TestCase):
    def test_dumb(self):
        self.assertEqual(1, 1, "First test error")
