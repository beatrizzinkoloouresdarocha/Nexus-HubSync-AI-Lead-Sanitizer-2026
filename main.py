import os

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel
import requests
from sqlalchemy.orm import Session

from ai_service import sanitize_and_classify_lead
from database import AuditLogModel, LeadModel, SessionLocal, init_db

load_dotenv()
init_db()

app = FastAPI(title="Nexus HubSync & Lead Sanitizer")


class LeadWebhookPayload(BaseModel):
    name: str
    email: str
    company: str | None = "Desconhecida"


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def send_discord_alert(message: str):
    webhook_url = os.environ.get("DISCORD_WEBHOOK_URL")
    if webhook_url:
        requests.post(webhook_url, json={"content": message})


@app.post("/webhook/leads")
def receive_lead(payload: LeadWebhookPayload, db: Session = Depends(get_db)):  # noqa: B008
    try:
        sanitized = sanitize_and_classify_lead(
            name=payload.name,
            email=payload.email,
            company=payload.company or "Desconhecida"
        )

        if not sanitized.valid_corporate_email:
            audit = AuditLogModel(
                raw_payload=payload.model_dump_json(),
                error_message="E-mail inválido ou não corporativo detectado pela IA."
            )
            db.add(audit)
            db.commit()
            raise HTTPException(status_code=400, detail="Lead rejeitado: E-mail inválido ou pessoal.")

        db_lead = LeadModel(
            name=sanitized.corrected_name,
            email=payload.email,
            company=payload.company,
            profile_category=sanitized.profile_category,
            status="hot" if sanitized.is_hot_lead else "standard"
        )
        db.add(db_lead)
        db.commit()
        db.refresh(db_lead)

        if sanitized.is_hot_lead:
            send_discord_alert(
                f"🚨 **Lead Quente Detectado!**\n"
                f"👤 Nome: {db_lead.name}\n"
                f"📧 E-mail: {db_lead.email}\n"
                f"🏢 Empresa: {db_lead.company}\n"
                f"📊 Categoria: {db_lead.profile_category}"
            )

        return {"status": "success", "lead_id": db_lead.id, "category": sanitized.profile_category}

    except Exception as e:
        if not isinstance(e, HTTPException):
            audit = AuditLogModel(
                raw_payload=payload.model_dump_json(),
                error_message=str(e)
            )
            db.add(audit)
            db.commit()
        raise