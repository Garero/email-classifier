import unittest
import sys
import os

# Garante que a pasta services está no path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'services')))

from text_processor import (
    TextProcessor,
    clean_email_text,
    process_email_text
)

class TestTextProcessorMethods(unittest.TestCase):

    def setUp(self):
        self.processor = TextProcessor()

    def test_normalize_text(self):
        texto = "Olá, MUNDO! Árvore"
        resultado = self.processor.normalize_text(texto)
        self.assertEqual(resultado, "ola, mundo! arvore")

    def test_tokenize(self):
        texto = "Email de teste, com pontuação!"
        tokens = self.processor.tokenize(texto)
        self.assertIn("Email".lower(), [t.lower() for t in tokens])
        self.assertNotIn(",", tokens)

    def test_remove_stop_words(self):
        tokens = ["este", "é", "um", "teste"]
        filtrados = self.processor.remove_stop_words(tokens)
        self.assertIn("teste", filtrados)
        self.assertNotIn("um", filtrados)

    def test_stem_word(self):
        self.assertEqual(self.processor.stem_word("solicitação"), "solicit")
        self.assertEqual(self.processor.stem_word("urgência"), "urg")

    def test_stem_tokens(self):
        tokens = ["solicitação", "urgência"]
        resultado = self.processor.stem_tokens(tokens)
        self.assertIn("solicit", resultado)
        self.assertIn("urg", resultado)

    def test_extract_keywords(self):
        texto = "Erro no sistema. O sistema apresentou erro crítico."
        keywords = self.processor.extract_keywords(texto, top_n=3)
        self.assertIn("erro", keywords)
        self.assertIn("sistema", keywords)

    def test_classify_by_keywords_produtivo(self):
        texto = "O sistema apresentou um erro urgente no pagamento."
        resultado = self.processor.classify_by_keywords(texto)
        self.assertEqual(resultado["category"], "Produtivo")
        self.assertGreaterEqual(resultado["productive_count"], 1)

    def test_classify_by_keywords_improdutivo(self):
        texto = "Bom dia, parabéns pelo excelente trabalho!"
        resultado = self.processor.classify_by_keywords(texto)
        self.assertEqual(resultado["category"], "Improdutivo")
        self.assertGreaterEqual(resultado["unproductive_count"], 1)

    def test_preprocess_pipeline(self):
        texto = "Solicito urgente suporte no sistema de pagamento."
        resultado = self.processor.preprocess(texto)
        self.assertIn("normalized", resultado)
        self.assertIn("tokens", resultado)
        self.assertIn("classification", resultado)
        self.assertEqual(resultado["classification"]["category"], "Produtivo")

class TestHelperFunctions(unittest.TestCase):

    def test_clean_email_text(self):
        texto = """
        Prezado cliente,
        Acesse http://exemplo.com para mais informações.
        Contato: suporte@empresa.com
        Tel: (11) 91234-5678
        Obrigado!
        """
        resultado = clean_email_text(texto)
        self.assertNotIn("http", resultado)
        self.assertNotIn("@", resultado)
        self.assertNotIn("91234", resultado)
        self.assertIn("obrigado", resultado)

    def test_process_email_text(self):
        texto = "Preciso de suporte urgente no sistema de pagamento."
        resultado = process_email_text(texto)
        self.assertIsInstance(resultado, dict)
        self.assertIn("classification", resultado)
        self.assertEqual(resultado["classification"]["category"], "Produtivo")

    def test_preprocess_fallback(self):
        processor = TextProcessor()
        # Força erro passando None
        resultado = processor.preprocess(None)

        # Deve retornar um dicionário mesmo em caso de erro
        self.assertIsInstance(resultado, dict)
        self.assertIn("error", resultado)

        # Classificação padrão de fallback deve ser Produtivo
        self.assertEqual(resultado["classification"]["category"], "Produtivo")
        self.assertEqual(resultado["classification"]["confidence"], 0.5)

       
def test_preprocess_method_exists(self):
    """Verifica se o método preprocess existe"""
    processor = TextProcessor()
    self.assertTrue(hasattr(processor, 'preprocess'))
    self.assertTrue(callable(getattr(processor, 'preprocess')))

    
def test_clean_email_text_complex(self):
    """Testa limpeza de email com conteúdo complexo"""
    complex_email = """
    Olá! 
    Acesse https://exemplo.com para mais detalhes.
    Meu email: usuario@empresa.com
    Telefone: (11) 98765-4321
    Att.,
    João
    """
    result = clean_email_text(complex_email)
    self.assertNotIn("https://", result)
    self.assertNotIn("@", result)
    self.assertNotIn("98765", result)

def test_classify_edge_cases(self):
    """Testa casos limite de classificação"""
    processor = TextProcessor()
    
    # Email vazio
    result = processor.preprocess("")
    self.assertEqual(result["classification"]["category"], "Produtivo")
    
    # Email com apenas stop words
    result = processor.preprocess("o e um para com")
    self.assertEqual(result["classification"]["category"], "Produtivo")


if __name__ == "__main__":
    unittest.main()
