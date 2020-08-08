import unittest
import research


class TestResearch(unittest.TestCase):
    def test_format_authors(self):
        self.assertEqual(
            "Hello, world!", research.format_authors("Hello, world!")
        )


if __name__ == "__main__":
    unittest.main()
