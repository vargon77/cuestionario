// FASE_8B Formatter
import { PatternItem } from '../../patterns/index';

export function generateFase8BResponse(acceptedItems: PatternItem[]): string {
  // FASE_8B: Objetivos - deben tener KPI
  const acceptedObjectives = acceptedItems
    .filter(item => item.category === 'objetivo')
    .map(item => {
      // En una implementación real, estos valores vendrían de los datos del usuario
      // Por ahora usamos valores por defecto basados en lo especificado en el documento
      return {
        objetivo: item.name,
        kpi: 'reducir_tiempo_20%', // valor por defecto
        prioridad: 'alta', // valor por defecto
        tradeoff: 'costo_vs_velocidad', // valor por defecto
        horizonte: 'anual' // valor por defecto
      };
    });

  return acceptedObjectives.map(obj => 
    `${obj.objetivo} | ${obj.kpi} | ${obj.prioridad} | ${obj.tradeoff} | ${obj.horizonte}`
  ).join('\n');
}
