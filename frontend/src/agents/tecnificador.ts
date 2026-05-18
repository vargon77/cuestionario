// src/agents/tecnificador.ts
import { PatternItem } from '../patterns/index';
import { Proposal } from './architect';

export interface ParsedObject {
  nombre: string;
  volumenDia: string;
  retencion: string;
  atributos: string;
  owner: string;
  criticidad: string;
}

export interface ParsedOperation {
  nombre: string;
  actor: string;
  objetos: string;
  trigger: string;
  resultado: string;
  criticidad: string;
}

export interface ParsedState {
  objeto: string;
  estadoInicial: string;
  evento: string;
  nombre: string;
  rollback: string;
  esFinal: boolean;
}

export interface ParsedRule {
  regla: string;
  tipo: string;
  condicion: string;
  rechazo: string;
  severidad: string;
}

export interface ParsedEvent {
  evento: string;
  origen: string;
  prioridad: string;
  accion: string;
  timeout: string;
  errorStrategy: string;
}

export interface ParsedTime {
  elemento: string;
  sla: string;
  timeout: string;
  expiracion: string;
  scheduler: string;
}

export interface ParsedResource {
  recurso: string;
  maximo: string;
  unidad: string;
  degradacion: string;
  monitoreo: string;
}

export interface ParsedSpace {
  componente: string;
  ubicacion: string;
  region: string;
  replicacion: string;
  latenciaMax: string;
}

export interface ParsedCommunication {
  emisor: string;
  receptor: string;
  protocolo: string;
  syncAsync: string;
  retry: string;
  ordenGarantizado: string;
}

export interface ParsedModule {
  modulo: string;
  decision: string;
}

export interface ParsedObjective {
  objetivo: string;
  kpi: string;
  prioridad: string;
  tradeoff: string;
  horizonte: string;
}

export class Tecnificador {
  /**
   * Convierte respuesta del humano en formato estructurado para backend
   */
  static toBackend(
    respuestaHumana: string,
    fase: string,
    acceptedProposals: Proposal[],
    userExtractedData?: Record<string, any>
  ): string {
    switch (fase) {
      case 'FASE_0':
        return this.parseActores(respuestaHumana, acceptedProposals);
      case 'FASE_1':
        return this.parseObjetos(respuestaHumana, acceptedProposals, userExtractedData);
      case 'FASE_2':
        return this.parseOperaciones(respuestaHumana, acceptedProposals, userExtractedData);
      case 'FASE_3':
        return this.parseEstados(respuestaHumana, acceptedProposals, userExtractedData);
      case 'FASE_3B':
        return this.parseRelaciones(respuestaHumana, acceptedProposals);
      case 'FASE_4':
        return this.parseReglas(respuestaHumana, acceptedProposals, userExtractedData);
      case 'FASE_5':
        return this.parseEventos(respuestaHumana, acceptedProposals, userExtractedData);
      case 'FASE_6':
        return this.parseTiempo(respuestaHumana, acceptedProposals, userExtractedData);
      case 'FASE_7':
        return this.parseRecursos(respuestaHumana, acceptedProposals, userExtractedData);
      case 'FASE_7B':
        return this.parseEspacio(respuestaHumana, acceptedProposals, userExtractedData);
      case 'FASE_7C':
        return this.parseComunicacion(respuestaHumana, acceptedProposals, userExtractedData);
      case 'FASE_8':
        return this.parseModulos(respuestaHumana, acceptedProposals);
      case 'FASE_8B':
        return this.parseObjetivos(respuestaHumana, acceptedProposals, userExtractedData);
      default:
        return respuestaHumana;
    }
  }

  private static parseActores(text: string, accepted: Proposal[]): string {
    // Para FASE_0, el backend espera el texto crudo como "raw goal"
    // Los actores se extraen pero se envían después
    return text.trim();
  }

  private static parseObjetos(
    text: string,
    accepted: Proposal[],
    userData?: Record<string, any>
  ): string {
    const objects: ParsedObject[] = [];

    for (const proposal of accepted) {
      if (proposal.status !== 'aceptado') continue;

      // Intentar extraer del texto del usuario
      const extracted = this.extractObjectFromText(text, proposal.item.name);
      
      objects.push({
        nombre: proposal.item.name,
        volumenDia: extracted.volumenDia || userData?.[`${proposal.item.name}_volumen`] || 'DESCONOCIDO',
        retencion: extracted.retencion || userData?.[`${proposal.item.name}_retencion`] || 'DESCONOCIDO',
        atributos: extracted.atributos || 'nombre,id,estado',
        owner: extracted.owner || 'sistema',
        criticidad: proposal.item.priority,
      });
    }

    return objects.map(obj => 
      `${obj.nombre} | ${obj.volumenDia} | ${obj.retencion} | ${obj.atributos} | ${obj.owner} | ${obj.criticidad}`
    ).join('\n');
  }

