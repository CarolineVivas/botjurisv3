Chatbot jurídico via WhatsApp, desenvolvido com FastAPI, LangChain e Evolution API.

🚀 Tecnologias

FastAPI, SQLAlchemy, PostgreSQL

LangChain + OpenAI

Evolution API (WhatsApp)

Redis + RQ

Docker

📦 Instalação
git clone https://github.com/CarolineVivas/botjurisv3
cd botjurisv3
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

⚙️ Configuração
cp .env.example .env

Preencha DATABASE_URL, REDIS_URL, EVOLUTION_API_KEY, OPENAI_API_KEY.

▶️ Executar
uvicorn app.main:app --reload
python -m app.workers.worker

Docs: http://localhost:8000/docs

🧪 Testes
pytest

👩‍💻 Autoria

Caroline Gonçalves — @CarolineVivas
