import React, { useState, useEffect, Suspense } from 'react';
import './index.css';
import { createRoot } from 'react-dom/client';
import { 
  Terminal, Activity, Layers, MessageSquare, 
  Code, FileText, Cpu, Search, SlidersHorizontal, FileSearch, Wifi, Home
} from 'lucide-react';

import { InternalAuditDashboard } from './components/DashboardPage';
import { CodeEditor } from './components/CodeEditorPage';
import ChatPage from './components/ChatPage';
import { StackBuilder } from './components/StackBuilderPage';
import { LMSetup } from './components/LMSetupPage';
import { HomeDashboard } from './components/HomePage';
import { Placeholder, NavIcon } from './components/ui';
import { DevTools } from './components/DevToolsPage';
import { DocReview } from './components/DocReviewPage';
import { DocumentEditor } from './components/DocumentEditorPage';
import { CodeReview } from './components/CodeReviewPage';

/**
 * Aletheia Unified Interface (Prototype)
 * --------------------------------------
 * A React-based "Mission Control" for the ACP_V1 Backend.
 */
const AletheiaApp = () => {
  const [activeTab, setActiveTab] = useState('home');
  const [systemStatus, setSystemStatus] = useState('STABLE');
  const [logs, setLogs] = useState([]);
  
  useEffect(() => {
    const initialLogs = [
      `[${new Date().toISOString().split('T')[1].split('.')[0]}] [INFO] System boot complete. Aletheia v1.0.0 online.`,
      `[${new Date().toISOString().split('T')[1].split('.')[0]}] [REASONING] Evaluating workspace for stack 'Payment Gateway V2'.`,
      `[${new Date().toISOString().split('T')[1].split('.')[0]}] [INFO] Connected to Local Language Model API.`,
      `[${new Date().toISOString().split('T')[1].split('.')[0]}] [ERROR] High memory usage detected in 'simulation_hpc.py'.`,
      `[${new Date().toISOString().split('T')[1].split('.')[0]}] [INFO] Telemetry stream active.`
    ];
    setLogs(initialLogs);

    const interval = setInterval(() => {
      const logType = ['INFO', 'REASONING', 'ERROR'][Math.floor(Math.random() * 3)];
      const newLog = `[${new Date().toISOString().split('T')[1].split('.')[0]}] [${logType}] AUDIT: Checked integrity of module ${Math.floor(Math.random() * 999)}`;
      setLogs(prev => [newLog, ...prev].slice(0, 50));
    }, 2500);
    return () => clearInterval(interval);
  }, []);

  const renderContent = () => {
        switch(activeTab) {
          case 'home': return <HomeDashboard logs={logs} />;
          case 'audit': return <InternalAuditDashboard logs={logs} />;
          case 'editor': return <CodeEditor />;
          case 'code_review': return <CodeReview />;
          case 'docs': return <DocumentEditor />;
          case 'doc_review': return <DocReview />;
          case 'chat': return <ChatPage />;
          case 'factory': return <StackBuilder />;
          case 'lm_setup': return <LMSetup />;
          case 'dev_tools': return <DevTools />;
          default: return <HomeDashboard logs={logs} />;
        }
  }

  return (
    <div className="flex h-screen bg-gray-900 text-gray-100 font-sans overflow-hidden">
      {/* SIDEBAR NAVIGATION */}
      <nav className="w-20 flex flex-col items-center py-6 bg-gray-950 border-r border-gray-800 z-20 shrink-0">
        <div className="mb-8 p-2 bg-blue-600 rounded-lg shadow-lg shadow-blue-900/50">
          <Cpu size={28} className="text-white" />
        </div>
        
        <div className="px-5 pt-4 pb-2 text-xs uppercase text-gray-500 tracking-wider w-full text-center">Dev Core</div>
        <NavIcon icon={Code} id="editor" active={activeTab} set={setActiveTab} label="Code Editor" />
        <NavIcon icon={Search} id="code_review" active={activeTab} set={setActiveTab} label="Code Review" />
        <NavIcon icon={FileText} id="docs" active={activeTab} set={setActiveTab} label="Doc Editor" />
        <NavIcon icon={FileSearch} id="doc_review" active={activeTab} set={setActiveTab} label="Doc Review" />
        
        <div className="px-5 pt-4 pb-2 text-xs uppercase text-gray-500 tracking-wider w-full text-center">Aletheia</div>
        <NavIcon icon={MessageSquare} id="chat" active={activeTab} set={setActiveTab} label="Chat Interface" />

        <div className="px-5 pt-4 pb-2 text-xs uppercase text-gray-500 tracking-wider w-full text-center">Systems</div>
        <NavIcon icon={Home} id="home" active={activeTab} set={setActiveTab} label="Home" />
        <NavIcon icon={Activity} id="audit" active={activeTab} set={setActiveTab} label="Internal Audit" />
        <NavIcon icon={Layers} id="factory" active={activeTab} set={setActiveTab} label="Code Factory" />
        <NavIcon icon={SlidersHorizontal} id="lm_setup" active={activeTab} set={setActiveTab} label="LM Setup" />
        <NavIcon icon={Terminal} id="dev_tools" active={activeTab} set={setActiveTab} label="Dev Tools" />
      </nav>

      {/* MAIN CONTENT AREA */}
      <main className="flex-1 flex flex-col relative">
        <header className="h-16 bg-gray-900 border-b border-gray-800 flex items-center justify-between px-6 shrink-0">
          <div className="flex items-center gap-4">
            <h1 className="text-xl font-bold tracking-tight text-white">
              ALETHEIA <span className="text-blue-500 text-sm font-mono">ACP_V1</span>
            </h1>
          </div>
          <div className="flex items-center gap-6">
            <span className={`px-2 py-0.5 rounded text-xs font-mono border flex items-center gap-2 ${
              systemStatus === 'STABLE' ? 'bg-green-900/30 border-green-700 text-green-400' : 'bg-red-900/30 border-red-700 text-red-400'
            }`}>
              <div className={`w-1.5 h-1.5 rounded-full ${systemStatus === 'STABLE' ? 'bg-green-500' : 'bg-red-500'}`}></div>
              {systemStatus}
            </span>
            <div className="w-px h-6 bg-gray-700" />
            <div className="flex items-center gap-2 text-sm text-gray-400 font-mono">
              <Wifi size={14} className="text-green-500" />
              <span>API: Connected (Local)</span>
            </div>
            <div className="h-8 w-8 bg-gradient-to-tr from-blue-500 to-purple-600 rounded-full border border-gray-600" />
          </div>
        </header>
        <div className="flex-1 overflow-auto p-6 bg-[#0B0F19]">
            {renderContent()}
        </div>
      </main>
    </div>
  );
};


const container = document.getElementById('root');
const root = createRoot(container);
root.render(
  <Suspense fallback={
    <div className="w-screen h-screen flex items-center justify-center bg-gray-900 text-gray-500">
      <Cpu size={48} className="animate-spin" />
    </div>
  }>
    <AletheiaApp />
  </Suspense>
);

export default AletheiaApp;