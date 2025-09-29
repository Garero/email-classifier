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

# Inicializar processador NLP
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
        # Usa o processador NLP completo
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
        text = re.sub(r'[^\w\s\.,!?;:\-@áàâãéêíóôõúüçÁÀÂÃÉÊÍÓÔÕÚÜÇ]', '', text)
        return text.strip(), None

def classify_with_ai(email_text, nlp_data=None):
    """
    Classifica email usando Groq API (LLaMA 3.1)
    Agora com prompt melhorado para setor financeiro
    Retorna: (categoria, resposta_sugerida, confiança, motivo)
    """
    try:
        email_truncated = email_text[:2000] if len(email_text) > 2000 else email_text
        
        # Adiciona contexto NLP ao prompt se disponível
        nlp_context = ""
        if nlp_data and nlp_data.get('keywords'):
            keywords = ', '.join(nlp_data['keywords'][:5])
            nlp_context = f"\n\nPALAVRAS-CHAVE DETECTADAS: {keywords}"
        
        # PROMPT MELHORADO - Mais específico para setor financeiro
        prompt = f"""Você é um classificador especializado em emails CORPORATIVOS do SETOR FINANCEIRO.

CONTEXTO: Você trabalha para um banco/fintech e deve classificar emails baseado em URGÊNCIA e NECESSIDADE DE AÇÃO.

DIRETRIZES ESTRITAS DE CLASSIFICAÇÃO:

🔴 **CLASSIFICAR COMO "Produtivo" SE CONTIVER:**
- Problemas técnicos (sistema, app, login, transação)
- Solicitações de suporte/suporte técnico
- Dúvidas sobre produtos/serviços financeiros
- Problemas com pagamentos/transações/cobranças
- Solicitações de documentos/extratos/relatórios
- Prazos/urgências/datas limites
- Erros/falhas/bugs no sistema
- Solicitações de informações específicas
- Reclamações de clientes
- Mesmo que tenha "obrigado" ou "por favor", se tiver PROBLEMA = PRODUTIVO

🟢 **CLASSIFICAR COMO "Improdutivo" APENAS SE:**
- Apenas agradecimentos sem solicitação
- Apenas cumprimentos sociais
- Apenas parabéns genéricos
- Newsletters/marketing
- Mensagens automáticas
- Confirmações simples sem ação necessária

REGRA IMPORTANTE: Se o email mencionar QUALQUER problema, erro, solicitação ou dúvida → SEMPRE "Produtivo"

EXEMPLOS:
- "Problema no login" → Produtivo
- "Erro na transação" → Produtivo  
- "Solicito extrato" → Produtivo
- "Obrigado pelo atendimento" → Improdutivo
- "Parabéns pela equipe" → Improdutivo
{nlp_context}

EMAIL PARA CLASSIFICAR:
\"\"\"{email_truncated}\"\"\"

RESPONDA APENAS EM JSON (sem markdown, sem texto adicional):
{{
  "categoria": "Produtivo" ou "Improdutivo",
  "confianca": 0.0 a 1.0,
  "motivo": "explicação detalhada baseada nas diretrizes",
  "resposta_sugerida": "resposta profissional em português"
}}"""

        chat_completion = groq_client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "Você é um classificador especializado em emails corporativos do setor financeiro. Responda APENAS em formato JSON válido, sem texto adicional."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            model="llama-3.1-70b-versatile",
            temperature=0.1,  # Reduzido para menos criatividade, mais precisão
            max_tokens=800,
            response_format={"type": "json_object"},
            timeout=30
        )
        
        response_text = chat_completion.choices[0].message.content
        logger.info(f"Resposta bruta da IA: {response_text}")
        
        result = json.loads(response_text)
        
        categoria = result.get("categoria", "Produtivo")
        resposta = result.get("resposta_sugerida", "")
        confianca = float(result.get("confianca", 0.8))
        motivo = result.get("motivo", "")
        
        if not resposta:
            resposta = gerar_resposta_fallback(categoria)
        
        logger.info(f"Classificação IA: {categoria} (confiança: {confianca}) - {motivo}")
        return categoria, resposta, confianca, motivo
        
    except Exception as e:
        logger.error(f"Erro na classificação com IA: {str(e)}")
        # Fallback para classificação NLP
        return classify_fallback(email_text)

