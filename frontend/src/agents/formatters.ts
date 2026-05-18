// Tipos de datos para respuestas estructuradas por fase
export interface Fase1Object {
  nombre: string;
  volumenDia: string; // numero con unidad o rango o DESCONOCIDO
  retencion: string; // numero + unidad o rango o DESCONOCIDO
  atributos: string; // 3-5 atributos separados por comas
  owner: string;
  criticidad: string;
}

export interface Fase2Operation {
  nombre: string;
  actor: string;
  objetos: string; // puede ser múltiples objetos separados por coma
  trigger: string;
  resultado: string;
  criticidad: string;
}

// Interfaz genérica para respuesta estructurada
export interface StructuredResponse {
  fase: string;
  contenido: string;
}