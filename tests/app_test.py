import unittest
from unittest.mock import patch, MagicMock
from flask import Flask
import os
import unittest
from unittest.mock import patch, MagicMock
from flask import Flask
from src.app import app


class AppTestCase(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_get_supported_hosts(self):
        response = self.app.get('/api/v1/scrape-recipe/supported-hosts')
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json, list)

    @patch('app.requests.get')
    def test_import_recipe(self, mock_get):
        file_path = os.path.join(os.path.dirname(__file__), 'example_recipe.html')
        with open(file_path, 'r') as file:
            mock_html_content = file.read()
            mock_response = MagicMock()
            mock_response.content = mock_html_content
            mock_get.return_value = mock_response

            response = self.app.get('/api/v1/scrape-recipe?url=http://example.com/recipe')
            self.assertEqual(response.status_code, 200)
            self.assertIn('title', response.json)
            self.assertIn('ingredients', response.json)
            self.assertEqual(response.json['title'], 'Non-Alcoholic Piña Colada')
            self.assertEqual(response.json['author'], 'Mary Stone')
            self.assertEqual(response.json['total_time'], 3)
            self.assertEqual(response.json['cook_time'], 2)
            self.assertEqual(response.json['prep_time'], 1)
            self.assertEqual(response.json['yields'], '4 servings')
            self.assertEqual(response.json['category'], 'Drink')
            self.assertEqual(response.json['cuisine'], 'American')
            self.assertEqual(response.json['ratings'], 5)
            self.assertEqual(response.json['ingredients'], [
                "400ml of pineapple juice",
                "100ml cream of coconut",
                "ice"
            ])
            self.assertEqual(response.json['instructions'], "Blend 400ml of pineapple juice and 100ml cream of coconut until smooth.\nFill a glass with ice.\nPour the pineapple juice and coconut mixture over ice.")

    @patch('app.requests.get')
    def test_import_recipe_no_url(self, mock_get):
        response = self.app.get('/api/v1/scrape-recipe')
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json)

    @patch('app.requests.get')
    def test_import_recipe_invalid_url(self, mock_get):
        mock_get.side_effect = Exception("Invalid URL")
        response = self.app.get('/api/v1/scrape-recipe?url=http://invalid-url.com')
        self.assertEqual(response.status_code, 501)

if __name__ == '__main__':
    unittest.main()