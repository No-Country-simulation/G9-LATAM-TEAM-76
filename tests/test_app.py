import unittest

from app import app


class AppTestCase(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_home(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Analiza contenido", response.data)

    def test_api_returns_analysis(self):
        response = self.client.post("/api/contenido", json={"titulo": "Ciberseguridad", "texto": "encryption and vulnerability scanning"})
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertIn("categoria", payload)
        self.assertIn("probabilidad", payload)
        self.assertIn("palabras_clave", payload)

    def test_api_validates_empty_input(self):
        self.assertEqual(self.client.post("/api/contenido", json={}).status_code, 400)


if __name__ == "__main__":
    unittest.main()

