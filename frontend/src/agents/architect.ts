// src/agents/architect.ts
import { callLLM } from '../services/llm';
import {
  SystemPattern,
  PatternItem,
  getMissingItems,
  getItemsForPhase,
} from '../patterns/index';
import { Tecnificador } from './tecnificador';
import { Humanizador } from './humanizador';

import { generateFase0Response } from './phases/fase0-formatter';
import { generateFase1Response } from './phases/fase1-formatter';
import { generateFase2Response } from './phases/fase2-formatter';
import { generateFase3Response } from './phases/fase3-formatter';
import { generateFase3BResponse } from './phases/fase3b-formatter';
import { generateFase4Response } from './phases/fase4-formatter';
import { generateFase5Response } from './phases/fase5-formatter';
import { generateFase6Response } from './phases/fase6-formatter';
import { generateFase7Response } from './phases/fase7-formatter';
import { generateFase7BResponse } from './phases/fase7b-formatter';
import { generateFase7CResponse } from './phases/fase7c-formatter';
import { generateFase8Response } from './phases/fase8-formatter';
import { generateFase8BResponse } from './phases/fase8b-formatter';
import { advanceSession, submitCheckpoint } from '../api';

export type ProposalStatus = 'pendiente' | 'aceptado' | 'rechazado' | 'futuro';

export interface Proposal {
  item: PatternItem;
  status: ProposalStatus;
  userValues?: Record<string, string>;
}

export interface ArchitectMessage {
  role: 'architect' | 'user';
  content: string;
  proposals?: Proposal[];
}

export interface BackendResponse {
  prompt: string;
  nextPhase: string;
  isCheckpoint?: boolean;
  score?: number;
}

const CHECKPOINT_PHASES = new Set(['FASE_11', 'FASE_18']);

export class ArchitectAgent {
  private pattern: SystemPattern;
  private currentPhase: string;
  private messages: ArchitectMessage[];
  private existingItems: string[];
  private acceptedItems: string[];
  private sessionId: string;
  private userContext: Record<string, any>;

  constructor(pattern: SystemPattern, sessionId?: string) {
    this.pattern = pattern;
    this.currentPhase = 'FASE_0';
    this.messages = [];
    this.existingItems = [];
    this.acceptedItems = [];
    this.sessionId = sessionId || this.generateSessionId();
    this.userContext = {};

    const initialPrompt = Humanizador.toHuman('', 'FASE_0', this.pattern);
    this.messages.push({
      role: 'architect',
      content: initialPrompt,
      proposals: this.getInitialProposals(),
    });
  }

  private generateSessionId(): string {
    const suffix = Math.random().toString(36).substring(2, 8);
    return `${this.pattern.id.toLowerCase()}-${suffix}`;
  }

  getSessionId(): string {
    return this.sessionId;
  }

  setPhase(phase: string): void {
    this.currentPhase = phase;
  }

  getPhase(): string {
    return this.currentPhase;
  }

  getMessages(): ArchitectMessage[] {
    return this.messages;
  }

  getPattern(): SystemPattern {
    return this.pattern;
  }

  getAcceptedItems(): string[] {
    return this.acceptedItems;
  }

  getPendingProposals(): Proposal[] {
    const lastMessage = this.messages[this.messages.length - 1];
    if (lastMessage?.proposals) {
      return lastMessage.proposals.filter(p => p.status === 'pendiente');
    }
    return [];
  }

  deferProposal(itemName: string): void {
  this.updateProposalStatus(itemName, 'futuro');
  }

