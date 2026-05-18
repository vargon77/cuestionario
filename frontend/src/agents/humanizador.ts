// src/agents/humanizador.ts
import { SystemPattern, getItemsForPhase } from '../patterns/index';

export class Humanizador {
  /**
   * Convierte prompt técnico del backend en lenguaje natural amigable
   */
  static toHuman(
    promptBackend: string,
    fase: string,
    pattern?: SystemPattern
  ): string {
    // Si el prompt ya es amigable, devolverlo
    if (this.isAlreadyHumanFriendly(promptBackend)) {
      return promptBackend;
    }

    switch (fase) {
      case 'FASE_0':
        return this.humanizarActores(promptBackend, pattern);
      case 'FASE_1':
        return this.humanizarObjetos(promptBackend, pattern);
      case 'FASE_2':
        return this.humanizarOperaciones(promptBackend, pattern);
      case 'FASE_3':
        return this.humanizarEstados(promptBackend, pattern);
      case 'FASE_3B':
        return this.humanizarRelaciones(promptBackend, pattern);
      case 'FASE_4':
        return this.humanizarReglas(promptBackend, pattern);
      case 'FASE_5':
        return this.humanizarEventos(promptBackend, pattern);
      case 'FASE_6':
        return this.humanizarTiempo(promptBackend, pattern);
      case 'FASE_7':
        return this.humanizarRecursos(promptBackend, pattern);
      case 'FASE_7B':
        return this.humanizarEspacio(promptBackend, pattern);
      case 'FASE_7C':
        return this.humanizarComunicacion(promptBackend, pattern);
      case 'FASE_8':
        return this.humanizarModulos(promptBackend, pattern);
      case 'FASE_8B':
        return this.humanizarObjetivos(promptBackend, pattern);
      default:
        return promptBackend;
    }
  }

  private static isAlreadyHumanFriendly(prompt: string): boolean {
    // Si tiene signos de interrogación, saludos o lenguaje natural
    const humanIndicators = [/¿|\?/, /Hola/, /Gracias/, /cuéntame/, /dime/];
    return humanIndicators.some(pattern => pattern.test(prompt));
  }

  private static humanizarActores(prompt: string, pattern?: SystemPattern): string {
    const actorExamples = pattern 
      ? getItemsForPhase(pattern, 'FASE_0').slice(0, 3).map(a => a.name).join(', ')
      : 'usuarios, administradores, clientes';
    
    return `Excelente. Para comenzar, necesito entender quiénes interactuarán con el sistema.

**Cuéntame sobre los actores o roles** que usarán este sistema. Por ejemplo:
- ${actorExamples}
- Otros roles específicos de tu negocio

Describe brevemente cada actor y qué funciones principales realizaría.`;
  }

  private static humanizarObjetos(prompt: string, pattern?: SystemPattern): string {
    const objectExamples = pattern
      ? getItemsForPhase(pattern, 'FASE_1').slice(0, 4).map(o => o.name).join(', ')
      : 'clientes, productos, pedidos, facturas';
    
    return `Perfecto. Ahora pasemos a los **objetos o entidades** que maneja tu sistema.

¿Qué información almacenará? Por ejemplo: ${objectExamples}

Para cada objeto, dime:
• **Volumen**: ¿cuántas operaciones por día? (ej: 1000/día)
• **Retención**: ¿cuánto tiempo se guardan los datos? (ej: 30 días)
• **Atributos**: ¿qué campos principales tiene? (3-5 atributos)
• **Owner**: ¿quién es el dueño de esos datos?
• **Criticidad**: ALTA / MEDIA / BAJA`;
  }

  private static humanizarOperaciones(prompt: string, pattern?: SystemPattern): string {
    const operationExamples = pattern
      ? getItemsForPhase(pattern, 'FASE_2').slice(0, 3).map(o => o.name).join(', ')
      : 'crear, actualizar, eliminar, consultar';
    
    return `Gracias. Ahora necesito entender las **operaciones** que el sistema debe realizar.

¿Qué acciones pueden ejecutar los usuarios? Por ejemplo: ${operationExamples}

Para cada operación, especifica:
• **Actor**: ¿quién la ejecuta?
• **Objetos**: ¿sobre qué entidades opera?
• **Trigger**: ¿qué la desencadena?
• **Resultado esperado**
• **Criticidad**: ALTA / MEDIA / BAJA`;
  }

  private static humanizarEstados(prompt: string, pattern?: SystemPattern): string {
    return `Muy bien. Ahora hablemos de los **estados** que pueden tener las entidades.

¿Qué estados pueden tener los objetos principales? 
Por ejemplo: activo, inactivo, suspendido, procesando, completado.

Describe al menos 3 estados y qué eventos causan las transiciones entre ellos.`;
  }