def classify_fallback(text):
    """Classificação fallback MELHORADA - Mais agressiva para produtivo"""
    text_lower = text.lower()
    
    # PALAVRAS-CHAVE FORTES para PRODUTIVO (setor financeiro)
    strong_productive_indicators = [
        # Problemas técnicos
        'problema', 'erro', 'bug', 'falha', 'defeito', 'não funciona', 'parou', 'travou', 
        'lentidão', 'queda', 'fora do ar', 'inoperante', 'quebrado',
        
        # Urgência
        'urgente', 'urgência', 'imediat', 'asap', 'hoje', 'amanhã', 'prazo', 'prioridade',
        
        # Suporte técnico
        'suporte', 'ajuda', 'assistência', 'suport', 'resolver', 'corrigir', 'conserto',
        
        # Transações financeiras
        'transação', 'pagamento', 'transferência', 'ted', 'doc', 'pix', 'cobrança', 'fatura',
        'boleto', 'débito', 'crédito', 'estorno', 'chargeback',
        
        # Acesso e segurança
        'login', 'senha', 'acesso', 'bloqueado', 'bloqueio', 'conta', 'cartão',
        
        # Documentos
        'extrato', 'relatório', 'comprovante', 'documento', 'certificado', 'declaração',
        
        # Dúvidas específicas
        'como fazer', 'como usar', 'como configurar', 'dúvida', 'pergunta', 'esclarecimento'
    ]
    
    # PALAVRAS-CHAVE para IMPRODUTIVO
    unproductive_indicators = [
        'obrigado', 'obrigada', 'agradeço', 'parabéns', 'feliz', 'natal', 'ano novo',
        'bom dia', 'boa tarde', 'boa noite', 'abraço', 'abraços', 'sucesso', 'comemoração'
    ]
    
    # Contagem MELHORADA - Produtivo tem prioridade
    productive_count = 0
    unproductive_count = 0
    
    for indicator in strong_productive_indicators:
        if indicator in text_lower:
            productive_count += 2  # Peso maior para indicadores produtivos
    
    for indicator in unproductive_indicators:
        if indicator in text_lower:
            unproductive_count += 1
    
    # LÓGICA DECISÓRIA MELHORADA
    if productive_count > 0:
        categoria = "Produtivo"
        confianca = min(0.9, 0.6 + (productive_count * 0.1))
        motivo = f"Detectados {productive_count} indicadores fortes de produtividade"
    else:
        categoria = "Improdutivo" 
        confianca = min(0.8, 0.5 + (unproductive_count * 0.1))
        motivo = f"Detectados {unproductive_count} indicadores sociais/cortesia"
    
    resposta = gerar_resposta_fallback(categoria)
    
    logger.info(f"Classificação Fallback: {categoria} (prod: {productive_count}, impr: {unproductive_count})")
    return categoria, resposta, confianca, motivo

def gerar_resposta_fallback(categoria):
    """Gera respostas genéricas como fallback"""
    if categoria == "Produtivo":
        return """Prezado(a),

Agradecemos seu contato. Identificamos que sua mensagem requer atenção imediata.

Sua solicitação foi registrada em nosso sistema com prioridade e nossa equipe especializada está trabalhando para resolvê-la.

Retornaremos com uma solução ou atualização em até 24 horas úteis.

Caso seja uma emergência crítica, por favor responda este email marcando como URGENTE.

Atenciosamente,
Equipe de Suporte Técnico"""
    else:
        return """Prezado(a),

Agradecemos suas gentis palavras e o contato.

Ficamos muito felizes com seu feedback positivo. Não é necessária nenhuma ação adicional de sua parte.

Estamos sempre à disposição para ajudá-lo quando precisar.

Atenciosamente,
Equipe de Relacionamento"""

@app.route("/")
def home():
    """Serve a página HTML principal"""
    return render_template("index.html")

@app.route("/api")
def api_info():
    return jsonify({
        "status": "online",
        "app": "Classificador Inteligente de Emails - AutoU Case",
        "version": "2.2",
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
        
        # Log do texto recebido para debug
        logger.info(f"Texto recebido para análise ({len(email_text)} chars): {email_text[:200]}...")
        
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
        
        logger.info(f"Resposta final: {category} (confiança: {confidence})")
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
        print("🔑 Configure com: export GROQ_API_KEY='sua_chave_aqui'")
        print("🔄 Funcionando em modo fallback (NLP + palavras-chave)")
    
    os.makedirs("uploads", exist_ok=True)
    
    port = int(os.environ.get("PORT", 8000))
    
    print("🚀 Servidor iniciando...")
    print("🔗 API: http://localhost:8000")
    print("🤖 IA: Groq (LLaMA 3.1 70B)")
    print("📊 NLP: Stop Words + Stemming + Keywords Extraction")
    print("🎯 Classificador: Modo AGGRESSIVO-PRODUTIVO ativado")
    
    app.run(debug=True, host="0.0.0.0", port=port)