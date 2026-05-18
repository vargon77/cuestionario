// src/App.tsx
import { useState } from 'react';
import { SetupScreen } from './components/SetupScreen';
import { ChatScreen } from './components/ChatScreen';
import { ArchitectAgent } from './agents/architect';
import { SystemPattern } from './patterns';

function App() {
  const [isSetupComplete, setIsSetupComplete] = useState(false);
  const [agent, setAgent] = useState<ArchitectAgent | null>(null);
  const [pattern, setPattern] = useState<SystemPattern | null>(null);
  const [sessionId, setSessionId] = useState('');
  const [description, setDescription] = useState('');

  const handleSetupComplete = (
    selectedPattern: SystemPattern,
    sessionId: string,
    description: string,
    businessSize: string,
    seriousness: string
  ) => {
    // Crear el agente arquitecto
    const newAgent = new ArchitectAgent(selectedPattern, sessionId);
    
    // Almacenar contexto adicional si es necesario
    // (businessSize y seriousness se pueden usar para ajustar el tono del agente)
    
    setAgent(newAgent);
    setPattern(selectedPattern);
    setSessionId(sessionId);
    setDescription(description);
    setIsSetupComplete(true);
  };

  const handlePhaseChange = (phase: string) => {
    console.log(`Fase cambiada a: ${phase}`);
    // Aquí se puede actualizar cualquier estado global si es necesario
  };

  if (!isSetupComplete || !agent || !pattern) {
    return <SetupScreen onSetupComplete={handleSetupComplete} />;
  }

  return (
    <ChatScreen
      agent={agent}
      pattern={pattern}
      sessionId={sessionId}
      description={description}
      onPhaseChange={handlePhaseChange}
    />
  );
}

export default App;