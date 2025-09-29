import unittest
import sys
import os

# Garante que a pasta services está no path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'services')))

from text_processor import process_email_text, TextProcessor

class TestProcessEmailText(unittest.TestCase):

    def test_process_email_text_simples(self):
        texto = "Olá, este é um email de teste."
        resultado = process_email_text(texto)

        # Deve retornar um dicionário com chaves esperadas
        self.assertIsInstance(resultado, dict)
        self.assertIn("original", resultado)
        self.assertIn("normalized", resultado)
        self.assertIn("tokens", resultado)

        # Normalizado não deve estar vazio
        self.assertTrue(isinstance(resultado["normalized"], str))
        self.assertNotEqual(resultado["normalized"], "")

    def test_process_email_text_vazio(self):
        texto = ""
        resultado = process_email_text(texto)

        self.assertIsInstance(resultado, dict)
        self.assertEqual(resultado["normalized"], "")
        self.assertEqual(resultado["tokens"], [])

    def test_process_email_text_html(self):
        texto = "<p>Mensagem <b>importante</b></p>"
        resultado = process_email_text(texto)

        self.assertIsInstance(resultado, dict)
        self.assertNotIn("<p>", resultado["normalized"])
        self.assertIn("mensagem", resultado["normalized"].lower())

class TestTextProcessor(unittest.TestCase):

    def setUp(self):
        self.processor = TextProcessor()

    def test_instanciacao(self):
        # Apenas garante que a classe inicializa sem erro
        self.assertIsInstance(self.processor, TextProcessor)

    def test_tokenize_existente(self):
        if hasattr(self.processor, "tokenize"):
            tokens = self.processor.tokenize("Email de teste simples")
            self.assertIsInstance(tokens, list)
            self.assertIn("email", [t.lower() for t in tokens])

def test_atributos_basicos(self):
    # Verifica se atributos reais existem
    self.assertTrue(hasattr(self.processor, "remove_stopwords"))
    self.assertTrue(hasattr(self.processor, "apply_stemming"))
    self.assertTrue(hasattr(self.processor, "stop_words"))

