// FASE_0 Formatter
import { PatternItem } from '../../patterns/index';

export function generateFase0Response(acceptedItems: PatternItem[]): string {
  // FASE_0: Actor seed - solo necesitamos el objetivo/raw goal
  // En esta fase, aceptamos cualquier texto como objetivo
  if (acceptedItems.length > 0) {
    return acceptedItems[0].name;
  }
  // Si no hay ítems aceptados, retornamos vacío (el backend debería usar el user_input directamente)
  return '';
}
