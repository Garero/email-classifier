"""
Módulo de serviços do Classificador de Emails.
Contém processamento NLP, leitura de PDF e lógica de classificação.
"""

from .text_processor import TextProcessor, process_email_text, clean_email_text

__all__ = [
    'TextProcessor',
    'process_email_text', 
    'clean_email_text'
]

__version__ = '2.2.0'