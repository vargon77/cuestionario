// FASE_2 Formatter
import { PatternItem } from '../../patterns/index';

export function generateFase2Response(acceptedItems: PatternItem[]): string {
  // FASE_2: Operaciones con formato específico
  const acceptedOperations = acceptedItems
    .filter(item => item.category === 'operacion')
    .map(item => {
      // En una implementación real, estos valores vendrían de los datos del usuario
      // Por ahora usamos valores por defecto basados en lo especificado en el documento
      return {
        nombre: item.name,
        actor: 'usuario', // valor por defecto
        objetos: 'pedido', // valor por defecto (puede ser múltiples)
        trigger: 'solicitud',
        resultado: 'completado',
        criticidad: 'ALTA'
      };
    });

  // Formatear según la tabla esperada por capture.py
  return acceptedOperations.map(op => 
    `${op.nombre} | ${op.actor} | ${op.objetos} | ${op.trigger} | ${op.resultado} | ${op.criticidad}`
  ).join('\n');
}
