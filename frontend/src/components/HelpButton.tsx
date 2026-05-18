// FRONTEND/src/components/HelpButton.tsx
// Botón de ayuda contextual por fase. Llama al LLM solo para explicar,
// nunca para decidir ni modificar datos del SEC.

import { useState } from 'react';
import { getContextualHelp, HelpRequest, HelpResponse } from '../services/helpService';

interface HelpButtonProps {
  fase: string;
  dimension: string;
  pregunta: string;
  sistema: string;       // nombre del sistema que está diseñando el usuario
}

type HelpState = 'idle' | 'loading' | 'open' | 'error';

export function HelpButton({ fase, dimension, pregunta, sistema }: HelpButtonProps) {
  const [state, setState] = useState<HelpState>('idle');
  const [helpData, setHelpData] = useState<HelpResponse | null>(null);
  const [followUpInput, setFollowUpInput] = useState('');
  const [followUpAnswer, setFollowUpAnswer] = useState('');

  const handleOpen = async () => {
    if (state === 'open') {
      setState('idle');
      return;
    }

    setState('loading');
    try {
      const req: HelpRequest = { sistema, fase, pregunta, dimension };
      const data = await getContextualHelp(req);
      setHelpData(data);
      setState('open');
    } catch {
      setState('error');
      setTimeout(() => setState('idle'), 3000);
    }
  };

  const handleFollowUp = async () => {
    if (!followUpInput.trim()) return;
    // Follow-up es solo informativo, no modifica nada del flujo principal
    setFollowUpAnswer('Procesando...');
    try {
      const req: HelpRequest = {
        sistema,
        fase,
        pregunta: `${pregunta}\n\nPregunta de seguimiento: ${followUpInput}`,
        dimension,
      };
      const data = await getContextualHelp(req);
      setFollowUpAnswer(data.recomendacion);
      setFollowUpInput('');
    } catch {
      setFollowUpAnswer('Error al procesar. Intenta de nuevo.');
    }
  };

  return (
    <div className="help-container">
      <button
        className={`help-btn ${state}`}
        onClick={handleOpen}
        title={`Ayuda con ${dimension}`}
        disabled={state === 'loading'}
      >
        {state === 'loading' ? (
          <span className="help-spinner" />
        ) : state === 'open' ? (
          '✕'
        ) : (
          '?'
        )}
      </button>

      {state === 'error' && (
        <span className="help-error-toast">Error al cargar ayuda</span>
      )}

      {state === 'open' && helpData && (
        <div className="help-drawer">
          <div className="help-drawer-header">
            <span className="help-drawer-badge">{dimension}</span>
            <span className="help-drawer-fase">{fase}</span>
          </div>

          <section className="help-section">
            <h4 className="help-section-title">¿Por qué importa esto?</h4>
            <p className="help-explicacion">{helpData.explicacion}</p>
          </section>

          {helpData.ejemplos_alta.length > 0 && (
            <section className="help-section">
              <h4 className="help-section-title">
                <span className="dot alta" />
                Ejemplos clave para {sistema}
              </h4>
              <ul className="help-examples">
                {helpData.ejemplos_alta.map((ej, i) => (
                  <li key={i} className="example-item alta">{ej}</li>
                ))}
              </ul>
            </section>
          )}

          {helpData.ejemplos_media.length > 0 && (
            <section className="help-section">
              <h4 className="help-section-title">
                <span className="dot media" />
                Ejemplos adicionales
              </h4>
              <ul className="help-examples">
                {helpData.ejemplos_media.map((ej, i) => (
                  <li key={i} className="example-item media">{ej}</li>
                ))}
              </ul>
            </section>
          )}

          <section className="help-section recomendacion">
            <h4 className="help-section-title">Recomendación</h4>
            <p className="help-rec-text">{helpData.recomendacion}</p>
          </section>

          {helpData.preguntas_seguimiento && helpData.preguntas_seguimiento.length > 0 && (
            <section className="help-section">
              <h4 className="help-section-title">Para refinar la recomendación</h4>
              {helpData.preguntas_seguimiento.map((pq, i) => (
                <p key={i} className="follow-up-question">→ {pq}</p>
              ))}
              <div className="follow-up-input-row">
                <input
                  className="follow-up-input"
                  placeholder="Tu respuesta..."
                  value={followUpInput}
                  onChange={e => setFollowUpInput(e.target.value)}
                  onKeyDown={e => e.key === 'Enter' && handleFollowUp()}
                />
                <button className="follow-up-send" onClick={handleFollowUp}>→</button>
              </div>
              {followUpAnswer && (
                <p className="follow-up-answer">{followUpAnswer}</p>
              )}
            </section>
          )}
        </div>
      )}

      <style>{`
        .help-container {
          position: relative;
          display: inline-flex;
          align-items: center;
        }

        .help-btn {
          width: 22px;
          height: 22px;
          border-radius: 50%;
          border: 1.5px solid #475569;
          background: #1e293b;
          color: #94a3b8;
          font-size: 0.7rem;
          font-weight: 700;
          cursor: pointer;
          display: inline-flex;
          align-items: center;
          justify-content: center;
          transition: all 0.15s;
          flex-shrink: 0;
          line-height: 1;
        }
        .help-btn:hover:not(:disabled) {
          border-color: #f59e0b;
          color: #f59e0b;
          background: rgba(245, 158, 11, 0.1);
        }
        .help-btn.open {
          border-color: #f59e0b;
          background: rgba(245, 158, 11, 0.15);
          color: #f59e0b;
        }
        .help-btn.loading {
          border-color: #3b82f6;
          opacity: 0.7;
          cursor: wait;
        }
        .help-btn:disabled {
          cursor: wait;
        }

        .help-spinner {
          width: 10px;
          height: 10px;
          border: 1.5px solid #3b82f6;
          border-top-color: transparent;
          border-radius: 50%;
          animation: spin 0.7s linear infinite;
          display: block;
        }
        @keyframes spin {
          to { transform: rotate(360deg); }
        }

        .help-error-toast {
          position: absolute;
          left: 28px;
          top: 50%;
          transform: translateY(-50%);
          background: #7f1d1d;
          color: #fecaca;
          font-size: 0.7rem;
          padding: 3px 8px;
          border-radius: 6px;
          white-space: nowrap;
          z-index: 200;
        }

        .help-drawer {
          position: absolute;
          left: 28px;
          top: 0;
          width: 320px;
          background: #0f172a;
          border: 1px solid #334155;
          border-radius: 12px;
          padding: 1rem;
          z-index: 200;
          box-shadow: 0 8px 32px rgba(0,0,0,0.5);
          animation: drawerIn 0.18s ease;
          max-height: 70vh;
          overflow-y: auto;
        }
        @keyframes drawerIn {
          from { opacity: 0; transform: translateX(-6px); }
          to   { opacity: 1; transform: translateX(0); }
        }

        .help-drawer-header {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          margin-bottom: 0.75rem;
          padding-bottom: 0.5rem;
          border-bottom: 1px solid #1e293b;
        }
        .help-drawer-badge {
          background: rgba(245, 158, 11, 0.15);
          color: #f59e0b;
          font-size: 0.65rem;
          font-weight: 700;
          padding: 2px 7px;
          border-radius: 10px;
          text-transform: uppercase;
          letter-spacing: 0.5px;
        }
        .help-drawer-fase {
          color: #475569;
          font-size: 0.65rem;
          font-weight: 500;
        }

        .help-section {
          margin-bottom: 0.875rem;
        }
        .help-section-title {
          font-size: 0.7rem;
          font-weight: 700;
          text-transform: uppercase;
          letter-spacing: 0.6px;
          color: #64748b;
          margin-bottom: 0.4rem;
          display: flex;
          align-items: center;
          gap: 0.35rem;
        }
        .dot {
          width: 6px;
          height: 6px;
          border-radius: 50%;
          flex-shrink: 0;
        }
        .dot.alta  { background: #ef4444; }
        .dot.media { background: #f59e0b; }

        .help-explicacion {
          font-size: 0.8rem;
          color: #cbd5e1;
          line-height: 1.5;
        }

        .help-examples {
          list-style: none;
          padding: 0;
          margin: 0;
          display: flex;
          flex-direction: column;
          gap: 0.3rem;
        }
        .example-item {
          font-size: 0.75rem;
          line-height: 1.4;
          padding: 0.3rem 0.6rem;
          border-radius: 6px;
          border-left: 2px solid;
        }
        .example-item.alta {
          color: #fca5a5;
          border-color: #ef4444;
          background: rgba(239,68,68,0.06);
        }
        .example-item.media {
          color: #fde68a;
          border-color: #f59e0b;
          background: rgba(245,158,11,0.06);
        }

        .help-section.recomendacion {
          background: rgba(59,130,246,0.06);
          border: 1px solid rgba(59,130,246,0.2);
          border-radius: 8px;
          padding: 0.6rem 0.75rem;
        }
        .help-rec-text {
          font-size: 0.8rem;
          color: #93c5fd;
          line-height: 1.5;
        }

        .follow-up-question {
          font-size: 0.75rem;
          color: #94a3b8;
          margin-bottom: 0.4rem;
          font-style: italic;
        }
        .follow-up-input-row {
          display: flex;
          gap: 0.4rem;
          margin-top: 0.5rem;
        }
        .follow-up-input {
          flex: 1;
          background: #1e293b;
          border: 1px solid #334155;
          border-radius: 6px;
          padding: 0.35rem 0.6rem;
          color: #e2e8f0;
          font-size: 0.75rem;
        }
        .follow-up-input:focus {
          outline: none;
          border-color: #3b82f6;
        }
        .follow-up-send {
          background: #3b82f6;
          border: none;
          border-radius: 6px;
          width: 28px;
          color: white;
          cursor: pointer;
          font-size: 0.8rem;
        }
        .follow-up-answer {
          margin-top: 0.5rem;
          font-size: 0.75rem;
          color: #a5b4fc;
          line-height: 1.4;
          padding: 0.4rem 0.6rem;
          background: rgba(99,102,241,0.08);
          border-radius: 6px;
        }
      `}</style>
    </div>
  );
}