📧 Classificador Inteligente de Emails - AutoU Case

Solução inteligente para classificação automática de emails usando IA. Classifica emails como Produtivos ou Improdutivos e gera respostas automáticas contextualizadas em tempo real.

🎥 Demonstração
🔗 Aplicação Online: https://email-classifier-kd4a.onrender.com

Interface moderna com classificação em tempo real usando Groq AI

Dica: A aplicação está hospedada no Render.com - pode levar alguns segundos para "acordar" na primeira vez.

✨ Funcionalidades
🤖 Inteligência Artificial
Classificação Contextual com Groq + LLaMA 3.1 70B

Respostas Personalizadas baseadas no conteúdo do email

Sistema de Fallback inteligente caso a API falhe

Confiança da Classificação com score de 0-1

📁 Processamento de Arquivos
Suporte Multi-Formato: PDF e TXT

Drag & Drop intuitivo

Validação de Tamanho (até 10MB)

Extração Automática de texto

🎨 Experiência do Usuário
Interface Moderna com Tailwind CSS

Design 100% Responsivo (mobile-first)

Loading States animados

Feedback Visual imediato

Acessibilidade completa (ARIA labels)

🔒 Confiabilidade & Segurança
Tratamento Robusto de erros

Logging Profissional

Health Checks automáticos

Validações client-side e server-side

🗂️ Estrutura do Projeto
text
email-classifier/
├── app.py                 # 🚀 Aplicação Flask principal
├── requirements.txt       # 📦 Dependências do projeto
├── .env.example          # ⚙️ Exemplo de variáveis de ambiente
├── README.md             # 📖 Documentação
├── templates/
│   └── index.html        # 🎨 Interface web (Frontend)
├── routes/               # 🛣️ Sistema de rotas
│   ├── __init__.py
│   ├── main.py          # Rotas principais (/ e /health)
│   └── process.py       # Processamento de emails (/process)
├── services/             # 🔧 Lógica de negócio
│   ├── __init__.py
│   ├── classifier.py    # 🤖 IA - Classificação com Groq
│   └── pdf_reader.py    # 📄 Processamento de PDF
├── tests/               # 🧪 Testes unitários
└── uploads/             # 💾 Arquivos temporários (gitignored)
🛠️ Stack Tecnológica
Backend
Python 3.8+ - Linguagem principal

Flask 3.0 - Framework web leve e poderoso

Groq API - IA de alta performance com LLaMA 3.1 70B

PyMuPDF - Processamento eficiente de PDF

Werkzeug - Utilitários WSGI

Frontend
HTML5 - Estrutura semântica

Tailwind CSS - Framework CSS utility-first

JavaScript Vanilla - Interatividade sem dependências

Design System - Componentes consistentes

DevOps & Ferramentas
Render.com - Plataforma de deploy e hospedagem

Git & GitHub - Controle de versão

Python-dotenv - Gerenciamento de variáveis de ambiente

⚡ Instalação Rápida
Pré-requisitos
Python 3.8 ou superior

Conta no Groq para API key gratuita

Git instalado

🚀 Deploy em 5 Minutos
1. Clone o repositório
bash
git clone https://github.com/Garero/email-classifier.git
cd email-classifier
2. Ambiente Virtual (Recomendado)
bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows
3. Instale as dependências
bash
pip install -r requirements.txt
4. Configure a API Key
bash
cp .env.example .env
Edite o arquivo .env:

env
GROQ_API_KEY=sua_chave_groq_aqui
FLASK_ENV=development
PORT=8000
5. Execute a aplicação
bash
python app.py
6. Acesse
Abra seu navegador em: http://localhost:8000

🔌 API Reference
Processar Email
http
POST /process
Content-Type: multipart/form-data

Parâmetros:

text (string, opcional): Conteúdo textual do email

file (file, opcional): Arquivo .txt ou .pdf (máx 10MB)

Response (200):

json
{
  "category": "Produtivo",
  "suggested_response": "Agradecemos seu contato. Sua solicitação foi recebida...",
  "confidence": 0.92,
  "reason": "Email contém solicitação de suporte técnico",
  "text_length": 156,
  "timestamp": "2024-01-15T10:30:00Z",
  "ai_model": "llama-3.1-70b-versatile"
}
Response (400):

json
{
  "error": "Texto do email muito curto ou vazio. Mínimo 10 caracteres."
}
Health Check
http
GET /health
Response:

json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "groq_api": "OK"
}
Informações da API
http
GET /api
Response:

json
{
  "status": "online",
  "app": "Classificador Inteligente de Emails - AutoU Case",
  "version": "2.0",
  "ai_provider": "Groq (LLaMA 3.1)",
  "endpoints": {
    "/process": "POST - Classifica email e sugere resposta",
    "/health": "GET - Status do serviço"
  }
}
💡 Exemplos de Uso
Email Produtivo
text
"Preciso de ajuda urgente! Meu login não está funcionando desde ontem e preciso acessar o sistema para enviar um relatório importante para o cliente."
Resposta da IA:

