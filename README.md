# 📧 Classificador de Emails - AutoU

Este projeto é uma interface web simples para **classificação de emails**.  
O usuário pode **fazer upload** de arquivos `.txt` ou `.pdf` contendo emails, ou então **colar o texto diretamente** em uma caixa de texto.  

Após o envio, o sistema processa o conteúdo e retorna:
- A **categoria atribuída** ao email (Produtivo ou Improdutivo).
- Uma **resposta automática sugerida**.

---

## 🚀 Funcionalidades

- Upload de arquivos `.txt` ou `.pdf`.
- Inserção manual de texto de emails.
- Botão para processar o conteúdo.
- Exibição da categoria (Produtivo/Improdutivo).
- Exibição da resposta automática sugerida.
- Validação para garantir que apenas **um método de entrada** seja usado (arquivo ou texto).
- Feedback visual de **carregamento** e **mensagens de erro**.
- Layout simples, responsivo e acessível.

---

## 🛠️ Estrutura do Projeto
Desafio/
├── app.py # Aplicação Flask
├── requirements.txt # Dependências do Python
├── .env.example # Exemplo de variáveis de ambiente
├── .gitignore # Arquivos ignorados pelo Git
├── README.md # Este arquivo
├── templates/
│ └── index.html # Página web
└── uploads/ # Pasta para uploads (não versionada)


---

## 📦 Instalação e Uso

### Pré-requisitos

- Python 3.8 ou superior
- Conta no [Groq](https://console.groq.com) para obter a API key

### Passos

1. **Clone o repositório**
   ```bash
   git clone https://github.com/seu-usuario/email-classifier.git
   cd email-classifier

2.  **Crie um ambiente virtual (opcional, mas recomendado)**
   python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows

3.  **Instale as dependências**
pip install -r requirements.txt

4.  **Configure as variáveis de ambiente**
Copie o arquivo .env.example para .env

Edite o arquivo .env e adicione sua chave da Groq:
GROQ_API_KEY=sua_chave_groq_aqui

5.  **Execute a aplicação**
python app.py

6. **Acesse a aplicação**
Abra o navegador e vá para http://localhost:8000

🔌 API
Endpoints
GET / - Interface web

GET /api - Informações da API

GET /health - Status do serviço

POST /process - Processa um email (envie text ou file)

Exemplo de uso da API

curl -X POST http://localhost:8000/process \
  -F "text=Preciso de ajuda com meu login" \
  -F "file=@email.pdf"

  🚀 Deploy
Render.com (Recomendado)
Conecte seu repositório no Render.

Crie um novo Web Service.

Configure:

Build Command: pip install -r requirements.txt

Start Command: python app.py

Environment Variables: Adicione GROQ_API_KEY com sua chave.

Outras plataformas
O projeto pode ser deployado em qualquer plataforma que suporte Python, como Heroku, Railway, etc.

📝 Licença
Este projeto foi desenvolvido para o processo seletivo da AutoU.

