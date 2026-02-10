import React, { useState } from 'react';
import { FileText, Save, Folder, RefreshCw, AlertCircle, CheckCircle } from 'lucide-react';

const CodeEditorPage: React.FC = () => {
  const [filePath, setFilePath] = useState('');
  const [code, setCode] = useState('// Select a file to edit...');
  const [status, setStatus] = useState<{ type: 'success' | 'error' | 'loading' | 'idle', msg: string }>({ type: 'idle', msg: '' });

  // Ensure this matches your running backend port
  const API_BASE = 'http://localhost:8090'; 

  const loadFile = async () => {
    if (!filePath) return;
    setStatus({ type: 'loading', msg: 'Loading file...' });
    
    try {
      const res = await fetch(`${API_BASE}/dev/read-file`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'x-api-key': 'dev_key'
        },
        body: JSON.stringify({ path: filePath })
      });
      
      const data = await res.json();
      
      if (res.ok) {
        setCode(data.content);
        setStatus({ type: 'success', msg: 'File loaded.' });
      } else {
        setStatus({ type: 'error', msg: data.detail || 'Failed to load file' });
      }
    } catch (err) {
      setStatus({ type: 'error', msg: `Connection Error: ${err}` });
    }
  };

  const saveFile = async () => {
    if (!filePath) return;
    setStatus({ type: 'loading', msg: 'Saving...' });
    
    try {
      const res = await fetch(`${API_BASE}/dev/write-file`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'x-api-key': 'dev_key'
        },
        body: JSON.stringify({ path: filePath, content: code })
      });
      
      const data = await res.json();
      
      if (res.ok) {
        setStatus({ type: 'success', msg: `Saved! (${data.bytes_written} bytes)` });
      } else {
        setStatus({ type: 'error', msg: data.detail || 'Failed to save' });
      }
    } catch (err) {
      setStatus({ type: 'error', msg: `Connection Error: ${err}` });
    }
  };

  return (
    <div className="h-[calc(100vh-4rem)] flex flex-col p-6 text-slate-200">
      {/* Toolbar */}
      <div className="flex justify-between items-center mb-6 bg-slate-800 p-4 rounded-xl border border-slate-700 shadow-lg">
        <div className="flex items-center gap-3">
          <FileText className="w-6 h-6 text-blue-400" />
          <h1 className="text-xl font-bold">Code Editor</h1>
        </div>
        
        <div className="flex gap-2 w-full max-w-3xl justify-end">
          <div className="relative w-full max-w-md">
            <input 
              type="text" 
              value={filePath}
              onChange={(e) => setFilePath(e.target.value)}
              placeholder="Path (e.g., config/settings.py)"
              className="w-full px-4 py-2 bg-slate-900 border border-slate-600 rounded-lg text-sm font-mono focus:outline-none focus:border-blue-500 transition-colors"
              onKeyDown={(e) => e.key === 'Enter' && loadFile()}
            />
          </div>
          
          <button 
            onClick={loadFile}
            className="bg-slate-700 hover:bg-slate-600 px-4 py-2 rounded-lg flex items-center gap-2 text-sm font-medium transition-colors"
          >
            <Folder className="w-4 h-4" /> Load
          </button>
          
          <button 
            onClick={saveFile}
            className="bg-blue-600 hover:bg-blue-500 px-6 py-2 rounded-lg flex items-center gap-2 text-sm font-medium transition-colors shadow-md hover:shadow-blue-500/20"
          >
            <Save className="w-4 h-4" /> Save
          </button>
        </div>
      </div>

      {/* Editor Area */}
      <div className="flex-1 bg-[#1e1e1e] border border-slate-700 rounded-xl overflow-hidden shadow-2xl relative">
        <textarea
          value={code}
          onChange={(e) => setCode(e.target.value)}
          className="w-full h-full bg-transparent p-6 font-mono text-sm resize-none focus:outline-none text-slate-300 leading-relaxed custom-scrollbar"
          spellCheck="false"
        />
        
        {/* Status Toast */}
        {status.type !== 'idle' && (
          <div className={`absolute bottom-6 right-6 px-4 py-2 rounded-lg text-xs font-mono shadow-lg flex items-center gap-2 border ${
            status.type === 'error' ? 'bg-red-900/90 border-red-700 text-red-100' :
            status.type === 'success' ? 'bg-emerald-900/90 border-emerald-700 text-emerald-100' :
            'bg-slate-800/90 border-slate-600 text-slate-300'
          }`}>
            {status.type === 'loading' && <RefreshCw className="w-3 h-3 animate-spin" />}
            {status.type === 'error' && <AlertCircle className="w-3 h-3" />}
            {status.type === 'success' && <CheckCircle className="w-3 h-3" />}
            {status.msg}
          </div>
        )}
      </div>
    </div>
  );
};

export const CodeEditor = CodeEditorPage;
export default CodeEditorPage;