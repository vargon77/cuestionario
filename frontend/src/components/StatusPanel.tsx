// src/components/StatusPanel.tsx
import { SystemPattern } from '../patterns';

interface StatusPanelProps {
  sessionId: string;
  currentPhase: string;
  pattern: SystemPattern;
  description: string;
}

export function StatusPanel({ sessionId, currentPhase, pattern, description }: StatusPanelProps) {
  const totalItems = pattern.items.length;
  const rbacStatus = pattern.rbac ? '✅ Requiere RBAC' : '❌ Sin RBAC';
  const backendMappings = pattern.backendMappings.join(', ') || 'No definido';

  return (
    <div className="status-panel-content">
      <div className="status-header">
        <h3>📊 Estado</h3>
      </div>

      <div className="status-section">
        <div className="status-item">
          <span className="status-label">🔑 Sesión:</span>
          <span className="status-value">{sessionId}</span>
        </div>
        <div className="status-item">
          <span className="status-label">📍 Fase:</span>
          <span className="status-value current-phase">{currentPhase}</span>
        </div>
        <div className="status-item">
          <span className="status-label">🎯 Sistema:</span>
          <span className="status-value">{pattern.display}</span>
        </div>
      </div>

      <div className="status-divider" />

      <div className="status-section">
        <div className="status-item">
          <span className="status-label">🔐 RBAC:</span>
          <span className="status-value">{rbacStatus}</span>
        </div>
        <div className="status-item">
          <span className="status-label">🔗 Backend:</span>
          <span className="status-value">{backendMappings}</span>
        </div>
        <div className="status-item">
          <span className="status-label">📦 Items totales:</span>
          <span className="status-value">{totalItems}</span>
        </div>
      </div>

      <div className="status-divider" />

      <div className="status-section">
        <div className="status-label">📝 Descripción:</div>
        <div className="status-description">{description}</div>
      </div>

      <div className="status-divider" />

      <div className="status-section">
        <div className="status-label">🚪 Gate:</div>
        <div className="status-badge pending">PENDIENTE</div>
      </div>

      <style>{`
        .status-panel-content {
          padding: 1rem;
          height: 100%;
          overflow-y: auto;
        }
        .status-header {
          margin-bottom: 1rem;
          padding-bottom: 0.5rem;
          border-bottom: 1px solid #1e293b;
        }
        .status-header h3 {
          font-size: 0.875rem;
          font-weight: 600;
          color: #e2e8f0;
        }
        .status-section {
          margin-bottom: 1rem;
        }
        .status-item {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 0.5rem;
          font-size: 0.75rem;
        }
        .status-label {
          color: #64748b;
        }
        .status-value {
          color: #cbd5e1;
          font-weight: 500;
        }
        .status-value.current-phase {
          color: #3b82f6;
          font-weight: 600;
        }
        .status-divider {
          height: 1px;
          background: #1e293b;
          margin: 0.75rem 0;
        }
        .status-description {
          font-size: 0.7rem;
          color: #94a3b8;
          line-height: 1.4;
          margin-top: 0.25rem;
        }
        .status-badge {
          display: inline-block;
          padding: 0.25rem 0.5rem;
          border-radius: 12px;
          font-size: 0.65rem;
          font-weight: 600;
        }
        .status-badge.pending {
          background: #854d0e;
          color: #fef08a;
        }
      `}</style>
    </div>
  );
}