  private static extractObjectFromText(text: string, objectName: string): Partial<ParsedObject> {
    const lowerText = text.toLowerCase();
    const result: Partial<ParsedObject> = {};

    // Patrones para extraer volumen (números + /dia, /mes, /año, por día, etc)
    const volumenPattern = /(\d+(?:,\d+)?(?:\.\d+)?)\s*(?:\/|\s*por\s*)(dia|día|day|mes|month|año|year)/i;
    const volumenMatch = lowerText.match(volumenPattern);
    if (volumenMatch) {
      result.volumenDia = `${volumenMatch[1]}/${volumenMatch[2] === 'dia' || volumenMatch[2] === 'día' ? 'dia' : 
                           volumenMatch[2] === 'mes' || volumenMatch[2] === 'month' ? 'mes' : 'año'}`;
    }

    // Patrones para extraer retención
    const retencionPattern = /(\d+(?:\.\d+)?)\s*(dias?|días?|mes(?:es)?|años?|years?|days?)/i;
    const retencionMatch = lowerText.match(retencionPattern);
    if (retencionMatch) {
      result.retencion = `${retencionMatch[1]} ${retencionMatch[2]}`;
    }

    // Atributos mencionados
    const atributosPattern = /(atributos?|campos?|fields?):\s*([^.]+)/i;
    const atributosMatch = lowerText.match(atributosPattern);
    if (atributosMatch) {
      result.atributos = atributosMatch[2].trim().replace(/\s+/g, ',');
    }

    return result;
  }

  private static parseOperaciones(
    text: string,
    accepted: Proposal[],
    userData?: Record<string, any>
  ): string {
    const operations: ParsedOperation[] = [];

    for (const proposal of accepted) {
      if (proposal.status !== 'aceptado') continue;

      const extracted = this.extractOperationFromText(text, proposal.item.name);

      operations.push({
        nombre: proposal.item.name,
        actor: extracted.actor || userData?.[`${proposal.item.name}_actor`] || 'sistema',
        objetos: extracted.objetos || 'entidad',
        trigger: extracted.trigger || 'evento',
        resultado: extracted.resultado || 'exitoso',
        criticidad: proposal.item.priority,
      });
    }

    return operations.map(op => 
      `${op.nombre} | ${op.actor} | ${op.objetos} | ${op.trigger} | ${op.resultado} | ${op.criticidad}`
    ).join('\n');
  }

  private static extractOperationFromText(text: string, operationName: string): Partial<ParsedOperation> {
    const lowerText = text.toLowerCase();
    const result: Partial<ParsedOperation> = {};

    // Extraer actor (quién ejecuta)
    const actorPattern = /(?:el|la|los|las)\s+([a-záéíóúñ]+)\s+(?:realiza|ejecuta|hace|ejecutaría)/i;
    const actorMatch = lowerText.match(actorPattern);
    if (actorMatch) {
      result.actor = actorMatch[1];
    }

    // Extraer trigger
    const triggerPattern = /(?:cuando|si|al)\s+([^.]+?)(?:\s+se|\s+ocurr|$)/i;
    const triggerMatch = lowerText.match(triggerPattern);
    if (triggerMatch) {
      result.trigger = triggerMatch[1].trim();
    }

    return result;
  }

  private static parseEstados(
    text: string,
    accepted: Proposal[],
    userData?: Record<string, any>
  ): string {
    const states: ParsedState[] = [];
    const defaultObject = userData?.defaultObject || 'entidad';

    for (let i = 0; i < Math.max(accepted.length, 3); i++) {
      const proposal = accepted[i];
      const stateName = proposal?.status === 'aceptado' ? proposal.item.name : this.getDefaultState(i);
      
      states.push({
        objeto: defaultObject,
        estadoInicial: i === 0 ? 'inicial' : `estado_${i}`,
        evento: `evento_${i}`,
        nombre: stateName,
        rollback: `rollback_${i}`,
        esFinal: i === states.length - 1,
      });
    }

    return states.map(state => 
      `${state.objeto} | ${state.estadoInicial} | ${state.evento} | ${state.nombre} | ${state.rollback} | ${state.esFinal}`
    ).join('\n');
  }

