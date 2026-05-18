// src/agents/phases/fase7b-formatter.ts
import { PatternItem } from '../../patterns/index';

export function generateFase7BResponse(acceptedItems: PatternItem[]): string {
  // FASE_7B: Espacio - componentes con ubicación
  // Usar categoría 'espacio' según la biblioteca de patrones
  const acceptedComponents = acceptedItems
    .filter(item => item.category === 'espacio')
    .map(item => {
      return {
        componente: item.name,
        ubicacion: 'cloud',
        region: 'us-east-1',
        replicacion: 'activa',
        latenciaMax: '50ms'
      };
    });

  // Si no hay componentes aceptados, retornar valores por defecto
  if (acceptedComponents.length === 0) {
    return 'sistema | cloud | us-east-1 | activa | 50ms';
  }

  return acceptedComponents.map(comp => 
    `${comp.componente} | ${comp.ubicacion} | ${comp.region} | ${comp.replicacion} | ${comp.latenciaMax}`
  ).join('\n');
}