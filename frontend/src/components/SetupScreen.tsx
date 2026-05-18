// src/components/SetupScreen.tsx
import { useState } from 'react';
import { PATTERNS, SystemPattern, getAllPatterns } from '../patterns';
import { createSession } from '../api';

interface SetupScreenProps {
  onSetupComplete: (
    pattern: SystemPattern,
    sessionId: string,
    description: string,
    businessSize: string,
    seriousness: string
  ) => void;
}

const BUSINESS_SIZES = [
  { id: 'startup',   label: '🚀 Startup',    description: 'Equipo pequeño, buscando validar' },
  { id: 'pyme',      label: '🏢 PyME',        description: 'Negocio establecido, crecimiento' },
  { id: 'corporate', label: '🏛️ Corporativo', description: 'Múltiples áreas, procesos definidos' },
  { id: 'enterprise',label: '🌍 Enterprise',  description: 'Alta escala, requisitos críticos' },
];

const SERIOUSNESS_LEVELS = [
  { id: 'prototype', label: '🧪 Prototipo', description: 'Validar idea, cambios frecuentes' },
  { id: 'mvp',       label: '🎯 MVP',       description: 'Producto mínimo viable para producción' },
  { id: 'production',label: '⚙️ Producción', description: 'Sistema listo para usuarios reales' },
  { id: 'enterprise',label: '🏆 Enterprise', description: 'Alta disponibilidad, SLA estrictos' },
];

const PATTERN_ICONS: Record<string, string> = {
  CRM: '📊', ERP: '🏭', POS: '🛒', ECOMMERCE: '🛍️',
  MANUFACTURA: '⚙️', LOGISTICA: '🚚', HOSPITALARIO: '🏥',
  RH: '👥', IA_MULTIAGENTE: '🤖', IOT: '📡',
  FINTECH: '💰', SAAS: '☁️', CUSTOM: '🔧',
};

