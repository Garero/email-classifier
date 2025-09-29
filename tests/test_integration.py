import unittest
from services.text_processor import process_email_text

class TestIntegration(unittest.TestCase):
    def test_full_pipeline_produtivo(self):
        email = "URGENTE: Sistema com erro crítico, não consigo acessar"
        result = process_email_text(email)
        self.assertEqual(result["classification"]["category"], "Produtivo")
        self.assertGreater(result["classification"]["confidence"], 0.6)

    def test_full_pipeline_improdutivo(self):
        email = "Parabéns pelo excelente trabalho! Obrigado"
        result = process_email_text(email)
        self.assertEqual(result["classification"]["category"], "Improdutivo")