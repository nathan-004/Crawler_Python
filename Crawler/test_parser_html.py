import unittest
from web import RobotFileParser, WebScrapping

class TestRobotFileParserWithGoogle(unittest.TestCase):
    def test_google_robots_txt(self):
        parser = RobotFileParser()
        parser.crawler_name = "*" 
        parser.parse("https://www.google.com/")

        self.assertFalse(parser.is_allowed("https://www.google.com/search"))
        self.assertTrue(parser.is_allowed("https://www.google.com/search/about"))

        parser.crawler_name = "Mediapartners-Google"
        parser.parse("https://www.google.com/")
        self.assertTrue(parser.is_allowed("https://www.google.com/ads"))


class TestIsValidUrlFormat(unittest.TestCase):
    def setUp(self):
        self.web = WebScrapping()

    def test_valid_urls(self):
        valid_urls = [
            "https://www.google.com",
            "http://example.com",
            "https://sub.domain.co.uk",
            "https://example.com/page.html",
            "https://example.com/page.test.html",
            "https://example.com/page.test.html?query=1",
            "https://example.com/path/to/file.txt",
            "http://127.0.0.1:8000",
            "https://localhost:5000",
            "https://www.site.com/file.name.with.many.dots.html",
            "https://my.site.com/images/image.v2.0.jpg",
            "https://api.example.com/v1.0/users"
        ]
        for url in valid_urls:
            with self.subTest(url=url):
                self.assertTrue(self.web.is_valide_url_format(url), f"Should be valid: {url}")

    def test_invalid_urls(self):
        invalid_urls = [
            "htp://www.google.com",
            "https:/www.google.com",
            "https://",
            "example.com",
            "www.example",
            "http://.",
            "ftp://example.com",
            "http://site..com",
            "https://?q=test",
            "https://.com",
            "https://google..com/page",
            "https://google.com/..",
        ]

        for url in invalid_urls:
            with self.subTest(url=url):
                self.assertFalse(self.web.is_valide_url_format(url), f"Should be invalid: {url}")

if __name__ == "__main__":
    unittest.main()