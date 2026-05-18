// src/agents/phases/fase7c-formatter.ts
import { PatternItem } from '../../patterns/index';

export function generateFase7CResponse(acceptedItems: PatternItem[]): string {
  // FASE_7C: Comunicación - debe tener protocolo
  // Usar categoría 'comunicacion' según la biblioteca de patrones
  const acceptedCommunications = acceptedItems
    .filter(item => item.category === 'comunicacion')
    .map(item => {
      return {
        emisor: item.name,
        receptor: 'servicio_rest',
        protocolo: 'REST',
        syncAsync: 'async',
        retry: '3',
        ordenGarantizado: 'garantizado'
      };
    });

  // Si no hay comunicaciones aceptadas, retornar valores por defecto
  if (acceptedCommunications.length === 0) {
    return 'sistema | servicio_rest | REST | async | 3 | garantizado';
  }

  return acceptedCommunications.map(comm => 
    `${comm.emisor} | ${comm.receptor} | ${comm.protocolo} | ${comm.syncAsync} | ${comm.retry} | ${comm.ordenGarantizado}`
  ).join('\n');
}