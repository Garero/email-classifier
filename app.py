from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os
from werkzeug.utils import secure_filename
import fitz
from groq import Groq
import re
from datetime import datetime
from dotenv import load_dotenv
import logging
import json
from services.text_processor import TextProcessor, process_email_text, clean_email_text

load_dotenv()

app = Flask(__name__)
CORS(app)

# Configurações
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB max
ALLOWED_EXTENSIONS = {'txt', 'pdf'}

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Inicializar cliente Groq
groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

#Inicializar processador NLP
nlp_processor = TextProcessor(remove_stopwords=True, apply_stemming=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_pdf(file_stream):
    """Extrai texto de PDF diretamente do stream de arquivo"""
    try:
        doc = fitz.open(stream=file_stream.read(), filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        return text.strip()
    except Exception as e:
        raise Exception(f"Erro ao ler PDF: {str(e)}")

def extract_text_from_txt(file_stream):
    """Extrai texto de arquivo TXT"""
    try:
        return file_stream.read().decode('utf-8').strip()
    except UnicodeDecodeError:
        try:
            file_stream.seek(0)
            return file_stream.read().decode('latin-1').strip()
        except Exception as e:
            raise Exception(f"Erro ao ler arquivo texto: {str(e)}")

def preprocess_text(text):
    """
    Pré-processamento avançado com NLP.
    Aplica: limpeza, tokenização, remoção de stop words, stemming.
    """
    try:
        #Usa o processador NLP completo
        cleaned = clean_email_text(text)
        nlp_result = nlp_processor.preprocess(cleaned)
        
        logger.info(f"📊 NLP Stats: {nlp_result['statistics']['token_count']} tokens, "
                   f"{len(nlp_result['keywords'])} keywords: {', '.join(nlp_result['keywords'][:5])}")
        
        # Retorna o texto original limpo (para enviar à IA) 
        # e os dados NLP processados (para análise)
        return cleaned, nlp_result
        
    except Exception as e:
        logger.error(f"Erro no pré-processamento NLP: {str(e)}")
        # Fallback para limpeza básica
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'[^\w\s\.,!?;:\-@áàâãéêíóôõúçÁÀÂÃÉÊÍÓÔÕÚÇ]', '', text)
        return text.strip(), None

def classify_with_ai(email_text, nlp_data=None):
    """
    Classifica email usando Groq API (LLaMA 3.1)
    Agora recebe dados NLP para melhorar o prompt
    Retorna: (categoria, resposta_sugerida, confiança, motivo)
    """
    try:
        email_truncated = email_text[:2000] if len(email_text) > 2000 else email_text
        
        # Adiciona contexto NLP ao prompt se disponível
        nlp_context = ""
        if nlp_data and nlp_data.get('keywords'):
            keywords = ', '.join(nlp_data['keywords'][:5])
            nlp_context = f"\n\nPALAVRAS-CHAVE DETECTADAS: {keywords}"
        
        prompt = f"""Você é um assistente especializado em classificar emails corporativos do setor financeiro.

TAREFA 1 - CLASSIFICAÇÃO:
Classifique o email abaixo em uma das categorias:
- "Produtivo": Emails que requerem ação ou resposta específica (solicitações, dúvidas técnicas, problemas, atualizações de status, pedidos de suporte)
- "Improdutivo": Emails que não necessitam ação imediata (felicitações, agradecimentos genéricos, mensagens sociais)

TAREFA 2 - RESPOSTA:
Gere uma resposta automática profissional, cordial e objetiva em português brasileiro adequada à categoria.

Para emails PRODUTIVOS:
- Confirme o recebimento
- Indique que a solicitação será tratada
- Dê um prazo estimado (24-48h úteis)
- Seja específico se possível

Para emails IMPRODUTIVOS:
- Agradeça gentilmente
- Seja breve e cordial
- Indique que não é necessária ação adicional
{nlp_context}

EMAIL A ANALISAR:
{email_truncated}

FORMATO DA RESPOSTA (JSON):
{{
  "categoria": "Produtivo" ou "Improdutivo",
  "confianca": 0.0 a 1.0,
  "motivo": "breve justificativa",
  "resposta_sugerida": "texto da resposta"
}}"""

        chat_completion = groq_client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "Você é um assistente especializado em análise e classificação de emails corporativos. Responda sempre em formato JSON válido."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            model="llama-3.1-70b-versatile",
            temperature=0.3,
            max_tokens=500,
            response_format={"type": "json_object"},
            timeout=30
        )
        
        response_text = chat_completion.choices[0].message.content
        result = json.loads(response_text)
        
        categoria = result.get("categoria", "Produtivo")
        resposta = result.get("resposta_sugerida", "")
        confianca = float(result.get("confianca", 0.8))
        motivo = result.get("motivo", "")
        
        if not resposta:
            resposta = gerar_resposta_fallback(categoria)
        
        return categoria, resposta, confianca, motivo
        
    except Exception as e:
        logger.error(f"Erro na classificação com IA: {str(e)}")
        return classify_fallback(email_text)

