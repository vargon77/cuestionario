// FASE_1 Formatter
import { PatternItem } from '../../patterns/index';

export function generateFase1Response(acceptedItems: PatternItem[]): string {
  // FASE_1: Objetos con formato específico
  const acceptedObjects = acceptedItems
    .filter(item => item.category === 'objeto')
    .map(item => {
      // En una implementación real, estos valores vendrían de los datos del usuario
      // Por ahora usamos valores por defecto basados en lo especificado en el documento
      return {
        nombre: item.name,
        volumenDia: '1000/dia', // valor por defecto, en realidad vendría del usuario
        retencion: '30 dias',   // valor por defecto
        atributos: 'nombre,edad,email', // valor por defecto (3 atributos)
        owner: 'sistema',
        criticidad: 'ALTA'
      };
    });

  // Formatear según la tabla esperada por capture.py
  return acceptedObjects.map(obj => 
    `${obj.nombre} | ${obj.volumenDia} | ${obj.retencion} | ${obj.atributos} | ${obj.owner} | ${obj.criticidad}`
  ).join('\n');
}
