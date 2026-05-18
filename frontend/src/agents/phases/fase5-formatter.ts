// FASE_5 Formatter
import { PatternItem } from '../../patterns/index';

export function generateFase5Response(acceptedItems: PatternItem[]): string {
  // FASE_5: Eventos - verificar que tengan acción
  const acceptedEvents = acceptedItems
    .filter(item => item.category === 'evento')
    .map(item => {
      // En una implementación real, estos valores vendrían de los datos del usuario
      // Por ahora usamos valores por defecto basados en lo especificado en el documento
      return {
        evento: item.name,
        origen: 'usuario', // valor por defecto (usuario, temporizador, sistema externo, sensor)
        prioridad: 'alta', // valor por defecto
        accion: 'procesar_evento', // valor por defecto
        timeout: '5000ms', // valor por defecto
        errorStrategy: 'retry' // valor por defecto
      };
    });

  return acceptedEvents.map(event => 
    `${event.evento} | ${event.origen} | ${event.prioridad} | ${event.accion} | ${event.timeout} | ${event.errorStrategy}`
  ).join('\n');
}
