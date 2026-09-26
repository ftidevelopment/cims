import unittest

from flask import Flask

from app import create_app


class CreateAppTests(unittest.TestCase):
    def test_create_app_returns_flask_instance(self):
        app = create_app()

        self.assertIsInstance(app, Flask)
        self.assertEqual(app.name, "app")


if __name__ == "__main__":
    unittest.main()
