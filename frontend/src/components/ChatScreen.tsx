// src/components/ChatScreen.tsx
import { useState, useRef, useEffect } from 'react';
import { ArchitectAgent, ArchitectMessage, Proposal } from '../agents/architect';
import { SystemPattern } from '../patterns';
import { ProposalChecklist } from './ProposalChecklist';
import { PhaseStepper } from './PhaseStepper';
import { StatusPanel } from './StatusPanel';

interface ChatScreenProps {
  agent: ArchitectAgent;
  pattern: SystemPattern;
  sessionId: string;
  description: string;
  onPhaseChange: (phase: string) => void;
}

export function ChatScreen({ agent, pattern, sessionId, description, onPhaseChange }: ChatScreenProps) {
  const [messages, setMessages] = useState<ArchitectMessage[]>(agent.getMessages());
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [currentPhase, setCurrentPhase] = useState(agent.getPhase());
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [rightPanelOpen, setRightPanelOpen] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };
  const handleDeferProposal = (proposal: Proposal) => {
    agent.deferProposal(proposal.item.name);
    const updatedMessages = agent.getMessages();
    setMessages(updatedMessages);
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Actualizar pre-llenado cuando cambian las propuestas aceptadas
  useEffect(() => {
    const prefilled = agent.getPrefilledText();
    if (prefilled && !inputValue) {
      setInputValue(prefilled);
      // Auto-ajustar altura del textarea
      if (textareaRef.current) {
        textareaRef.current.style.height = 'auto';
        textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
      }
    }
  }, [messages]);

  const handleSendMessage = async () => {
    if (!inputValue.trim() || isLoading) return;

    const userMessage = inputValue.trim();
    setInputValue('');
    setIsLoading(true);

    // Mostrar mensaje del usuario inmediatamente
    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);

    try {
      const response = await agent.processUserResponse(userMessage);
      setMessages(prev => [...prev, response]);
      setCurrentPhase(agent.getPhase());
      onPhaseChange(agent.getPhase());
    } catch (error) {
      console.error('Error:', error);
      setMessages(prev => [...prev, {
        role: 'architect',
        content: 'Lo siento, hubo un error al procesar tu respuesta. ¿Podrías intentarlo de nuevo?',
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleAcceptProposal = (proposal: Proposal, userValues?: Record<string, string>) => {
    agent.acceptProposal(proposal.item.name, userValues);
    // Actualizar mensajes para reflejar el cambio de estado
    const updatedMessages = agent.getMessages();
    setMessages(updatedMessages);
    
    // Actualizar pre-llenado
    const prefilled = agent.getPrefilledText();
    if (prefilled) {
      setInputValue(prefilled);
    }
  };

  const handleRejectProposal = (proposal: Proposal) => {
    agent.rejectProposal(proposal.item.name);
    const updatedMessages = agent.getMessages();
    setMessages(updatedMessages);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  // Extraer propuestas del último mensaje del arquitecto
  const lastArchitectMessage = [...messages].reverse().find(m => m.role === 'architect');
  const currentProposals = lastArchitectMessage?.proposals || [];

  return (
    <div className="chat-screen">
      {/* Botón toggle sidebar izquierdo */}
      <button className="sidebar-toggle left" onClick={() => setSidebarOpen(!sidebarOpen)}>
        {sidebarOpen ? '◀' : '▶'} FASES
      </button>

      {/* Botón toggle panel derecho */}
      <button className="sidebar-toggle right" onClick={() => setRightPanelOpen(!rightPanelOpen)}>
        {rightPanelOpen ? '▶' : '◀'} ESTADO
      </button>

      {/* Sidebar izquierdo - PhaseStepper */}
      <div className={`phase-sidebar ${sidebarOpen ? 'open' : 'closed'}`}>
        <PhaseStepper currentPhase={currentPhase} />
      </div>

      {/* Panel derecho - StatusPanel */}
      <div className={`status-panel ${rightPanelOpen ? 'open' : 'closed'}`}>
        <StatusPanel
          sessionId={sessionId}
          currentPhase={currentPhase}
          pattern={pattern}
          description={description}
        />
      </div>

      {/* Área principal de chat */}
      <div className="chat-main">
        <div className="chat-header">
          <h2>🤖 Arquitecto de {pattern.display}</h2>
          <div className="chat-header-badge">{currentPhase}</div>
        </div>

        <div className="messages-container">
          {messages.map((msg, idx) => (
            <div key={idx} className={`message ${msg.role}`}>
              <div className="message-avatar">
                {msg.role === 'architect' ? '🤖' : '👤'}
              </div>
              <div className="message-content">
                <div className="message-text">{msg.content}</div>
                
                {/* Propuestas inline - solo en mensajes del arquitecto que las tengan */}
                {msg.role === 'architect' && msg.proposals && msg.proposals.length > 0 && (
                  <ProposalChecklist
                    proposals={msg.proposals}
                    onAccept={handleAcceptProposal}
                    onReject={handleRejectProposal}
                    onDefer={handleDeferProposal}
                    phase={currentPhase}
                  />
                )}
              </div>
            </div>
          ))}
          
          {isLoading && (
            <div className="message architect">
              <div className="message-avatar">🤖</div>
              <div className="message-content">
                <div className="typing-indicator">
                  <span></span><span></span><span></span>
                </div>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        <div className="input-container">
          <textarea
            ref={textareaRef}
            className="chat-input"
            value={inputValue}
            onChange={(e) => {
              setInputValue(e.target.value);
              e.target.style.height = 'auto';
              e.target.style.height = `${e.target.scrollHeight}px`;
            }}
            onKeyDown={handleKeyDown}
            placeholder="Escribe tu respuesta aquí..."
            rows={1}
            disabled={isLoading}
          />
          <button
            className="send-button"
            onClick={handleSendMessage}
            disabled={isLoading || !inputValue.trim()}
          >
            {isLoading ? '⏳' : '📤'}
          </button>
        </div>
      </div>

      <style>{`
        .chat-screen {
          display: flex;
          height: 100vh;
          background: #0f1117;
          position: relative;
        }
        .sidebar-toggle {
          position: fixed;
          top: 50%;
          transform: translateY(-50%);
          background: #1e293b;
          border: 1px solid #334155;
          border-radius: 8px;
          padding: 8px 6px;
          cursor: pointer;
          z-index: 100;
          font-size: 12px;
          color: #94a3b8;
          transition: all 0.2s;
        }
        .sidebar-toggle.left {
          left: 0;
          border-left: none;
          border-radius: 0 8px 8px 0;
        }
        .sidebar-toggle.right {
          right: 0;
          border-right: none;
          border-radius: 8px 0 0 8px;
        }
        .sidebar-toggle:hover {
          background: #334155;
          color: #e2e8f0;
        }
        .phase-sidebar {
          position: fixed;
          left: 0;
          top: 0;
          height: 100vh;
          background: #070b12;
          border-right: 1px solid #1e293b;
          transition: transform 0.3s ease;
          z-index: 90;
          overflow-y: auto;
        }
        .phase-sidebar.open {
          transform: translateX(0);
          width: 280px;
        }
        .phase-sidebar.closed {
          transform: translateX(-100%);
          width: 0;
        }
        .status-panel {
          position: fixed;
          right: 0;
          top: 0;
          height: 100vh;
          background: #070b12;
          border-left: 1px solid #1e293b;
          transition: transform 0.3s ease;
          z-index: 90;
          overflow-y: auto;
        }
        .status-panel.open {
          transform: translateX(0);
          width: 260px;
        }
        .status-panel.closed {
          transform: translateX(100%);
          width: 0;
        }
        .chat-main {
          flex: 1;
          display: flex;
          flex-direction: column;
          margin: 0 0 0 0;
          transition: margin 0.3s ease;
        }
        .phase-sidebar.open ~ .chat-main {
          margin-left: 280px;
        }
        .status-panel.open ~ .chat-main {
          margin-right: 260px;
        }
        .chat-header {
          background: #1a1f2e;
          border-bottom: 1px solid #334155;
          padding: 1rem 1.5rem;
          display: flex;
          justify-content: space-between;
          align-items: center;
        }
        .chat-header h2 {
          font-family: 'DM Serif Display', serif;
          font-size: 1.25rem;
          color: #f1f5f9;
        }
        .chat-header-badge {
          background: #3b82f6;
          padding: 0.25rem 0.75rem;
          border-radius: 20px;
          font-size: 0.75rem;
          font-weight: 600;
          color: white;
        }
        .messages-container {
          flex: 1;
          overflow-y: auto;
          padding: 1.5rem;
          display: flex;
          flex-direction: column;
          gap: 1rem;
        }
        .message {
          display: flex;
          gap: 0.75rem;
          max-width: 80%;
          animation: fadeIn 0.3s ease;
        }
        .message.architect {
          align-self: flex-start;
        }
        .message.user {
          align-self: flex-end;
          flex-direction: row-reverse;
        }
        .message-avatar {
          width: 36px;
          height: 36px;
          background: #1e293b;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 1.25rem;
          flex-shrink: 0;
        }
        .message.user .message-avatar {
          background: #3b82f6;
        }
        .message-content {
          flex: 1;
        }
        .message-text {
          background: #1e293b;
          padding: 0.75rem 1rem;
          border-radius: 18px;
          color: #e2e8f0;
          font-size: 0.9375rem;
          line-height: 1.5;
          white-space: pre-wrap;
        }
        .message.user .message-text {
          background: #3b82f6;
        }
        .typing-indicator {
          display: flex;
          gap: 4px;
          padding: 0.75rem 1rem;
          background: #1e293b;
          border-radius: 18px;
          width: fit-content;
        }
        .typing-indicator span {
          width: 8px;
          height: 8px;
          background: #94a3b8;
          border-radius: 50%;
          animation: typing 1.4s infinite;
        }
        .typing-indicator span:nth-child(2) { animation-delay: 0.2s; }
        .typing-indicator span:nth-child(3) { animation-delay: 0.4s; }
        @keyframes typing {
          0%, 60%, 100% { transform: translateY(0); opacity: 0.4; }
          30% { transform: translateY(-8px); opacity: 1; }
        }
        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(10px); }
          to { opacity: 1; transform: translateY(0); }
        }
        .input-container {
          background: #1a1f2e;
          border-top: 1px solid #334155;
          padding: 1rem 1.5rem;
          display: flex;
          gap: 0.75rem;
          align-items: flex-end;
        }
        .chat-input {
          flex: 1;
          background: #0f172a;
          border: 1px solid #334155;
          border-radius: 24px;
          padding: 0.75rem 1rem;
          color: #f1f5f9;
          font-size: 0.9375rem;
          font-family: inherit;
          resize: none;
          max-height: 120px;
          transition: border-color 0.2s;
        }
        .chat-input:focus {
          outline: none;
          border-color: #3b82f6;
        }
        .chat-input:disabled {
          opacity: 0.5;
        }
        .send-button {
          background: #3b82f6;
          border: none;
          border-radius: 50%;
          width: 40px;
          height: 40px;
          display: flex;
          align-items: center;
          justify-content: center;
          cursor: pointer;
          font-size: 1.25rem;
          transition: all 0.2s;
        }
        .send-button:hover:not(:disabled) {
          background: #2563eb;
          transform: scale(1.05);
        }
        .send-button:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }
      `}</style>
    </div>
  );
}