  /**
   * Procesa la respuesta del usuario y genera la siguiente interacción.
   * TECNIFICAR → BACKEND (advanceSession o submitCheckpoint) → HUMANIZAR
   */
  async processUserResponse(userText: string): Promise<ArchitectMessage> {
    // 1. Registrar mensaje del usuario
    this.messages.push({ role: 'user', content: userText });

    // 2. Extraer ítems mencionados por el usuario
    const mentionedItems = this.extractMentionedItems(userText);
    this.existingItems.push(...mentionedItems);

    // 3. TECNIFICAR: convertir respuesta humana a formato backend
    const pendingProposals = this.getPendingProposals();
    const structuredPayload = Tecnificador.toBackend(
      userText,
      this.currentPhase,
      pendingProposals,
      this.userContext
    );

    // 4. Llamar al backend con el cliente correcto
    let backendResponse: BackendResponse;
    try {
      if (CHECKPOINT_PHASES.has(this.currentPhase)) {
        // FASE_11 y FASE_18 usan el endpoint de checkpoint
        const result = await submitCheckpoint(this.sessionId, structuredPayload);
        backendResponse = {
          prompt: result.prompt ?? '',
          nextPhase: result.next_phase ?? this.currentPhase,
          isCheckpoint: false,
        };
      } else {
        // Resto de fases usan advance
        const result = await advanceSession(this.sessionId, structuredPayload);
        backendResponse = {
          prompt: result.prompt ?? '',
          nextPhase: result.next_phase ?? this.currentPhase,
          isCheckpoint: result.gate?.status === 'NEEDS_HUMAN',
        };
      }
    } catch (error) {
      console.error('Backend error:', error);
      backendResponse = {
        prompt: 'Hubo un error de comunicación. Por favor, intenta nuevamente.',
        nextPhase: this.currentPhase,
      };
    }

    // 5. HUMANIZAR: convertir prompt técnico a lenguaje natural
    const humanizedPrompt = Humanizador.toHuman(
      backendResponse.prompt,
      backendResponse.nextPhase,
      this.pattern
    );

    // 6. Actualizar fase con la que devuelve el backend
    this.currentPhase = backendResponse.nextPhase;

    // 7. Generar propuestas para la nueva fase
    const phaseItems = getItemsForPhase(this.pattern, this.currentPhase);
    const missing = phaseItems.filter(
      item =>
        !this.existingItems.includes(item.name) &&
        !this.acceptedItems.includes(item.name)
    );
    const newProposals: Proposal[] = missing.slice(0, 8).map(item => ({
      item,
      status: 'pendiente',
      userValues: {},
    }));

    // 8. Redactar mensaje del Arquitecto con LLM (solo redacción)
    let architectContent: string;
    try {
      architectContent = await this.generateArchitectMessage(
        userText,
        humanizedPrompt,
        newProposals
      );
    } catch {
      architectContent = this.generateFallbackMessage(humanizedPrompt, newProposals.length);
    }

    const responseMessage: ArchitectMessage = {
      role: 'architect',
      content: architectContent,
      proposals: newProposals,
    };

    this.messages.push(responseMessage);
    return responseMessage;
  }

  acceptProposal(itemName: string, userValues?: Record<string, string>): void {
    if (!this.acceptedItems.includes(itemName)) {
      this.acceptedItems.push(itemName);
    }
    if (userValues) {
      this.userContext = { ...this.userContext, ...userValues };
    }
    this.updateProposalStatus(itemName, 'aceptado', userValues);
  }

  rejectProposal(itemName: string): void {
    this.updateProposalStatus(itemName, 'rechazado');
  }

  // Reemplazar parseModulos completo:
  private static parseModulos(text: string, accepted: Proposal[]): string {
    const lines: string[] = [];

    for (const proposal of accepted) {
      // Mapear estado del frontend al contrato del backend
      const decisionMap: Record<ProposalStatus, string> = {
        aceptado:  'ACEPTADO_V1',
        futuro:    'FUTURO',
        rechazado: 'EXCLUSION',
        pendiente: '',            // sin decisión todavía, no enviar
      };

      const decision = decisionMap[proposal.status];
      if (!decision) continue;   // omitir pendientes

      lines.push(`${proposal.item.name} | ${decision}`);
    }

   return lines.join('\n');
  }

  private updateProposalStatus(
    itemName: string,
    status: ProposalStatus,
    userValues?: Record<string, string>
  ): void {
    for (const msg of this.messages) {
      if (msg.proposals) {
        for (const prop of msg.proposals) {
          if (prop.item.name === itemName) {
            prop.status = status;
            if (userValues) {
              prop.userValues = userValues;
            }
            return;
          }
        }
      }
    }
  }

