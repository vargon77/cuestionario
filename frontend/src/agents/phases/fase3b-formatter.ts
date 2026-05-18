// FASE_3B Formatter
import { PatternItem } from '../../patterns/index';

export function generateFase3BResponse(acceptedItems: PatternItem[]): string {
  // FASE_3B: Relaciones
  if (acceptedItems.length < 2) {
    return ''; // No hay suficientes ítems para formar relaciones
  }
  
  // Crear algunas relaciones básicas entre los primeros ítems aceptados
  return acceptedItems.slice(0, 3).map((item, index) => {
    const nextIndex = (index + 1) % acceptedItems.length;
    return `${item.name} | pertenece_a | ${acceptedItems[nextIndex].name} | 1:N | cascada | true`;
  }).join('\n');
}
