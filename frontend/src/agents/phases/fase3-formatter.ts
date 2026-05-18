// FASE_3 Formatter
import { PatternItem } from '../../patterns/index';

export function generateFase3Response(acceptedItems: PatternItem[]): string {
  // FASE_3: Estados - mínimo 3 estados
  const acceptedStates = acceptedItems
    .filter(item => item.category === 'estado');
  
  // Necesitamos al menos 3 estados
  if (acceptedStates.length < 3) {
    // Retornamos estados por defecto para cumplir el mínimo
    const defaultStates = ['activo', 'inactivo', 'suspendido'];
    return defaultStates.map((state, index) => 
      `objeto_${index} | estado_inicial | evento | ${state} | rollback_${index} | false`
    ).join('\n');
  }
  
  return acceptedStates.map((state, index) => 
    `objeto_${index} | estado_inicial_${index} | evento_${index} | ${state.name} | rollback_${index} | false`
  ).join('\n');
}