  private static humanizarRelaciones(prompt: string, pattern?: SystemPattern): string {
    return `Excelente. Ahora necesito entender las **relaciones** entre entidades.

¿Cómo se conectan los objetos entre sí?
• ¿Una entidad "pertenece a" otra?
• ¿Es relación 1:1, 1:N o N:M?
• ¿Hay cascada al eliminar?

Por ejemplo: "Pedido | pertenece_a | Cliente | N:1"`;
  }

  private static humanizarReglas(prompt: string, pattern?: SystemPattern): string {
    return `Perfecto. Ahora definamos las **reglas de negocio** (lo que NO se puede hacer).

¿Qué restricciones o prohibiciones debe tener el sistema?
Ejemplos:
• "No acceder a datos sin autorización"
• "No eliminar registros de auditoría"
• "No permitir inventario negativo"

Necesito al menos 5 reglas. Cada regla debe incluir:
• Condición que la activa
• Acción de rechazo (denegar, cancelar, alertar)
• Severidad (alta/media/baja)`;
  }

  private static humanizarEventos(prompt: string, pattern?: SystemPattern): string {
    return `Gracias. Ahora hablemos de los **eventos** que disparan acciones automáticas.

¿Qué cosas "que pasan" en tu negocio deben activar procesos?
Ejemplos:
• "LeadCreado" → enviar email de bienvenida
• "PagoFallido" → reintentar 3 veces
• "StockBajo" → generar orden de compra

Para cada evento, necesito:
• Origen (usuario, temporizador, sistema externo)
• Prioridad (alta/media/baja)
• Acción a ejecutar
• Timeout (ej: 5000ms)
• Estrategia de error (retry, cancelar, notificar)`;
  }

  private static humanizarTiempo(prompt: string, pattern?: SystemPattern): string {
    return `Muy bien. Ahora definamos los **tiempos y SLAs** del sistema.

¿Qué plazos deben cumplirse?
• SLA de respuesta: ¿en cuánto tiempo debe procesarse?
• Timeout de operaciones
• Caducidad de datos o sesiones
• Programación de tareas (diario, semanal, mensual)

Ejemplo: "5000ms | 10000ms | 30 días | diario"

Usa unidades: ms, s, min, h, días, meses.`;
  }

  private static humanizarRecursos(prompt: string, pattern?: SystemPattern): string {
    return `Perfecto. Ahora necesito entender los **recursos limitantes** del sistema.

¿Qué recursos pueden agotarse?
• API calls por segundo
• Almacenamiento disponible
• Conexiones simultáneas
• CPU/Memoria

Para cada recurso, dime:
• Límite máximo
• Unidad (porcentaje, número, GB)
• Comportamiento al degradar
• Qué monitorear`;
  }

  private static humanizarEspacio(prompt: string, pattern?: SystemPattern): string {
    return `Excelente. Ahora hablemos del **espacio/ubicación** de los componentes.

¿Dónde se ejecutarán los servicios?
• Cloud (AWS, Azure, GCP) ¿qué región?
• On-premise ¿qué datacenter?
• Edge ¿dispositivos locales?

También necesito saber:
• Estrategia de replicación
• Latencia máxima aceptable entre componentes`;
  }

  private static humanizarComunicacion(prompt: string, pattern?: SystemPattern): string {
    return `Muy bien. Ahora definamos la **comunicación** entre componentes.

¿Cómo se comunican los servicios?
• Protocolo: REST, gRPC, GraphQL, WebSocket, Message Queue
• ¿Síncrono o asíncrono?
• ¿Cuántos reintentos?
• ¿Garantía de orden de mensajes?

Para cada par emisor-receptor, especifica estos detalles.`;
  }

  private static humanizarModulos(prompt: string, pattern?: SystemPattern): string {
    return `Perfecto. Estamos cerca del final. Ahora hablaremos de los **módulos opcionales**.

Basado en los patrones del sistema, se sugieren estos módulos. ¿Cuáles incluirías?
• Puedes ACEPTAR (incluir en V1)
• RECHAZAR (no incluir)
• ACEPTAR_V2 (para versión futura)

Tómate un momento para revisar cada propuesta.`;
  }

  private static humanizarObjetivos(prompt: string, pattern?: SystemPattern): string {
    return `Excelente. Para terminar, definamos los **objetivos de negocio** y KPIs.

¿Qué quieres lograr con este sistema?
Ejemplos:
• "Reducir tiempo de respuesta 50%" (KPI: respuesta_promedio_ms)
• "Aumentar conversión 20%" (KPI: tasa_conversion)
• "Disminuir costos operativos 30%" (KPI: costo_por_transaccion)

Para cada objetivo, dime:
• KPI medible
• Prioridad (alta/media/baja)
• Trade-offs aceptables (costo vs velocidad, seguridad vs usabilidad)
• Horizonte de logro (trimestral, anual)`;
  }
}