  private static getDefaultState(index: number): string {
    const defaults = ['activo', 'inactivo', 'suspendido', 'eliminado', 'archivado'];
    return defaults[index % defaults.length];
  }

  private static parseRelaciones(text: string, accepted: Proposal[]): string {
    const acceptedNames = accepted
      .filter(p => p.status === 'aceptado')
      .map(p => p.item.name);
    
    if (acceptedNames.length < 2) return '';

    const relations: string[] = [];
    for (let i = 0; i < acceptedNames.length - 1; i++) {
      relations.push(`${acceptedNames[i]} | pertenece_a | ${acceptedNames[i + 1]} | 1:N | cascada | true`);
    }

    return relations.join('\n');
  }

  private static parseReglas(
    text: string,
    accepted: Proposal[],
    userData?: Record<string, any>
  ): string {
    const rules: ParsedRule[] = [];
    const acceptedRules = accepted.filter(p => p.status === 'aceptado');

    for (const proposal of acceptedRules) {
      const extracted = this.extractRuleFromText(text, proposal.item.name);
      
      rules.push({
        regla: proposal.item.name,
        tipo: extracted.tipo || 'negocio',
        condicion: extracted.condicion || 'siempre',
        rechazo: extracted.rechazo || 'denegar',
        severidad: proposal.item.priority === 'ALTA' ? 'alta' : 'media',
      });
    }

    // Mínimo 5 reglas
    while (rules.length < 5) {
      rules.push({
        regla: `Regla_${rules.length + 1}`,
        tipo: 'seguridad',
        condicion: 'siempre',
        rechazo: 'denegar',
        severidad: 'media',
      });
    }

    return rules.map(rule => 
      `${rule.regla} | ${rule.tipo} | ${rule.condicion} | ${rule.rechazo} | ${rule.severidad}`
    ).join('\n');
  }

  private static extractRuleFromText(text: string, ruleName: string): Partial<ParsedRule> {
    const lowerText = text.toLowerCase();
    const result: Partial<ParsedRule> = {};

    // Extraer condición
    const condPattern = /(?:cuando|si|en caso de que)\s+([^.]+)/i;
    const condMatch = lowerText.match(condPattern);
    if (condMatch) {
      result.condicion = condMatch[1].trim();
    }

    return result;
  }

  private static parseEventos(
    text: string,
    accepted: Proposal[],
    userData?: Record<string, any>
  ): string {
    const events: ParsedEvent[] = [];
    const acceptedEvents = accepted.filter(p => p.status === 'aceptado');

    for (const proposal of acceptedEvents) {
      events.push({
        evento: proposal.item.name,
        origen: userData?.[`${proposal.item.name}_origen`] || 'sistema',
        prioridad: proposal.item.priority === 'ALTA' ? 'alta' : 'media',
        accion: `procesar_${proposal.item.name.toLowerCase()}`,
        timeout: '5000ms',
        errorStrategy: 'retry',
      });
    }

    return events.map(event => 
      `${event.evento} | ${event.origen} | ${event.prioridad} | ${event.accion} | ${event.timeout} | ${event.errorStrategy}`
    ).join('\n');
  }

  private static parseTiempo(
    text: string,
    accepted: Proposal[],
    userData?: Record<string, any>
  ): string {
    const times: ParsedTime[] = [];
    const acceptedTimes = accepted.filter(p => p.status === 'aceptado');

    for (const proposal of acceptedTimes) {
      const extracted = this.extractTimeFromText(text, proposal.item.name);
      
      times.push({
        elemento: proposal.item.name,
        sla: extracted.sla || userData?.[`${proposal.item.name}_sla`] || 'DESCONOCIDO',
        timeout: extracted.timeout || 'DESCONOCIDO',
        expiracion: extracted.expiracion || 'DESCONOCIDO',
        scheduler: extracted.scheduler || 'diario',
      });
    }

    return times.map(time => 
      `${time.elemento} | ${time.sla} | ${time.timeout} | ${time.expiracion} | ${time.scheduler}`
    ).join('\n');
  }

