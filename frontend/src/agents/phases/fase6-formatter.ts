// FASE_6 Formatter
import { PatternItem } from '../../patterns/index';

export function generateFase6Response(acceptedItems: PatternItem[]): string {
  // FASE_6: Tiempo - números con unidades o DESCONOCIDO
  const acceptedTimeElements = acceptedItems
    .filter(item => item.category === 'tiempo')
    .map(item => {
      // En una implementación real, estos valores vendrían de los datos del usuario
      // Por ahora usamos valores por defecto basados en lo especificado en el documento
      return {
        elemento: item.name,
        sla: '5000ms', // valor por defecto
        timeout: '10000ms', // valor por defecto
        expiracion: '30000ms', // valor por defecto
        scheduler: 'diario' // valor por defecto
      };
    });

  return acceptedTimeElements.map(time => 
    `${time.elemento} | ${time.sla} | ${time.timeout} | ${time.expiracion} | ${time.scheduler}`
  ).join('\n');
}
