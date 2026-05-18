# app/api/routes/help.py
# Proxy del LLM para ayuda contextual.
# El LLM solo explica y ejemplifica — nunca escribe al SEC ni a las fases.
# Aislado completamente del orchestrator y session_store.

from __future__ import annotations

import json
import os
from typing import Any

import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/api/help", tags=["help"])

# --------------------------------------------------------------------------- #
# Contratos de entrada / salida                                                #
# --------------------------------------------------------------------------- #

class HelpRequest(BaseModel):
    sistema: str
    fase: str
    pregunta: str
    dimension: str


class HelpResponse(BaseModel):
    explicacion: str
    ejemplos_alta: list[str]
    ejemplos_media: list[str]
    recomendacion: str
    preguntas_seguimiento: list[str] = []


# --------------------------------------------------------------------------- #
# Configuración del proveedor LLM                                              #
# --------------------------------------------------------------------------- #

def _llm_config() -> dict[str, Any]:
    """
    Lee las variables de entorno para seleccionar el proveedor.
    Soporta Anthropic (Claude), OpenAI y DeepSeek.
    Agrega más bloques if/elif para otros proveedores.
    """
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    openai_key    = os.getenv("OPENAI_API_KEY")
    deepseek_key  = os.getenv("DEEPSEEK_API_KEY")

    if anthropic_key:
        return {
            "provider": "anthropic",
            "url": "https://api.anthropic.com/v1/messages",
            "headers": {
                "x-api-key": anthropic_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            "model": os.getenv("HELP_LLM_MODEL", "claude-haiku-4-5-20251001"),
        }

    if openai_key:
        return {
            "provider": "openai",
            "url": "https://api.openai.com/v1/chat/completions",
            "headers": {
                "Authorization": f"Bearer {openai_key}",
                "Content-Type": "application/json",
            },
            "model": os.getenv("HELP_LLM_MODEL", "gpt-4o-mini"),
        }

    if deepseek_key:
        return {
            "provider": "deepseek",
            "url": "https://api.deepseek.com/v1/chat/completions",
            "headers": {
                "Authorization": f"Bearer {deepseek_key}",
                "Content-Type": "application/json",
            },
            "model": os.getenv("HELP_LLM_MODEL", "deepseek-chat"),
        }

    raise HTTPException(status_code=503, detail="No LLM provider configured. Set ANTHROPIC_API_KEY, OPENAI_API_KEY or DEEPSEEK_API_KEY.")


# --------------------------------------------------------------------------- #
# Constructor del prompt                                                        #
# --------------------------------------------------------------------------- #

def _build_prompt(req: HelpRequest) -> str:
    return (
        f"Eres un consultor senior de sistemas experto en {req.sistema}.\n\n"
        f"El humano está respondiendo la dimensión {req.dimension} ({req.fase}) y tiene dudas sobre:\n"
        f'"{req.pregunta}"\n\n'
        f"Responde ÚNICAMENTE con un objeto JSON válido, sin markdown, sin texto adicional:\n\n"
        "{\n"
        f'  "explicacion": "Qué significa esta pregunta en el contexto de {req.sistema} y por qué es importante. Máx 3 oraciones.",\n'
        f'  "ejemplos_alta": ["ejemplo concreto 1 para {req.sistema}", "ejemplo 2", "ejemplo 3"],\n'
        f'  "ejemplos_media": ["ejemplo secundario 1 para {req.sistema}", "ejemplo 2"],\n'
        f'  "recomendacion": "Recomendación final concreta para {req.sistema}. Máx 2 oraciones.",\n'
        '  "preguntas_seguimiento": []\n'
        "}\n\n"
        "REGLAS:\n"
        f"- ejemplos_alta: 3-5 ejemplos específicos para {req.sistema} de importancia crítica\n"
        f"- ejemplos_media: 2-3 ejemplos de importancia secundaria\n"
        "- preguntas_seguimiento: solo incluir si sin ellas no puedes dar recomendación. Máx 2 preguntas.\n"
        "- Sin saludos ni despedidas\n"
        "- Solo JSON puro y válido"
    )


# --------------------------------------------------------------------------- #
# Llamada al LLM según proveedor                                               #
# --------------------------------------------------------------------------- #

async def _call_llm(prompt: str, config: dict[str, Any]) -> str:
    """Devuelve el texto de respuesta del LLM."""
    timeout = httpx.Timeout(30.0)

    if config["provider"] == "anthropic":
        payload = {
            "model": config["model"],
            "max_tokens": 800,
            "messages": [{"role": "user", "content": prompt}],
        }
    else:
        # OpenAI-compatible (OpenAI, DeepSeek, etc.)
        payload = {
            "model": config["model"],
            "max_tokens": 800,
            "temperature": 0.2,
            "messages": [{"role": "user", "content": prompt}],
        }

    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.post(
            config["url"],
            headers=config["headers"],
            json=payload,
        )

    if response.status_code != 200:
        raise HTTPException(
            status_code=502,
            detail=f"LLM provider error {response.status_code}: {response.text[:200]}",
        )

    data = response.json()

    # Extraer texto según formato del proveedor
    if config["provider"] == "anthropic":
        return data["content"][0]["text"]
    else:
        return data["choices"][0]["message"]["content"]


# --------------------------------------------------------------------------- #
# Parseo de la respuesta JSON del LLM                                          #
# --------------------------------------------------------------------------- #

def _parse_llm_response(raw: str) -> HelpResponse:
    """
    Parsea la respuesta JSON del LLM con fallback robusto.
    Si el LLM alucinó formato, devuelve una respuesta degradada en lugar de 500.
    """
    text = raw.strip()

    # Limpiar posibles bloques markdown que el LLM incluya aunque se lo prohibamos
    if text.startswith("```"):
        lines = text.splitlines()
        text = "\n".join(
            line for line in lines
            if not line.strip().startswith("```")
        ).strip()

    try:
        data = json.loads(text)
        return HelpResponse(
            explicacion=str(data.get("explicacion", "Sin explicación disponible.")),
            ejemplos_alta=[str(e) for e in data.get("ejemplos_alta", [])],
            ejemplos_media=[str(e) for e in data.get("ejemplos_media", [])],
            recomendacion=str(data.get("recomendacion", "Consulta con tu equipo técnico.")),
            preguntas_seguimiento=[str(p) for p in data.get("preguntas_seguimiento", [])],
        )
    except (json.JSONDecodeError, KeyError, TypeError):
        # Fallback: devolver el texto crudo como explicación
        return HelpResponse(
            explicacion=text[:400] if text else "No se pudo obtener ayuda en este momento.",
            ejemplos_alta=[],
            ejemplos_media=[],
            recomendacion="Intenta reformular la pregunta o consulta la documentación.",
        )


# --------------------------------------------------------------------------- #
# Endpoint                                                                      #
# --------------------------------------------------------------------------- #

@router.post("", response_model=HelpResponse)
async def get_help(req: HelpRequest) -> HelpResponse:
    """
    Proxy de ayuda contextual. Solo explica y ejemplifica.
    No modifica sesiones ni artefactos del SEC.
    """
    config = _llm_config()
    prompt = _build_prompt(req)
    raw = await _call_llm(prompt, config)
    return _parse_llm_response(raw)