// FRONTEND/src/services/helpService.ts
// Llama al backend proxy para obtener ayuda contextual sobre una pregunta de fase.
// El LLM nunca toca datos del SEC ni decisiones — solo explica y ejemplifica.

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000';

export interface HelpRequest {
  sistema: string;       // Ej: "punto de venta", "clínica", "e-commerce"
  fase: string;          // Ej: "FASE_3B", "FASE_7B"
  pregunta: string;      // La pregunta técnica que el usuario no entiende
  dimension: string;     // Ej: "RELACIONES", "ESPACIO", "COMUNICACION"
}

export interface HelpResponse {
  explicacion: string;   // Por qué es importante esta pregunta
  ejemplos_alta: string[];
  ejemplos_media: string[];
  recomendacion: string;
  preguntas_seguimiento?: string[];  // máx 2, solo si son necesarias
}

export async function getContextualHelp(req: HelpRequest): Promise<HelpResponse> {
  const res = await fetch(`${API_BASE}/api/help`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(req),
  });

  if (!res.ok) {
    throw new Error(`Help API error: ${res.status}`);
  }

  return res.json();
}

// Construye el prompt estructurado que va al backend
export function buildHelpPrompt(req: HelpRequest): string {
  return `Eres un consultor senior de sistemas experto en ${req.sistema}.

El humano está respondiendo la dimensión ${req.dimension} del sistema y pregunta:
"${req.pregunta}"

Responde en exactamente 3 partes con este formato JSON:

{
  "explicacion": "Qué significa esta pregunta en el contexto de ${req.sistema} y por qué es importante responderla bien. Máx 3 oraciones.",
  "ejemplos_alta": ["ejemplo 1", "ejemplo 2", "ejemplo 3"],
  "ejemplos_media": ["ejemplo 1", "ejemplo 2"],
  "recomendacion": "Recomendación final concreta para ${req.sistema}. Máx 2 oraciones.",
  "preguntas_seguimiento": []
}

REGLAS:
- ejemplos_alta: 3-5 ejemplos concretos específicos para ${req.sistema}
- ejemplos_media: 2-3 ejemplos de importancia secundaria
- preguntas_seguimiento: solo incluir si sin ellas no puedes dar recomendación. Máx 2.
- Sin saludos ni despedidas
- Solo JSON válido, sin markdown

Sistema: ${req.sistema}
Fase actual: ${req.fase}`;
}