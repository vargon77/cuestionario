// FASE_7 Formatter
import { PatternItem } from '../../patterns/index';

export function generateFase7Response(acceptedItems: PatternItem[]): string {
  // FASE_7: Recursos - números con unidades o DESCONOCIDO
  const acceptedResources = acceptedItems
    .filter(item => item.category === 'recurso')
    .map(item => {
      // En una implementación real, estos valores vendrían de los datos del usuario
      // Por ahora usamos valores por defecto basados en lo especificado en el documento
      return {
        recurso: item.name,
        maximo: '100', // valor por defecto
        unidad: 'porcentaje', // valor por defecto
        degradacion: 'degradar_linealmente', // valor por defecto
        monitoreo: 'monitoreo_basico' // valor por defecto
      };
    });

  return acceptedResources.map(resource => 
    `${resource.recurso} | ${resource.maximo} | ${resource.unidad} | ${resource.degradacion} | ${resource.monitoreo}`
  ).join('\n');
}
