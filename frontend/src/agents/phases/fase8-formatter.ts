// src/agents/phases/fase8-formatter.ts
import { PatternItem } from '../../patterns/index';

export function generateFase8Response(acceptedItems: PatternItem[]): string {
  // FASE_8: Inferencia - decisiones sobre módulos
  // Usar categoría 'modulo' según la biblioteca de patrones
  const acceptedInferences = acceptedItems
    .filter(item => item.category === 'modulo')
    .map(item => {
      return {
        modulo: item.name,
        decision: 'ACEPTADO_V1'
      };
    });

  // Si no hay módulos aceptados, retornar vacío
  if (acceptedInferences.length === 0) {
    return '';
  }

  return acceptedInferences.map(inf => 
    `${inf.modulo} | ${inf.decision}`
  ).join('\n');
}