json
{
  "category": "Produtivo",
  "suggested_response": "Prezado(a), Agradecemos seu contato sobre o problema de login. Nossa equipe técnica já foi notificada e está trabalhando na solução. Iremos atualizá-lo em até 2 horas úteis. Atenciosamente, Equipe de Suporte",
  "confidence": 0.95,
  "reason": "Email contém solicitação urgente de suporte técnico"
}
Email Improdutivo
text
"Olá equipe! Gostaria de parabenizar todos pelo excelente trabalho no último projeto. Ficou fantástico e o cliente está muito satisfeito! Abraços."
Resposta da IA:

json
{
  "category": "Improdutivo",
  "suggested_response": "Prezado(a), Agradecemos suas gentis palavras e o feedback positivo! Ficamos muito felizes em saber que o projeto atendeu às expectativas. Continuamos à disposição. Atenciosamente, Equipe",
  "confidence": 0.88,
  "reason": "Email é um agradecimento/parabenização sem necessidade de ação"
}
Uso via cURL
bash
curl -X POST http://localhost:8000/process \
  -F "text=Preciso de ajuda com reset de senha" \
  -F "file=@email.pdf"
🌐 Deploy em Produção
Render.com (Recomendado - Grátis)
Fork este repositório no GitHub

Acesse Render.com

Conecte sua conta GitHub

Crie novo Web Service

Configure:

Build Command: pip install -r requirements.txt

Start Command: python app.py

Environment Variables: GROQ_API_KEY=sua_chave_groq

Variáveis de Ambiente (Produção)
env
GROQ_API_KEY=sua_chave_groq_aqui
FLASK_ENV=production
PORT=10000
Outras Plataformas
Heroku: Procfile incluído automaticamente

Railway: Compatível com requirements.txt

PythonAnywhere: Upload manual do repositório

🧪 Testes
Testes Unitários
bash
python -m pytest tests/ -v
Testes Manuais
Teste de Saúde:

bash
curl https://seu-app.onrender.com/health
Teste de Classificação:

bash
curl -X POST https://seu-app.onrender.com/process \
  -F "text=Preciso de suporte técnico urgente"
🗺️ Roadmap Futuro
Histórico de Classificações com localStorage

Múltiplos Templates de resposta por categoria

Análise de Sentimentos avançada

Suporte a Mais Formatos (DOCX, imagens com OCR)

Dashboard Administrativo com métricas

API Rate Limiting e autenticação

Exportação de Resultados (PDF/CSV)

Integração com APIs de Email (Gmail, Outlook)

🤝 Contribuindo
Contribuições são bem-vindas! Siga estos passos:

Fork o projeto

Crie uma branch: git checkout -b feature/nova-feature

Commit suas mudanças: git commit -m 'Add nova feature'

Push: git push origin feature/nova-feature

Abra um Pull Request

Padrões de Código
Siga PEP 8 para Python

Use commits semânticos

Mantenha testes atualizados

Documente novas funcionalidades

🐛 Solução de Problemas
Problemas Comuns
❌ "GROQ_API_KEY não encontrada"

bash
# Solução: Configure a variável de ambiente
export GROQ_API_KEY=sua_chave_groq
# ou edite o arquivo .env
❌ Erro ao processar PDF

bash
# Solução: Verifique se o PyMuPDF está instalado
pip install PyMuPDF==1.23.8
❌ Aplicação lenta no primeiro acesso

bash
# Isso é normal no plano gratuito do Render
# O servidor "acorda" após alguns segundos de inatividade
❌ Timeout na API Groq

bash
# Solução: A IA pode estar sob carga pesada
# O sistema automaticamente usa fallback após 30 segundos
📞 Contato & Suporte
👨💻 Desenvolvedor: Gabriel Reis
🐙 GitHub: @Garero
📧 Email: [Seu email]
💼 LinkedIn: [Seu LinkedIn]

Projeto desenvolvido para o processo seletivo da AutoU

📄 Licença
Este projeto está sob a licença MIT. Veja o arquivo LICENSE para detalhes.

🙏 Agradecimentos
AutoU pela oportunidade e desafio inspirador

Groq pela incrível API de IA gratuita

Render.com pela hospedagem gratuita

Comunidade Open Source pelas ferramentas incríveis

<div align="center">
⭐ Se este projeto te ajudou, deixe uma estrela no repositório!

"Do. Or do not. There is no try." - Mestre Yoda

</div>
🔗 Links Úteis:

Aplicação Online

Repositório GitHub

Groq Console

Documentação Render