"""
Módulo de processamento de linguagem natural (NLP) para emails.
Implementa técnicas avançadas: tokenização, remoção de stop words,
stemming, lemmatização e limpeza de texto.
"""

import re
import unicodedata
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

# Stop words em português brasileiro (palavras comuns sem valor semântico)
STOP_WORDS_PT = {
    'a', 'o', 'e', 'é', 'de', 'da', 'do', 'em', 'um', 'uma', 'os', 'as', 'dos', 'das',
    'para', 'com', 'por', 'sem', 'sob', 'sobre', 'ao', 'aos', 'à', 'às', 'no', 'na',
    'nos', 'nas', 'pelo', 'pela', 'pelos', 'pelas', 'que', 'qual', 'quando', 'onde',
    'como', 'se', 'mas', 'mais', 'menos', 'muito', 'pouco', 'todo', 'toda', 'todos',
    'todas', 'outro', 'outra', 'outros', 'outras', 'mesmo', 'mesma', 'mesmos', 'mesmas',
    'tal', 'tais', 'este', 'esta', 'estes', 'estas', 'esse', 'essa', 'esses', 'essas',
    'aquele', 'aquela', 'aqueles', 'aquelas', 'isto', 'isso', 'aquilo', 'eu', 'tu',
    'ele', 'ela', 'nós', 'vós', 'eles', 'elas', 'me', 'te', 'se', 'lhe', 'nos', 'vos',
    'lhes', 'meu', 'minha', 'meus', 'minhas', 'teu', 'tua', 'teus', 'tuas', 'seu',
    'sua', 'seus', 'suas', 'nosso', 'nossa', 'nossos', 'nossas', 'vosso', 'vossa',
    'vossos', 'vossas', 'ser', 'estar', 'ter', 'haver', 'fazer', 'ir', 'poder', 'dar',
    'ver', 'saber', 'querer', 'dizer', 'olá', 'oi', 'obrigado', 'obrigada', 'por favor',
    'att', 'atenciosamente', 'cordialmente', 'abs', 'abraço', 'abraços'
}

# Dicionário de stemming simples (sufixos comuns em português)
STEMMING_RULES = [
    ('amente', ''),      # rapidamente -> rapid
    ('mente', ''),       # felizmente -> feliz
    ('ação', ''),        # solicitação -> solicit
    ('ções', ''),        # solicitações -> solicit
    ('ador', ''),        # trabalhador -> trabalh
    ('ante', ''),        # estudante -> estud
    ('ência', ''),       # urgência -> urg
    ('ância', ''),       # importância -> import
    ('ismo', ''),        # capitalismo -> capital
    ('ista', ''),        # dentista -> dent
    ('oso', ''),         # generoso -> gener
    ('osa', ''),         # generosa -> gener
    ('ivo', ''),         # produtivo -> produt
    ('iva', ''),         # produtiva -> produt
    ('mente', ''),       # certamente -> cert
    ('idade', ''),       # rapidez -> rapid
    ('ar', ''),          # trabalhar -> trabalh
    ('er', ''),          # fazer -> faz
    ('ir', ''),          # partir -> part
]


