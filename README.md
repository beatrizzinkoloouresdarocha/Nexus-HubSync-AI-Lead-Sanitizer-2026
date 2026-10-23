# 🚀 Nexus HubSync & AI Lead Sanitizer (2026)

Microserviço e pipeline de automação backend desenvolvido em Python para sanitização de leads com Inteligência Artificial (Google Gemini API), armazenamento persistente em SQLite via SQLAlchemy e notificações em tempo real através de Webhooks do Discord.

---

## 🛠️ Tecnologias Utilizadas

- **Linguagem:** Python 3.10+
- **Framework Web:** FastAPI
- **Servidor ASGI:** Uvicorn
- **ORM & Banco de Dados:** SQLAlchemy & SQLite
- **Validação de Dados:** Pydantic
- **Inteligência Artificial:** Google GenAI SDK (`google-genai` / Gemini API)
- **Notificações:** Discord Webhooks (`requests`)
- **Gestão de Ambiente:** `python-dotenv`

---

## 📌 Funcionalidades Principais

1. **Higienização de Leads com IA (Google Gemini):**
   - Correção automática de formatação de nomes e padronização.
   - Categorização inteligente com base no e-mail e empresa informada (ex: *Enterprise / B2B*).

2. **Persistência de Dados (SQLite & SQLAlchemy):**
   - Armazenamento seguro de registros limpos em banco de dados relacional local.

3. **Notificações em Tempo Real:**
   - Disparo automático de alertas via Webhook do Discord para sinalização de novos leads qualificados.

4. **Documentação Automática:**
   - Swagger UI interativo integrado para teste das rotas HTTP.

---

## 📂 Estrutura do Projeto

```text
.
├── main.py              # Ponto de entrada da aplicação FastAPI
├── ai_service.py        # Integração e lógica da API do Google Gemini
├── database.py          # Configuração de modelos e sessão do SQLAlchemy
├── iniciar.bat          # Script de automação para execução e abertura do Swagger
├── requirements.txt     # Lista de dependências do projeto
├── .env.example         # Modelo de variáveis de ambiente
└── .gitignore           # Exclusão de credenciais, ambiente virtual e banco