export function SetupScreen({ onSetupComplete }: SetupScreenProps) {
  const patterns = getAllPatterns().filter(p => p.id !== 'CUSTOM');
  const [selectedPattern, setSelectedPattern] = useState<SystemPattern | null>(null);
  const [description, setDescription] = useState('');
  const [businessSize, setBusinessSize] = useState('startup');
  const [seriousness, setSeriousness] = useState('mvp');
  const [sessionId, setSessionId] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const generateSessionId = (patternId: string) => {
    const suffix = Math.random().toString(36).substring(2, 8);
    return `${patternId.toLowerCase()}-${suffix}`;
  };

  const handlePatternSelect = (pattern: SystemPattern) => {
    setSelectedPattern(pattern);
    setSessionId(generateSessionId(pattern.id));
    setError('');
  };

  const handleSubmit = async () => {
    if (!selectedPattern) {
      alert('Por favor selecciona un tipo de sistema');
      return;
    }
    if (!description.trim()) {
      alert('Por favor describe brevemente el proyecto');
      return;
    }

    setLoading(true);
    setError('');

    try {
      // Crear la sesión en el backend antes de continuar
      await createSession(sessionId);
      onSetupComplete(selectedPattern, sessionId, description, businessSize, seriousness);
    } catch (err) {
      setError('No se pudo conectar con el backend. Verifica que el servidor esté corriendo.');
      console.error('createSession error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="setup-screen">
      <div className="setup-container">
        <div className="setup-header">
          <h1>🏗️ Entrevistador V6</h1>
          <p>Diseño Arquitectónico de Sistemas</p>
        </div>

        <div className="setup-section">
          <label>Selecciona el tipo de sistema</label>
          <div className="pattern-grid">
            {patterns.map(pattern => (
              <button
                key={pattern.id}
                className={`pattern-card ${selectedPattern?.id === pattern.id ? 'selected' : ''}`}
                onClick={() => handlePatternSelect(pattern)}
              >
                <span className="pattern-icon">{PATTERN_ICONS[pattern.id] || '📦'}</span>
                <span className="pattern-name">{pattern.display}</span>
                <span className="pattern-desc">{pattern.description.substring(0, 40)}...</span>
              </button>
            ))}
          </div>
        </div>

        <div className="setup-section">
          <label>Describe brevemente el proyecto</label>
          <textarea
            className="setup-textarea"
            placeholder="Ej: CRM para equipo de ventas de empresa inmobiliaria con 3 sucursales en México"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            rows={3}
          />
        </div>

        <div className="setup-row">
          <div className="setup-section half">
            <label>Tamaño del negocio</label>
            <select
              className="setup-select"
              value={businessSize}
              onChange={(e) => setBusinessSize(e.target.value)}
            >
              {BUSINESS_SIZES.map(size => (
                <option key={size.id} value={size.id}>
                  {size.label} - {size.description}
                </option>
              ))}
            </select>
          </div>

          <div className="setup-section half">
            <label>Seriedad del proyecto</label>
            <select
              className="setup-select"
              value={seriousness}
              onChange={(e) => setSeriousness(e.target.value)}
            >
              {SERIOUSNESS_LEVELS.map(level => (
                <option key={level.id} value={level.id}>
                  {level.label} - {level.description}
                </option>
              ))}
            </select>
          </div>
        </div>

        <div className="setup-section">
          <label>ID de sesión (auto-generado, editable)</label>
          <input
            type="text"
            className="setup-input"
            value={sessionId}
            onChange={(e) => setSessionId(e.target.value)}
            placeholder="crm-inmobiliaria-001"
          />
        </div>

        {error && (
          <div className="setup-error">{error}</div>
        )}

        <button
          className="setup-submit"
          onClick={handleSubmit}
          disabled={!selectedPattern || !description.trim() || loading}
        >
          {loading ? '⏳ Conectando...' : '🚀 Iniciar Entrevista'}
        </button>
      </div>

      <style>{`
        .setup-screen {
          min-height: 100vh;
          background: linear-gradient(135deg, #0f1117 0%, #1a1f2e 100%);
          display: flex;
          align-items: center;
          justify-content: center;
          padding: 2rem;
        }
        .setup-container {
          max-width: 900px;
          width: 100%;
          background: #1a1f2e;
          border-radius: 24px;
          padding: 2rem;
          box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
          border: 1px solid #334155;
        }
        .setup-header {
          text-align: center;
          margin-bottom: 2rem;
        }
        .setup-header h1 {
          font-family: 'DM Serif Display', serif;
          font-size: 2rem;
          color: #f1f5f9;
          margin-bottom: 0.5rem;
        }
        .setup-header p { color: #94a3b8; }
        .setup-section { margin-bottom: 1.5rem; }
        .setup-section label {
          display: block;
          color: #cbd5e1;
          font-weight: 500;
          margin-bottom: 0.5rem;
          font-size: 0.875rem;
        }
        .pattern-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
          gap: 0.75rem;
        }
        .pattern-card {
          background: #0f172a;
          border: 1px solid #334155;
          border-radius: 12px;
          padding: 0.75rem;
          text-align: center;
          cursor: pointer;
          transition: all 0.2s;
        }
        .pattern-card:hover { border-color: #3b82f6; transform: translateY(-2px); }
        .pattern-card.selected {
          border-color: #3b82f6;
          background: #1e293b;
          box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.3);
        }
        .pattern-icon { font-size: 1.5rem; display: block; margin-bottom: 0.25rem; }
        .pattern-name { font-size: 0.75rem; font-weight: 600; color: #e2e8f0; }
        .pattern-desc { font-size: 0.65rem; color: #94a3b8; display: block; margin-top: 0.25rem; }
        .setup-textarea, .setup-input, .setup-select {
          width: 100%;
          background: #0f172a;
          border: 1px solid #334155;
          border-radius: 12px;
          padding: 0.75rem;
          color: #f1f5f9;
          font-size: 0.875rem;
          font-family: inherit;
        }
        .setup-textarea:focus, .setup-input:focus, .setup-select:focus {
          outline: none;
          border-color: #3b82f6;
        }
        .setup-row { display: flex; gap: 1rem; }
        .setup-section.half { flex: 1; }
        .setup-error {
          background: rgba(239, 68, 68, 0.1);
          border: 1px solid #ef4444;
          border-radius: 8px;
          padding: 0.75rem;
          color: #fca5a5;
          font-size: 0.875rem;
          margin-bottom: 1rem;
        }
        .setup-submit {
          width: 100%;
          background: linear-gradient(135deg, #3b82f6, #2563eb);
          border: none;
          border-radius: 12px;
          padding: 1rem;
          color: white;
          font-weight: 600;
          font-size: 1rem;
          cursor: pointer;
          transition: all 0.2s;
          margin-top: 1rem;
        }
        .setup-submit:hover:not(:disabled) {
          transform: translateY(-2px);
          box-shadow: 0 10px 20px -5px rgba(59, 130, 246, 0.4);
        }
        .setup-submit:disabled { opacity: 0.5; cursor: not-allowed; }
      `}</style>
    </div>
  );
}