class TextProcessor:
    """Processador de texto com técnicas de NLP"""
    
    def __init__(self, remove_stopwords: bool = True, apply_stemming: bool = True):
        """
        Inicializa o processador de texto.
        
        Args:
            remove_stopwords: Se True, remove stop words
            apply_stemming: Se True, aplica stemming
        """
        self.remove_stopwords = remove_stopwords
        self.apply_stemming = apply_stemming
        self.stop_words = STOP_WORDS_PT
        
    def normalize_text(self, text: str) -> str:
        """
        Normaliza texto removendo acentos e caracteres especiais.
        
        Args:
            text: Texto a ser normalizado
            
        Returns:
            Texto normalizado
        """
        # Converte para lowercase
        text = text.lower()
        
        # Remove acentos (mantém ç)
        nfkd = unicodedata.normalize('NFKD', text)
        text = ''.join([c for c in nfkd if not unicodedata.combining(c)])
        
        return text
    
    def tokenize(self, text: str) -> List[str]:
        """
        Tokeniza o texto em palavras individuais.
        
        Args:
            text: Texto a ser tokenizado
            
        Returns:
            Lista de tokens (palavras)
        """
        # Remove pontuação e caracteres especiais, mantendo apenas palavras
        text = re.sub(r'[^\w\s]', ' ', text)
        
        # Divide em tokens (palavras)
        tokens = text.split()
        
        # Remove tokens vazios
        tokens = [t for t in tokens if t.strip()]
        
        return tokens
    
    def remove_stop_words(self, tokens: List[str]) -> List[str]:
        """
        Remove stop words (palavras comuns sem valor semântico).
        
        Args:
            tokens: Lista de tokens
            
        Returns:
            Lista de tokens sem stop words
        """
        return [t for t in tokens if t.lower() not in self.stop_words]
    
    def stem_word(self, word: str) -> str:
        """
        Aplica stemming em uma palavra (reduz à raiz).
        
        Args:
            word: Palavra a ser processada
            
        Returns:
            Palavra com stemming aplicado
        """
        word_lower = word.lower()
        
        # Aplica regras de stemming
        for suffix, replacement in STEMMING_RULES:
            if word_lower.endswith(suffix) and len(word_lower) > len(suffix) + 2:
                return word_lower[:-len(suffix)] + replacement
        
        return word_lower
    
    def stem_tokens(self, tokens: List[str]) -> List[str]:
        """
        Aplica stemming em uma lista de tokens.
        
        Args:
            tokens: Lista de tokens
            
        Returns:
            Lista de tokens com stemming aplicado
        """
        return [self.stem_word(t) for t in tokens]
    
    def extract_keywords(self, text: str, top_n: int = 10) -> List[str]:
        """
        Extrai palavras-chave mais relevantes do texto.
        
        Args:
            text: Texto para análise
            top_n: Número de palavras-chave a retornar
            
        Returns:
            Lista de palavras-chave mais frequentes
        """
        # Normaliza e tokeniza
        normalized = self.normalize_text(text)
        tokens = self.tokenize(normalized)
        
        # Remove stop words
        if self.remove_stopwords:
            tokens = self.remove_stop_words(tokens)
        
        # Aplica stemming
        if self.apply_stemming:
            tokens = self.stem_tokens(tokens)
        
        # Conta frequência
        freq = {}
        for token in tokens:
            if len(token) > 2:  # Ignora palavras muito curtas
                freq[token] = freq.get(token, 0) + 1
        
        # Ordena por frequência
        sorted_keywords = sorted(freq.items(), key=lambda x: x[1], reverse=True)
        
        return [kw[0] for kw in sorted_keywords[:top_n]]
    
    def preprocess(self, text: str) -> Dict[str, any]:
        """
        Pipeline completo de pré-processamento NLP.
        
        Args:
            text: Texto original
            
        Returns:
            Dicionário com resultados do processamento:
            - original: texto original
            - normalized: texto normalizado
            - tokens: lista de tokens
            - tokens_clean: tokens sem stop words
            - tokens_stemmed: tokens com stemming
            - keywords: palavras-chave extraídas
            - statistics: estatísticas do texto
        """
        try:
            # 1. Normalização
            normalized = self.normalize_text(text)
            
            # 2. Tokenização
            tokens = self.tokenize(normalized)
            
            # 3. Remoção de stop words
            tokens_clean = self.remove_stop_words(tokens) if self.remove_stopwords else tokens
            
            # 4. Stemming
            tokens_stemmed = self.stem_tokens(tokens_clean) if self.apply_stemming else tokens_clean
            
            # 5. Extração de palavras-chave
            keywords = self.extract_keywords(text)
            
            # 6. Estatísticas
            statistics = {
                'original_length': len(text),
                'token_count': len(tokens),
                'unique_tokens': len(set(tokens)),
                'tokens_after_stopwords': len(tokens_clean),
                'tokens_after_stemming': len(tokens_stemmed),
                'keyword_count': len(keywords)
            }
            
            logger.info(f"Texto processado: {statistics['token_count']} tokens, "
                       f"{statistics['keyword_count']} keywords extraídas")
            
            return {
                'original': text,
                'normalized': normalized,
                'tokens': tokens,
                'tokens_clean': tokens_clean,
                'tokens_stemmed': tokens_stemmed,
                'keywords': keywords,
                'statistics': statistics,
                'processed_text': ' '.join(tokens_stemmed)  # Texto processado final
            }
            
        except Exception as e:
            logger.error(f"Erro no pré-processamento NLP: {str(e)}")
            return {
                'original': text,
                'error': str(e)
            }


def clean_email_text(text: str) -> str:
    """
    Limpeza específica para emails (remove assinaturas, disclaimers, etc).
    
    Args:
        text: Texto do email
        
    Returns:
        Texto limpo
    """
    # Remove múltiplas quebras de linha
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    # Remove múltiplos espaços
    text = re.sub(r' {2,}', ' ', text)
    
    # Remove linhas com apenas símbolos
    text = re.sub(r'^[^\w\s]+$', '', text, flags=re.MULTILINE)
    
    # Remove URLs
    text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
    
    # Remove emails
    text = re.sub(r'\S+@\S+', '', text)
    
    # Remove números de telefone
    text = re.sub(r'\(?\d{2}\)?\s?\d{4,5}-?\d{4}', '', text)
    
    return text.strip()


# Função de conveniência para uso rápido
def process_email_text(text: str) -> Dict[str, any]:
    """
    Função helper para processar texto de email rapidamente.
    
    Args:
        text: Texto do email
        
    Returns:
        Dicionário com resultado do processamento
    """
    # Limpa o email primeiro
    cleaned = clean_email_text(text)
    
    # Processa com NLP
    processor = TextProcessor(remove_stopwords=True, apply_stemming=True)
    result = processor.preprocess(cleaned)
    
    return result


# Exemplo de uso
if __name__ == "__main__":
    # Teste com email exemplo
    email_exemplo = """
    Prezados,
    
    Estou entrando em contato para solicitar urgentemente o status da minha 
    requisição #12345 que foi aberta na última segunda-feira. O sistema está 
    apresentando erros críticos e preciso de uma solução imediata.
    
    Agradeço antecipadamente pela atenção.
    
    Atenciosamente,
    João Silva
    joao.silva@empresa.com
    (11) 98765-4321
    """
    
    result = process_email_text(email_exemplo)
    
    print("="*50)
    print("PROCESSAMENTO NLP - EXEMPLO")
    print("="*50)
    print(f"\n📊 Estatísticas:")
    for key, value in result['statistics'].items():
        print(f"  • {key}: {value}")
    
    print(f"\n🔑 Palavras-chave extraídas:")
    print(f"  {', '.join(result['keywords'][:5])}")
    
    print(f"\n✨ Texto processado (stemming + sem stopwords):")
    print(f"  {result['processed_text'][:100]}...")