  generateStructuredResponse(): string {
    const accepted = this.pattern.items.filter(item =>
      this.acceptedItems.includes(item.name)
    );
    switch (this.currentPhase) {
      case 'FASE_0':  return generateFase0Response(accepted);
      case 'FASE_1':  return generateFase1Response(accepted);
      case 'FASE_2':  return generateFase2Response(accepted);
      case 'FASE_3':  return generateFase3Response(accepted);
      case 'FASE_3B': return generateFase3BResponse(accepted);
      case 'FASE_4':  return generateFase4Response(accepted);
      case 'FASE_5':  return generateFase5Response(accepted);
      case 'FASE_6':  return generateFase6Response(accepted);
      case 'FASE_7':  return generateFase7Response(accepted);
      case 'FASE_7B': return generateFase7BResponse(accepted);
      case 'FASE_7C': return generateFase7CResponse(accepted);
      case 'FASE_8':  return generateFase8Response(accepted);
      case 'FASE_8B': return generateFase8BResponse(accepted);
      default:
        return accepted
          .map(item => `${item.name} | ${item.category} | ${item.priority}`)
          .join('\n');
    }
  }

  getPrefilledText(): string {
    const acceptedProposals = this.getAcceptedProposalsFromLastMessage();
    if (acceptedProposals.length === 0) return '';
    return acceptedProposals
      .map(prop => {
        const item = prop.item;
        switch (item.category) {
          case 'objeto':
            return `${item.name} | DESCONOCIDO | DESCONOCIDO | id,nombre | sistema | ${item.priority}`;
          case 'operacion':
            return `${item.name} | sistema | entidad | evento | exitoso | ${item.priority}`;
          default:
            return `${item.name}`;
        }
      })
      .join('\n');
  }

  private getAcceptedProposalsFromLastMessage(): Proposal[] {
    const lastMessage = this.messages[this.messages.length - 1];
    if (lastMessage?.proposals) {
      return lastMessage.proposals.filter(p => p.status === 'aceptado');
    }
    return [];
  }

  private extractMentionedItems(text: string): string[] {
    const lowerText = text.toLowerCase();
    return this.pattern.items
      .filter(item => {
        const itemLower = item.name.toLowerCase();
        return (
          lowerText.includes(itemLower) ||
          itemLower.split(' ').some(word => word.length > 3 && lowerText.includes(word))
        );
      })
      .map(item => item.name);
  }

  private async generateArchitectMessage(
    userText: string,
    humanizedPrompt: string,
    proposals: Proposal[]
  ): Promise<string> {
    const prompt = `Eres un Arquitecto de Sistemas experto entrevistando a un cliente.

Contexto del sistema: **${this.pattern.display}** - ${this.pattern.description}

Lo que dijo el usuario: "${userText}"

El sistema necesita saber esto: "${humanizedPrompt}"

Basado en la Biblioteca de Patrones, estos son los elementos típicos que el usuario no ha mencionado:
${proposals.map(p => `- ${p.item.name} (${p.item.category}): ${p.item.rationale}`).join('\n')}

Redacta un mensaje profesional y amigable en español que:
1. Reconozca amablemente lo que el usuario dijo
2. Explique qué necesita saber el sistema (usa el humanizedPrompt)
3. Mencione brevemente las propuestas (solo mencionarlas, no las expliques todas)
4. Invite al usuario a responder

NO generes propuestas nuevas fuera de la lista. Sé cálido pero profesional. Máximo 4 párrafos.`;

    try {
      return await callLLM(prompt);
    } catch {
      return this.generateFallbackMessage(humanizedPrompt, proposals.length);
    }
  }

  private generateFallbackMessage(humanizedPrompt: string, proposalCount: number): string {
    if (proposalCount === 0) {
      return `${humanizedPrompt}\n\n¿Podrías compartir más detalles sobre lo que necesitas?`;
    }
    return `${humanizedPrompt}\n\nTe voy a sugerir ${proposalCount} elementos típicos en sistemas ${this.pattern.display}. ¿Me confirmas cuáles aplican a tu caso?`;
  }

  private getInitialProposals(): Proposal[] {
    const actors = this.pattern.items.filter(i => i.category === 'actor');
    const objects = this.pattern.items.filter(i => i.category === 'objeto').slice(0, 3);
    return [...actors, ...objects].map(item => ({
      item,
      status: 'pendiente',
      userValues: {},
    }));
  }
}

export function generateSessionId(patternId: string): string {
  const suffix = Math.random().toString(36).substring(2, 6);
  return `${patternId.toLowerCase()}-${suffix}`;
}

export function detectProvider(): 'deepseek' | 'gemini' | null {
  const env = typeof import.meta !== 'undefined' ? (import.meta as any).env : {};
  if (env.VITE_DEEPSEEK_API_KEY) return 'deepseek';
  if (env.VITE_GEMINI_API_KEY) return 'gemini';
  return null;
}