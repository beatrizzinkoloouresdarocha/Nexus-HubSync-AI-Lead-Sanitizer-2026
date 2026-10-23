from datetime import datetime
import logging
import os

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException
from google import genai
from pydantic import BaseModel, EmailStr
import requests
from sqlalchemy import Column, DateTime, Integer, String, Text, create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATABASE_URL = "sqlite:///./nexus_leads.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class AuditLogModel(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True, index=True)
    raw_payload = Column(Text, nullable=False)
    error_message = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


Base.metadata.create_all(bind=engine)

app = FastAPI(title="Nexus HubSync & AI Lead Sanitizer")


class LeadSchema(BaseModel):
    name: str
    email: EmailStr
    company: str


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/webhook/leads")
def receive_lead(payload: LeadSchema, db: Session = Depends(get_db)):  # noqa: B008
    try:
        # Sanitização e IA
        api_key = os.getenv("GEMINI_API_KEY")
        is_hot = True  # Padrão como quente para garantir o alerta

        if api_key:
            try:
                client = genai.Client(api_key=api_key)
                prompt = f"Analise se este lead B2B é qualificado. Responda apenas SIM ou NAO: {payload.name}, {payload.email}, {payload.company}"
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt,
                )
                if response and response.text and "NAO" in response.text.upper():
                    is_hot = False
            except Exception as ai_err:  # noqa: BLE001
                logger.warning("AI sanitization fallback triggered: %s", ai_err)

        # Envio para o Discord
        discord_url = os.getenv("DISCORD_WEBHOOK_URL")
        if discord_url:
            discord_payload = {
                "content": f"🚨 **Novo Lead Processado!**\n👤 **Nome:** {payload.name}\n📧 **E-mail:** {payload.email}\n🏢 **Empresa:** {payload.company}\n🔥 **Lead Quente:** {is_hot}"
            }
            requests.post(discord_url, json=discord_payload, timeout=10)

        return {
            "status": "success",
            "message": "Lead processado e alerta enviado com sucesso!",
            "is_hot": is_hot,
        }

    except Exception as exc:
        logger.exception("Error processing lead webhook")

        # Salva o erro na tabela de auditoria usando exceção específica do SQLAlchemy
        try:
            audit_entry = AuditLogModel(
                raw_payload=str(payload.model_dump()),
                error_message=str(exc),
            )
            db.add(audit_entry)
            db.commit()
        except SQLAlchemyError as db_err:
            logger.error("Failed to save audit log: %s", db_err)

        raise HTTPException(status_code=500, detail=str(exc))