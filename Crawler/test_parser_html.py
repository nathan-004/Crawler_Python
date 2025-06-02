import unittest
from web import RobotFileParser  # Assure-toi que le chemin est correct

class TestRobotFileParserWithGoogle(unittest.TestCase):
    def test_google_robots_txt(self):
        parser = RobotFileParser()
        parser.crawler_name = "*"  # Spécifie le nom de ton crawler
        parser.parse("https://www.google.com/")

        # URL bloquée pour Googlebot
        self.assertFalse(parser.is_allowed("https://www.google.com/search"))

        # URL autorisée pour Googlebot
        self.assertTrue(parser.is_allowed("https://www.google.com/search/about"))

        # URL autorisée pour Mediapartners-Google
        parser.crawler_name = "Mediapartners-Google"
        parser.parse("https://www.google.com/")
        self.assertTrue(parser.is_allowed("https://www.google.com/ads"))

if __name__ == "__main__":
    unittest.main()