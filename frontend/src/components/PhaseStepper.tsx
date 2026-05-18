// src/components/PhaseStepper.tsx
interface PhaseStepperProps {
  currentPhase: string;
}

const PHASES = [
  { id: 'FASE_0', name: 'Awareness', description: 'Actores y objetivo' },
  { id: 'FASE_1', name: 'Objetos', description: 'Entidades y datos' },
  { id: 'FASE_2', name: 'Operaciones', description: 'Acciones del sistema' },
  { id: 'FASE_3', name: 'Estados', description: 'Máquina de estados' },
  { id: 'FASE_3B', name: 'Relaciones', description: 'Cardinalidades' },
  { id: 'FASE_4', name: 'Reglas', description: 'Restricciones NO-GO' },
  { id: 'FASE_5', name: 'Eventos', description: 'Disparadores' },
  { id: 'FASE_6', name: 'Tiempo', description: 'SLAs y timeouts' },
  { id: 'FASE_7', name: 'Recursos', description: 'Limitantes' },
  { id: 'FASE_7B', name: 'Espacio', description: 'Ubicación' },
  { id: 'FASE_7C', name: 'Comunicación', description: 'Protocolos' },
  { id: 'FASE_8', name: 'Módulos', description: 'Decisiones' },
  { id: 'FASE_8B', name: 'Objetivos', description: 'KPIs' },
  { id: 'FASE_9', name: 'Score', description: 'Validación' },
  { id: 'FASE_10', name: 'SEC', description: 'Generación' },
  { id: 'FASE_11', name: 'Checkpoint', description: 'Aprobación' },
  { id: 'FASE_18', name: 'Final', description: 'Entrega' },
];

export function PhaseStepper({ currentPhase }: PhaseStepperProps) {
  const currentIndex = PHASES.findIndex(p => p.id === currentPhase);
  
  const getStatus = (index: number) => {
    if (index < currentIndex) return 'completed';
    if (index === currentIndex) return 'current';
    return 'pending';
  };

  return (
    <div className="phase-stepper">
      <div className="phase-header">
        <h3>📋 Fases</h3>
        <p className="phase-subtitle">Progreso de entrevista</p>
      </div>
      
      <div className="phase-timeline">
        {PHASES.map((phase, idx) => {
          const status = getStatus(idx);
          return (
            <div key={phase.id} className={`phase-item ${status}`}>
              <div className="phase-marker">
                {status === 'completed' ? '✓' : idx + 1}
              </div>
              <div className="phase-info">
                <div className="phase-id">{phase.id}</div>
                <div className="phase-name">{phase.name}</div>
                <div className="phase-desc">{phase.description}</div>
              </div>
            </div>
          );
        })}
      </div>

      <style>{`
        .phase-stepper {
          padding: 1rem;
          height: 100%;
          overflow-y: auto;
        }
        .phase-header {
          margin-bottom: 1.5rem;
          padding-bottom: 0.75rem;
          border-bottom: 1px solid #1e293b;
        }
        .phase-header h3 {
          font-size: 0.875rem;
          font-weight: 600;
          color: #e2e8f0;
          margin-bottom: 0.25rem;
        }
        .phase-subtitle {
          font-size: 0.7rem;
          color: #64748b;
        }
        .phase-timeline {
          display: flex;
          flex-direction: column;
          gap: 0.5rem;
        }
        .phase-item {
          display: flex;
          align-items: flex-start;
          gap: 0.75rem;
          padding: 0.5rem;
          border-radius: 8px;
          transition: background 0.2s;
        }
        .phase-item.current {
          background: rgba(59, 130, 246, 0.1);
        }
        .phase-item.completed .phase-marker {
          background: #22c55e;
          color: white;
        }
        .phase-item.current .phase-marker {
          background: #3b82f6;
          color: white;
          box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.3);
        }
        .phase-item.pending .phase-marker {
          background: #1e293b;
          color: #64748b;
        }
        .phase-marker {
          width: 24px;
          height: 24px;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 0.7rem;
          font-weight: 600;
          flex-shrink: 0;
        }
        .phase-info {
          flex: 1;
        }
        .phase-id {
          font-size: 0.6rem;
          color: #64748b;
          font-family: 'JetBrains Mono', monospace;
        }
        .phase-name {
          font-size: 0.75rem;
          font-weight: 500;
          color: #cbd5e1;
        }
        .phase-desc {
          font-size: 0.65rem;
          color: #64748b;
        }
        .phase-item.current .phase-name {
          color: #3b82f6;
        }
        .phase-item.completed .phase-name {
          color: #22c55e;
        }
      `}</style>
    </div>
  );
}