import json
import os

from google import genai
from google.genai import types
from pydantic import BaseModel, Field


class SanitizedLead(BaseModel):
    corrected_name: str = Field(description="Nome do lead corrigido e capitalizado corretamente")
    valid_corporate_email: bool = Field(description="True se o e-mail parece corporativo e válido, False para e-mails descartáveis/inválidos")
    profile_category: str = Field(description="Categoria do perfil: 'Enterprise', 'SMB' ou 'Desconhecido'")
    is_hot_lead: bool = Field(description="True se for lead altamente qualificado")


def sanitize_and_classify_lead(name: str, email: str, company: str) -> SanitizedLead:
    client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
    
    prompt = f"""
    Analise e higienize os seguintes dados de lead recebidos do CRM:
    Nome: {name}
    E-mail: {email}
    Empresa: {company}

    Corrija formatações de nomes, avalie se o e-mail é corporativo legítimo e classifique o lead.
    """

    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=SanitizedLead,
            temperature=0.1
        ),
    )
    
    data = json.loads(response.text)
    return SanitizedLead(**data)