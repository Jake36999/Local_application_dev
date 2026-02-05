import React, { useState, useEffect, useRef } from 'react';
import {
  Play,
  Folder,
  Activity,
  Terminal,
  Settings,
  FileText,
  CheckCircle,
  AlertCircle,
  Clock,
  ChevronDown,
  ChevronRight,
  Search,
  Database,
  Trash2,
  RefreshCw,
} from 'lucide-react';

export default function App() {
  const [activeTab, setActiveTab] = useState('workflows');
  const [scanPath, setScanPath] = useState('');
  const [isScanning, setIsScanning] = useState(false);
  const [progress, setProgress] = useState(0);
  const [currentStep, setCurrentStep] = useState('Idle');

  // Data State
  const [completedScans, setCompletedScans] = useState([
    { id: 1, path: '/usr/local/docs/project_alpha', date: '2023-10-25 14:30', status: 'success', bundleSize: '4.2MB' },
    { id: 2, path: '/home/user/workspace/legacy_code', date: '2023-10-24 09:15', status: 'warning', bundleSize: '12.8MB' },
  ]);

  // Bus / Logging State
  const [busLogs, setBusLogs] = useState([]);
  const logsEndRef = useRef(null);

  // Auto-scroll logs
  useEffect(() => {
    if (activeTab === 'debug' && logsEndRef.current) {
      logsEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [busLogs, activeTab]);

  // --- BUS SYSTEM SIMULATION ---
  const emitBusEvent = (source, type, message, payload = null) => {
    const newEvent = {
      id: Date.now(),
      timestamp: new Date().toISOString(),
      source,
      type,
      message,
      payload,
    };
    setBusLogs((prev) => [...prev, newEvent]);
    console.log('[BUS]', newEvent);
  };

  // --- HANDLERS ---

  const handleStartScan = () => {
    if (!scanPath) {
      emitBusEvent('UI', 'ERROR', 'Validation Failed', { field: 'path', error: 'Empty path' });
      alert('Please enter a valid file path.');
      return;
    }

    if (isScanning) return;

    setIsScanning(true);
    setProgress(0);
    emitBusEvent('CORE', 'PROCESS_START', 'Initiating Workspace Scan', { target: scanPath });

    // Simulate Scan Process
    let step = 0;
    const steps = [
      'Initializing Handlers...',
      'Crawling Directory Structure...',
      'Filtering Ignored Patterns...',
      'Reading File Contents...',
      'Running OCR Services...',
      'Compiling Knowledge Bundle...',
      'Finalizing Output...',
    ];

    const interval = setInterval(() => {
      setProgress((old) => {
        const next = old + 100 / steps.length;
        if (next >= 100) {
          clearInterval(interval);
          finishScan();
          return 100;
        }
        return next;
      });

      if (step < steps.length) {
        setCurrentStep(steps[step]);
        emitBusEvent('WORKER', 'PROGRESS', steps[step], { progress: Math.round((step / steps.length) * 100) });
        step++;
      }
    }, 800);
  };

  const finishScan = () => {
    setIsScanning(false);
    setCurrentStep('Completed');
    const newScan = {
      id: Date.now(),
      path: scanPath,
      date: new Date().toLocaleString(),
      status: 'success',
      bundleSize: (Math.random() * 10 + 1).toFixed(1) + 'MB',
    };
    setCompletedScans((prev) => [newScan, ...prev]);
    emitBusEvent('CORE', 'PROCESS_COMPLETE', 'Scan Finished Successfully', { output: newScan });
  };

  const handleClearLogs = () => {
    setBusLogs([]);
    emitBusEvent('DEBUG_TOOL', 'ACTION', 'Bus Logs Cleared');
  };

  return (
    <div className="flex h-screen bg-slate-900 text-slate-100 font-sans selection:bg-indigo-500 selection:text-white">
      {/* --- SIDEBAR --- */}
      <div className="w-64 bg-slate-950 border-r border-slate-800 flex flex-col shadow-2xl z-10">
        <div className="p-6 border-b border-slate-800 flex items-center gap-3">
          <div className="bg-indigo-600 p-2 rounded-lg">
            <Folder className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="font-bold text-lg tracking-tight">Packager</h1>
            <p className="text-xs text-slate-500">Workspace V2.3</p>
          </div>
        </div>

        <nav className="flex-1 p-4 space-y-2">
          <TabButton
            active={activeTab === 'workflows'}
            onClick={() => setActiveTab('workflows')}
            icon={<Activity size={20} />}
            label="Workflows"
          />
          <TabButton
            active={activeTab === 'debug'}
            onClick={() => setActiveTab('debug')}
            icon={<Terminal size={20} />}
            label="Debug Tools"
          />
        </nav>

        <div className="p-4 border-t border-slate-800">
          <div className="bg-slate-900 rounded p-3 flex items-center gap-3 border border-slate-800">
            <div className={`w-3 h-3 rounded-full ${isScanning ? 'bg-amber-500 animate-pulse' : 'bg-emerald-500'}`} />
            <div className="text-xs">
              <p className="text-slate-400">System Status</p>
              <p className="font-medium">{isScanning ? 'Processing...' : 'Ready'}</p>
            </div>
          </div>
        </div>
      </div>

      {/* --- MAIN CONTENT --- */}
      <div className="flex-1 flex flex-col overflow-hidden bg-slate-900">
        {/* Header */}
        <header className="h-16 border-b border-slate-800 bg-slate-900/50 backdrop-blur flex items-center justify-between px-8">
          <h2 className="text-xl font-semibold text-slate-200">
            {activeTab === 'workflows' ? 'Ingestion Workflows' : 'System Diagnostics & Bus'}
          </h2>
          <div className="flex items-center gap-4">
            <span className="text-xs font-mono text-slate-500">Bus Connection: LOCAL_MOCK</span>
          </div>
        </header>

        {/* Content Area */}
        <main className="flex-1 overflow-auto p-8 relative">
          {activeTab === 'workflows' && (
            <div className="max-w-5xl mx-auto space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
              {/* 1. INPUT AREA */}
              <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-8 shadow-lg">
                <div className="flex flex-col gap-4">
                  <label className="text-sm font-medium text-slate-400 uppercase tracking-wider">Target Scan Location</label>
                  <div className="flex gap-4">
                    <div className="relative flex-1 group">
                      <Folder className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500 group-focus-within:text-indigo-400 transition-colors" size={20} />
                      <input
                        type="text"
                        value={scanPath}
                        onChange={(e) => setScanPath(e.target.value)}
                        placeholder="/path/to/your/workspace"
                        disabled={isScanning}
                        className="w-full bg-slate-950 border border-slate-700 rounded-lg py-4 pl-12 pr-4 text-slate-100 placeholder:text-slate-600 focus:outline-none focus:ring-2 focus:ring-indigo-500/50 focus:border-indigo-500 transition-all font-mono"
                      />
                    </div>
                    <button
                      onClick={handleStartScan}
                      disabled={isScanning}
                      className={`px-8 rounded-lg font-semibold flex items-center gap-2 transition-all shadow-lg ${
                        isScanning
                          ? 'bg-slate-700 text-slate-400 cursor-not-allowed'
                          : 'bg-indigo-600 hover:bg-indigo-500 text-white hover:scale-105 active:scale-95'
                      }`}
                    >
                      {isScanning ? <RefreshCw className="animate-spin" size={20} /> : <Play size={20} />}
                      {isScanning ? 'Running...' : 'Run Scan'}
                    </button>
                  </div>
                </div>

                {/* ACTIVE MONITOR */}
                {(isScanning || progress > 0) && (
                  <div className="mt-8 pt-8 border-t border-slate-700/50">
                    <div className="flex justify-between items-end mb-2">
                      <span className="text-sm font-medium text-indigo-400 animate-pulse">{currentStep}</span>
                      <span className="text-xs font-mono text-slate-400">{Math.round(progress)}%</span>
                    </div>
                    <div className="h-3 bg-slate-900 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-indigo-500 shadow-[0_0_15px_rgba(99,102,241,0.5)] transition-all duration-300 ease-out relative"
                        style={{ width: `${progress}%` }}
                      >
                        <div className="absolute inset-0 bg-white/20 w-full animate-[shimmer_2s_infinite]" />
                      </div>
                    </div>
                  </div>
                )}
              </div>

              {/* 2. SCAN INDEX */}
              <div>
                <h3 className="text-lg font-semibold mb-4 text-slate-300 flex items-center gap-2">
                  <CheckCircle size={20} className="text-emerald-500" /> Completed Scans Index
                </h3>
                <div className="bg-slate-800/50 border border-slate-700 rounded-xl overflow-hidden shadow-lg">
                  <table className="w-full text-left border-collapse">
                    <thead>
                      <tr className="bg-slate-900/50 border-b border-slate-700 text-xs uppercase text-slate-500 tracking-wider">
                        <th className="p-4 font-medium">Status</th>
                        <th className="p-4 font-medium">Directory Path</th>
                        <th className="p-4 font-medium">Date Processed</th>
                        <th className="p-4 font-medium">Output Size</th>
                        <th className="p-4 font-medium text-right">Actions</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-700/50">
                      {completedScans.map((scan) => (
                        <tr key={scan.id} className="hover:bg-slate-700/30 transition-colors group">
                          <td className="p-4">
                            {scan.status === 'success' ? (
                              <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full bg-emerald-500/10 text-emerald-400 text-xs border border-emerald-500/20">
                                <CheckCircle size={12} /> Success
                              </span>
                            ) : (
                              <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full bg-amber-500/10 text-amber-400 text-xs border border-amber-500/20">
                                <AlertCircle size={12} /> Warning
                              </span>
                            )}
                          </td>
                          <td className="p-4 font-mono text-sm text-slate-300">{scan.path}</td>
                          <td className="p-4 text-sm text-slate-400">{scan.date}</td>
                          <td className="p-4 text-sm text-slate-400">{scan.bundleSize}</td>
                          <td className="p-4 text-right">
                            <button className="text-indigo-400 hover:text-indigo-300 text-sm font-medium hover:underline">
                              Open Folder
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                  {completedScans.length === 0 && (
                    <div className="p-12 text-center text-slate-500">
                      No scans completed yet. Run a workflow to see results here.
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}

          {activeTab === 'debug' && (
            <div className="h-full flex flex-col gap-6 animate-in fade-in slide-in-from-right-4 duration-500">
              {/* HELPER TOOLS */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                <DebugToolCard
                  title="Clear Cache"
                  desc="Flush temporary PDF artifacts"
                  icon={<Trash2 size={18} />}
                  action={() => emitBusEvent('TOOL', 'ACTION', 'Cache Cleared')}
                />
                <DebugToolCard
                  title="Verify Dependencies"
                  desc="Check OCR and PyMuPDF status"
                  icon={<Settings size={18} />}
                  action={() => emitBusEvent('TOOL', 'CHECK', 'Dependencies OK', { tesseract: 'v5.3', python: 'v3.11' })}
                />
                <DebugToolCard
                  title="Re-Index DB"
                  desc="Force update of local SQLite index"
                  icon={<Database size={18} />}
                  action={() => emitBusEvent('TOOL', 'DB', 'Re-index triggered')}
                />
              </div>

              {/* LOG MONITOR */}
              <div className="flex-1 bg-slate-950 rounded-xl border border-slate-800 flex flex-col shadow-2xl overflow-hidden">
                <div className="p-3 border-b border-slate-800 bg-slate-900 flex justify-between items-center">
                  <div className="flex items-center gap-2">
                    <Activity size={16} className="text-indigo-400" />
                    <span className="text-xs font-mono font-bold text-slate-300 uppercase tracking-wider">System Event Bus</span>
                  </div>
                  <div className="flex gap-2">
                    <button
                      onClick={handleClearLogs}
                      className="p-1.5 hover:bg-slate-800 rounded text-slate-400 hover:text-white transition-colors"
                      title="Clear Logs"
                    >
                      <Trash2 size={14} />
                    </button>
                  </div>
                </div>

                <div className="flex-1 overflow-auto p-4 font-mono text-xs space-y-1">
                  {busLogs.length === 0 && <div className="text-slate-600 italic p-4 text-center">Waiting for bus events...</div>}
                  {busLogs.map((log) => (
                    <div key={log.id} className="flex gap-3 hover:bg-white/5 p-1 rounded transition-colors group">
                      <span className="text-slate-500 shrink-0 w-32">{log.timestamp.split('T')[1].slice(0, -1)}</span>
                      <span className={`shrink-0 w-16 font-bold ${getSourceColor(log.source)}`}>{log.source}</span>
                      <span className={`shrink-0 w-24 ${getTypeColor(log.type)}`}>{log.type}</span>
                      <span className="text-slate-300 flex-1">{log.message}</span>
                      {log.payload && (
                        <span className="text-slate-500 truncate max-w-xs opacity-50 group-hover:opacity-100 transition-opacity">
                          {JSON.stringify(log.payload)}
                        </span>
                      )}
                    </div>
                  ))}
                  <div ref={logsEndRef} />
                </div>
              </div>
            </div>
          )}
        </main>
      </div>
    </div>
  );
}

// --- SUB COMPONENTS ---

function TabButton({ active, onClick, icon, label }) {
  return (
    <button
      onClick={onClick}
      className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-200 ${
        active
          ? 'bg-indigo-600/10 text-indigo-400 border border-indigo-500/20 shadow-sm'
          : 'text-slate-400 hover:bg-slate-800 hover:text-slate-200'
      }`}
    >
      {icon}
      <span className="font-medium text-sm">{label}</span>
      {active && <div className="ml-auto w-1.5 h-1.5 rounded-full bg-indigo-500 shadow-[0_0_8px_rgba(99,102,241,0.8)]" />}
    </button>
  );
}

function DebugToolCard({ title, desc, icon, action }) {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className="bg-slate-800/40 border border-slate-700 rounded-lg p-4 hover:border-indigo-500/50 transition-colors">
      <div className="flex justify-between items-start">
        <div className="flex gap-3 items-center mb-2">
          <div className="p-2 bg-slate-900 rounded text-slate-400 border border-slate-800">{icon}</div>
          <div>
            <h4 className="font-semibold text-sm text-slate-200">{title}</h4>
            <p className="text-xs text-slate-500">{desc}</p>
          </div>
        </div>
        <button onClick={() => setIsOpen(!isOpen)} className="text-slate-500 hover:text-white">
          {isOpen ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
        </button>
      </div>

      {isOpen && (
        <div className="mt-4 pt-4 border-t border-slate-700/50 animate-in fade-in slide-in-from-top-2">
          <button
            onClick={action}
            className="w-full py-2 bg-slate-700 hover:bg-indigo-600 text-slate-200 hover:text-white rounded text-xs font-medium transition-colors"
          >
            Execute Tool
          </button>
        </div>
      )}
    </div>
  );
}

// --- UTILS ---

function getSourceColor(source) {
  switch (source) {
    case 'UI':
      return 'text-purple-400';
    case 'CORE':
      return 'text-blue-400';
    case 'WORKER':
      return 'text-orange-400';
    case 'TOOL':
      return 'text-pink-400';
    default:
      return 'text-slate-400';
  }
}

function getTypeColor(type) {
  switch (type) {
    case 'ERROR':
      return 'text-red-500 font-bold';
    case 'WARNING':
      return 'text-amber-500';
    case 'SUCCESS':
      return 'text-emerald-500';
    case 'PROCESS_START':
      return 'text-cyan-400';
    default:
      return 'text-slate-500';
  }
}