  private static extractTimeFromText(text: string, timeName: string): Partial<ParsedTime> {
    const lowerText = text.toLowerCase();
    const result: Partial<ParsedTime> = {};

    // Extraer tiempo (números + ms/s/min/h/día)
    const timePattern = /(\d+(?:\.\d+)?)\s*(ms|milisegundos|s|segundos|min|minutos|h|horas|día|días)/i;
    const timeMatch = lowerText.match(timePattern);
    if (timeMatch) {
      const value = timeMatch[1];
      const unit = timeMatch[2];
      const unitMap: Record<string, string> = {
        'ms': 'ms', 'milisegundos': 'ms',
        's': 's', 'segundos': 's',
        'min': 'min', 'minutos': 'min',
        'h': 'h', 'horas': 'h',
        'día': 'd', 'días': 'd',
      };
      result.sla = `${value}${unitMap[unit] || unit}`;
    }

    return result;
  }

  private static parseRecursos(
    text: string,
    accepted: Proposal[],
    userData?: Record<string, any>
  ): string {
    const resources: ParsedResource[] = [];
    const acceptedResources = accepted.filter(p => p.status === 'aceptado');

    for (const proposal of acceptedResources) {
      resources.push({
        recurso: proposal.item.name,
        maximo: userData?.[`${proposal.item.name}_maximo`] || '100',
        unidad: 'porcentaje',
        degradacion: 'degradar_linealmente',
        monitoreo: 'monitoreo_basico',
      });
    }

    return resources.map(res => 
      `${res.recurso} | ${res.maximo} | ${res.unidad} | ${res.degradacion} | ${res.monitoreo}`
    ).join('\n');
  }

  private static parseEspacio(
    text: string,
    accepted: Proposal[],
    userData?: Record<string, any>
  ): string {
    const spaces: ParsedSpace[] = [];
    const acceptedSpaces = accepted.filter(p => p.status === 'aceptado');

    for (const proposal of acceptedSpaces) {
      spaces.push({
        componente: proposal.item.name,
        ubicacion: userData?.[`${proposal.item.name}_ubicacion`] || 'cloud',
        region: userData?.[`${proposal.item.name}_region`] || 'us-east-1',
        replicacion: userData?.[`${proposal.item.name}_replicacion`] || 'activa',
        latenciaMax: userData?.[`${proposal.item.name}_latencia`] || '50ms',
      });
    }

    return spaces.map(space => 
      `${space.componente} | ${space.ubicacion} | ${space.region} | ${space.replicacion} | ${space.latenciaMax}`
    ).join('\n');
  }

  private static parseComunicacion(
    text: string,
    accepted: Proposal[],
    userData?: Record<string, any>
  ): string {
    const communications: ParsedCommunication[] = [];
    const acceptedComms = accepted.filter(p => p.status === 'aceptado');

    for (const proposal of acceptedComms) {
      communications.push({
        emisor: proposal.item.name,
        receptor: userData?.[`${proposal.item.name}_receptor`] || 'servicio',
        protocolo: userData?.[`${proposal.item.name}_protocolo`] || 'REST',
        syncAsync: 'async',
        retry: '3',
        ordenGarantizado: 'garantizado',
      });
    }

    return communications.map(comm => 
      `${comm.emisor} | ${comm.receptor} | ${comm.protocolo} | ${comm.syncAsync} | ${comm.retry} | ${comm.ordenGarantizado}`
    ).join('\n');
  }

  private static parseModulos(text: string, accepted: Proposal[]): string {
    const modules: ParsedModule[] = [];
    const acceptedModules = accepted.filter(p => p.status === 'aceptado');

    for (const proposal of acceptedModules) {
      modules.push({
        modulo: proposal.item.name,
        decision: 'ACEPTADO_V1',
      });
    }

    return modules.map(mod => `${mod.modulo} | ${mod.decision}`).join('\n');
  }

  private static parseObjetivos(
    text: string,
    accepted: Proposal[],
    userData?: Record<string, any>
  ): string {
    const objectives: ParsedObjective[] = [];
    const acceptedObjectives = accepted.filter(p => p.status === 'aceptado');

    for (const proposal of acceptedObjectives) {
      objectives.push({
        objetivo: proposal.item.name,
        kpi: userData?.[`${proposal.item.name}_kpi`] || 'medir_mejora',
        prioridad: proposal.item.priority === 'ALTA' ? 'alta' : 'media',
        tradeoff: 'costo_vs_velocidad',
        horizonte: 'anual',
      });
    }

    return objectives.map(obj => 
      `${obj.objetivo} | ${obj.kpi} | ${obj.prioridad} | ${obj.tradeoff} | ${obj.horizonte}`
    ).join('\n');
  }
}