import os
import unittest
from unittest.mock import patch, MagicMock

from src.app import app

# The full response for example_recipe.html. The opencookbook apiserver reads this response
# into typed fields, so a field that silently turns into "" (which is what get_info returns
# whenever recipe-scrapers raises) can fail every import there - "nutrients": "" or
# "ingredients": "" do. Dependency updates are merged and released without review, so the
# whole response is pinned: an update that changes any field fails CI instead of shipping.
# If an update changes the output on purpose, check the change and update this.
EXPECTED_RECIPE = {
    "author": "Mary Stone",
    "category": "Drink",
    "cook_time": 2,
    "cuisine": "American",
    "host": "example.com",
    "image": "https://example.com/photos/1x1/photo.jpg",
    "ingredients": [
        "400ml of pineapple juice",
        "100ml cream of coconut",
        "ice",
    ],
    "instructions": "Blend 400ml of pineapple juice and 100ml cream of coconut until smooth.\n"
                    "Fill a glass with ice.\n"
                    "Pour the pineapple juice and coconut mixture over ice.",
    "language": "en",
    "links": [],
    "nutrients": {
        "calories": "120 calories",
    },
    "prep_time": 1,
    "ratings": 5.0,
    "title": "Non-Alcoholic Piña Colada",
    "total_time": 3,
    "yields": "4 servings",
}


class AppTestCase(unittest.TestCase):

    maxDiff = None

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_get_supported_hosts(self):
        response = self.app.get('/api/v1/scrape-recipe/supported-hosts')
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json, list)

    @patch('src.app.requests.get')
    def test_import_recipe(self, mock_get):
        file_path = os.path.join(os.path.dirname(__file__), 'example_recipe.html')
        with open(file_path, 'r', encoding='utf-8') as file:
            mock_get.return_value = MagicMock(content=file.read())

        response = self.app.get('/api/v1/scrape-recipe?url=http://example.com/recipe')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, EXPECTED_RECIPE)

    @patch('src.app.requests.get')
    def test_import_recipe_no_url(self, mock_get):
        response = self.app.get('/api/v1/scrape-recipe')
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json)

    @patch('src.app.requests.get')
    def test_import_recipe_invalid_url(self, mock_get):
        mock_get.side_effect = Exception("Invalid URL")
        response = self.app.get('/api/v1/scrape-recipe?url=http://invalid-url.com')
        self.assertEqual(response.status_code, 501)


if __name__ == '__main__':
    unittest.main()