def classify_fallback(text):
    """Classificação fallback caso a IA falhe - AGORA USA NLP"""
    text_lower = text.lower()
    
    # Tenta usar NLP para melhorar fallback
    try:
        nlp_result = nlp_processor.preprocess(text)
        keywords = set(nlp_result['keywords'])
        
        productive_keywords = {
            'status', 'solicit', 'pedid', 'requisic', 'atualiz',
            'problem', 'err', 'bug', 'funciona', 'defeito',
            'suport', 'ajud', 'assist', 'duvid', 'pergunt',
            'praz', 'urgent', 'important', 'priorid',
            'config', 'instal', 'implement'
        }
        
        unproductive_keywords = {
            'obrigad', 'agradec', 'paraben', 'feliz', 'natal', 'ano',
            'fest', 'cumpriment', 'saudac'
        }
        
        productive_count = len(keywords & productive_keywords)
        unproductive_count = len(keywords & unproductive_keywords)
        
    except:
        # Fallback do fallback
        productive_keywords = [
            "status", "solicitação", "pedido", "requisição", "atualização",
            "problema", "erro", "bug", "não funciona", "defeito",
            "suporte", "ajuda", "assistência", "dúvida", "pergunta",
            "prazo", "urgente", "importante", "prioridade"
        ]
        
        unproductive_keywords = [
            "obrigado", "agradeco", "parabéns", "feliz", "natal", "ano novo",
            "festas", "cumprimentos", "saudações"
        ]
        
        productive_count = sum(1 for kw in productive_keywords if kw in text_lower)
        unproductive_count = sum(1 for kw in unproductive_keywords if kw in text_lower)
    
    if productive_count > unproductive_count:
        categoria = "Produtivo"
    else:
        categoria = "Improdutivo"
    
    resposta = gerar_resposta_fallback(categoria)
    return categoria, resposta, 0.6, "Classificação baseada em análise NLP (fallback)"

def gerar_resposta_fallback(categoria):
    """Gera respostas genéricas como fallback"""
    if categoria == "Produtivo":
        return """Prezado(a),

Agradecemos seu contato. Sua solicitação foi recebida e registrada em nosso sistema.

Nossa equipe está analisando sua demanda e retornaremos com uma resposta em até 24-48 horas úteis.

Caso sua solicitação seja urgente, por favor nos informe através deste canal.

Atenciosamente,
Equipe de Suporte"""
    else:
        return """Prezado(a),

Agradecemos sua mensagem e suas gentis palavras.

Ficamos muito felizes com seu contato. Não é necessária nenhuma ação adicional de sua parte neste momento.

Estamos à disposição sempre que precisar.

Atenciosamente,
Equipe de Suporte"""

@app.route("/")
def home():
    """Serve a página HTML principal"""
    return render_template("index.html")

@app.route("/api")
def api_info():
    return jsonify({
        "status": "online",
        "app": "Classificador Inteligente de Emails - AutoU Case",
        "version": "2.1",
        "ai_provider": "Groq (LLaMA 3.1)",
        "nlp": "Enabled (Stop Words + Stemming + Keywords)",
        "endpoints": {
            "/process": "POST - Classifica email e sugere resposta",
            "/health": "GET - Status do serviço"
        }
    })

@app.route("/health")
def health():
    """Endpoint de saúde para monitoramento"""
    groq_status = "OK" if os.environ.get("GROQ_API_KEY") else "Missing API Key"
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "groq_api": groq_status,
        "nlp_processor": "Active"
    })

@app.route("/process", methods=["POST"])
def process_email():
    try:
        email_text = request.form.get("text", "").strip()
        uploaded_file = request.files.get("file")
        
        if uploaded_file and uploaded_file.filename:
            if not allowed_file(uploaded_file.filename):
                return jsonify({
                    "error": "Tipo de arquivo não permitido. Use apenas .txt ou .pdf"
                }), 400
            
            filename = secure_filename(uploaded_file.filename)
            
            if filename.endswith(".pdf"):
                email_text = extract_text_from_pdf(uploaded_file)
            elif filename.endswith(".txt"):
                email_text = extract_text_from_txt(uploaded_file)
        
        if not email_text or len(email_text.strip()) < 10:
            return jsonify({
                "error": "Texto do email muito curto ou vazio. Mínimo 10 caracteres."
            }), 400
        
        # Pré-processa com NLP
        processed_text, nlp_data = preprocess_text(email_text)
        
        # Classifica usando IA com contexto NLP
        category, suggested_response, confidence, reason = classify_with_ai(processed_text, nlp_data)
        
        # Inclui dados NLP na resposta
        response_data = {
            "category": category,
            "suggested_response": suggested_response,
            "confidence": confidence,
            "reason": reason,
            "text_length": len(email_text),
            "timestamp": datetime.now().isoformat(),
            "ai_model": "llama-3.1-70b-versatile"
        }
        
        # Adiciona keywords se NLP foi bem sucedido
        if nlp_data and nlp_data.get('keywords'):
            response_data['keywords'] = nlp_data['keywords'][:5]
            response_data['nlp_stats'] = nlp_data['statistics']
        
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Erro ao processar email: {str(e)}")
        return jsonify({
            "error": f"Erro ao processar email: {str(e)}"
        }), 500

if __name__ == "__main__":
    if not os.environ.get("GROQ_API_KEY"):
        logger.warning("GROQ_API_KEY não encontrada! Usando modo fallback.")
        print("⚠️  AVISO: GROQ_API_KEY não encontrada!")
        print("💡 Configure com: export GROQ_API_KEY='sua_chave_aqui'")
        print("🔧 Funcionando em modo fallback (NLP + palavras-chave)")
    
    os.makedirs("uploads", exist_ok=True)
    
    
    os.makedirs("services", exist_ok=True)

    port = int(os.environ.get("PORT", 8000))
    
    print("🚀 Servidor iniciando...")
    print("📡 API: http://localhost:8000")
    print("🤖 IA: Groq (LLaMA 3.1 70B)")
    print("🔬 NLP: Stop Words + Stemming + Keywords Extraction")
    
    app.run(debug=True, host="0.0.0.0", port=8000)