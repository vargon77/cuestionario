// src/components/ProposalChecklist.tsx
import { useState } from 'react';
import { Proposal } from '../agents/architect';
import { HelpButton } from './HelpButton';

interface ProposalChecklistProps {
  proposals: Proposal[];
  onAccept: (proposal: Proposal, userValues?: Record<string, string>) => void;
  onReject: (proposal: Proposal) => void;
  onDefer: (proposal: Proposal) => void;   // nuevo
  phase: string;
}

export function ProposalChecklist({ proposals, onAccept, onDefer, onReject, phase }: ProposalChecklistProps) {
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const [userInputs, setUserInputs] = useState<Record<string, Record<string, string>>>({});
  const isModulePhase = phase === 'FASE_8' || phase === 'FASE_12';

  const getPhaseSpecificFields = (proposal: Proposal): { label: string; key: string; placeholder: string }[] => {
    const category = proposal.item.category;
    switch (category) {
      case 'objeto':
        return [
          { label: 'Volumen por día', key: 'volumenDia', placeholder: 'Ej: 1000/dia, 5000/mes, DESCONOCIDO' },
          { label: 'Retención', key: 'retencion', placeholder: 'Ej: 30 días, 1 año, indefinido' },
          { label: 'Atributos', key: 'atributos', placeholder: 'nombre, email, teléfono (separados por comas)' },
          { label: 'Owner', key: 'owner', placeholder: 'sistema, vendedor, gerente' },
        ];
      case 'operacion':
        return [
          { label: 'Actor que ejecuta', key: 'actor', placeholder: 'usuario, sistema, administrador' },
          { label: 'Objetos involucrados', key: 'objetos', placeholder: 'pedido, cliente, producto' },
          { label: 'Trigger', key: 'trigger', placeholder: 'evento, temporizador, solicitud' },
        ];
      case 'regla':
        return [
          { label: 'Condición', key: 'condicion', placeholder: 'cuando X sucede' },
          { label: 'Acción de rechazo', key: 'rechazo', placeholder: 'denegar, cancelar, notificar' },
        ];
      case 'evento':
        return [
          { label: 'Origen', key: 'origen', placeholder: 'usuario, temporizador, sistema externo' },
          { label: 'Acción', key: 'accion', placeholder: 'procesar, notificar, almacenar' },
        ];
      case 'tiempo':
        return [
          { label: 'SLA', key: 'sla', placeholder: '5000ms, 30min, 1hora' },
          { label: 'Timeout', key: 'timeout', placeholder: '10000ms' },
        ];
      default:
        return [];
    }
  };

  const handleAcceptWithValues = (proposal: Proposal) => {
    const values = userInputs[proposal.item.name] || {};
    onAccept(proposal, values);
  };

  const updateUserInput = (proposalName: string, key: string, value: string) => {
    setUserInputs(prev => ({
      ...prev,
      [proposalName]: {
        ...prev[proposalName],
        [key]: value,
      },
    }));
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'aceptado': return '✅';
      case 'rechazado': return '❌';
      default: return '⬜';
    }
  };

  const filteredProposals = proposals.filter(p => p.status !== 'rechazado');

  if (filteredProposals.length === 0) return null;

  return (
    <div className="proposal-checklist">
      <div className="proposal-header">
        <span className="proposal-icon">📋</span>
        <span className="proposal-title">Elementos sugeridos para {phase}</span>
      </div>
      // Dentro del render de la pregunta, al lado del título:
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
        <span>FASE_3B — Relaciones</span>
        <HelpButton
          fase="FASE_3B"
          dimension="RELACIONES"
          pregunta="¿Quién pertenece a quién? ¿Qué cardinalidad existe entre los objetos?"
          sistema= "sistema"  // viene del pattern que ya tienes en contexto
        />
      </div>
      
      <div className="proposal-items">
        {filteredProposals.map(proposal => (
          <div key={proposal.item.name} className={`proposal-item ${proposal.status}`}>
            <div className="proposal-item-header">
              <span className="proposal-status">{getStatusIcon(proposal.status)}</span>
              <span className="proposal-name">{proposal.item.name}</span>
              <span className={`proposal-priority priority-${proposal.item.priority.toLowerCase()}`}>
                {proposal.item.priority}
              </span>
              <button
                className="proposal-info-btn"
                onClick={() => setExpandedId(expandedId === proposal.item.name ? null : proposal.item.name)}
              >
                {expandedId === proposal.item.name ? '▲' : '▼'}
              </button>
            </div>
            
            {expandedId === proposal.item.name && (
              <div className="proposal-details">
                <p className="proposal-rationale">{proposal.item.rationale}</p>
                
                {proposal.status === 'pendiente' && (
                  <div className="proposal-actions">
                    <div className="proposal-fields">
                      {getPhaseSpecificFields(proposal).map(field => (
                        <input
                          key={field.key}
                          type="text"
                          className="proposal-field"
                          placeholder={field.placeholder}
                          value={userInputs[proposal.item.name]?.[field.key] || ''}
                          onChange={(e) => updateUserInput(proposal.item.name, field.key, e.target.value)}
                        />
                      ))}
                    </div>
                    <div className="proposal-buttons">
                      <button
                        className="proposal-accept"
                        onClick={() => handleAcceptWithValues(proposal)}
                      >
                        ✅ Incluir en V1
                      </button>
                      {isModulePhase && (
                        <button
                          className="proposal-defer"
                          onClick={() => onDefer(proposal)}
                        >
                          🕐 Para después
                        </button>
                      )}
                      <button
                        className="proposal-reject"
                        onClick={() => onReject(proposal)}
                      >
                        ❌ {isModulePhase ? 'No aplica' : 'Rechazar'}
                      </button>
                    </div>
                  </div>
                )}
                
              </div>
            )}
          </div>
        ))}
      </div>

      <style>{`
        .proposal-checklist {
          background: #0f172a;
          border: 1px solid #334155;
          border-radius: 16px;
          margin-top: 0.75rem;
          overflow: hidden;
        }
        .proposal-header {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          padding: 0.75rem 1rem;
          background: #1e293b;
          border-bottom: 1px solid #334155;
        }
        .proposal-icon {
          font-size: 1rem;
        }
        .proposal-title {
          font-size: 0.8125rem;
          font-weight: 600;
          color: #cbd5e1;
          text-transform: uppercase;
          letter-spacing: 0.5px;
        }
        .proposal-items {
          display: flex;
          flex-direction: column;
        }
        .proposal-item {
          border-bottom: 1px solid #1e293b;
          transition: background 0.2s;
        }
        .proposal-item:last-child {
          border-bottom: none;
        }
        .proposal-item.aceptado {
          background: rgba(34, 197, 94, 0.05);
        }
        .proposal-item-header {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          padding: 0.75rem 1rem;
          cursor: pointer;
        }
        .proposal-item-header:hover {
          background: rgba(59, 130, 246, 0.05);
        }
        .proposal-status {
          font-size: 1rem;
        }
        .proposal-name {
          flex: 1;
          font-weight: 500;
          color: #e2e8f0;
          font-size: 0.875rem;
        }
        .proposal-priority {
          font-size: 0.625rem;
          padding: 2px 6px;
          border-radius: 12px;
          font-weight: 600;
        }
        .priority-alta {
          background: #7f1d1d;
          color: #fecaca;
        }
        .priority-media {
          background: #854d0e;
          color: #fef08a;
        }
        .priority-baja {
          background: #14532d;
          color: #bbf7d0;
        }
        .proposal-info-btn {
          background: none;
          border: none;
          color: #64748b;
          cursor: pointer;
          font-size: 0.75rem;
        }
        .proposal-details {
          padding: 0 1rem 0.75rem 2rem;
        }
        .proposal-rationale {
          font-size: 0.75rem;
          color: #94a3b8;
          margin-bottom: 0.75rem;
          line-height: 1.4;
        }
        .proposal-actions {
          display: flex;
          flex-direction: column;
          gap: 0.75rem;
        }
        .proposal-fields {
          display: flex;
          flex-wrap: wrap;
          gap: 0.5rem;
        }
        .proposal-field {
          flex: 1;
          min-width: 150px;
          background: #1e293b;
          border: 1px solid #334155;
          border-radius: 8px;
          padding: 0.5rem 0.75rem;
          color: #e2e8f0;
          font-size: 0.75rem;
        }
        .proposal-field:focus {
          outline: none;
          border-color: #3b82f6;
        }
        .proposal-field::placeholder {
          color: #64748b;
        }
        .proposal-buttons {
          display: flex;
          gap: 0.5rem;
        }
        .proposal-accept, .proposal-reject {
          padding: 0.375rem 0.75rem;
          border-radius: 8px;
          font-size: 0.75rem;
          font-weight: 500;
          cursor: pointer;
          transition: all 0.2s;
        }
        .proposal-accept {
          background: #22c55e;
          border: none;
          color: white;
        }
        .proposal-accept:hover {
          background: #16a34a;
        }
        .proposal-reject {
          background: #ef4444;
          border: none;
          color: white;
        }
        .proposal-reject:hover {
          background: #dc2626;
        }
        .proposal-accepted-badge {
          color: #22c55e;
          font-size: 0.75rem;
          font-weight: 500;
        }
      `}</style>
    </div>
  );
}