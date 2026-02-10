import React, { useState } from 'react';

const DevToolsPage: React.FC = () => {
  const [status, setStatus] = useState<string>('');
  const [loading, setLoading] = useState(false);
  const [contextData, setContextData] = useState<string>('');

  const initializeContext = async () => {
    setLoading(true);
    setStatus('Scanning codebase...');
    try {
      // Hit the endpoint we just built
      const response = await fetch('http://localhost:8090/dev/initialize-context', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'x-api-key': 'dev_key' 
        }
      });
      
      const data = await response.json();
      
      if (response.ok) {
        setStatus(`✅ Success! Snapshot generated (${Math.round(data.token_estimate)} tokens).`);
        setContextData(data.system_context);
      } else {
        setStatus(`❌ Error: ${data.detail || 'Failed to initialize'}`);
      }
    } catch (err) {
      setStatus(`❌ Connection Error: Is the Backend running?`);
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = () => {
    navigator.clipboard.writeText(contextData);
    setStatus('✅ Copied to clipboard! Paste into Chat.');
  };

  return (
    <div className="p-8 max-w-4xl mx-auto text-slate-200">
      <h1 className="text-3xl font-bold mb-6 text-blue-400">Developer Operations</h1>
      
      <div className="grid gap-6">
        {/* Card: Context Primer */}
        <div className="bg-slate-800 p-6 rounded-xl border border-slate-700 shadow-lg">
          <h2 className="text-xl font-semibold mb-2 flex items-center gap-2">
            <span>🧠</span> System Context Primer
          </h2>
          <p className="mb-6 text-slate-400">
            Scans the local `ACP_v2` codebase, filters out noise, and generates a compressed 
            architectural snapshot. Use this to give the AI "sight" of the project.
          </p>
          
          <div className="flex gap-4">
            <button 
              onClick={initializeContext}
              disabled={loading}
              className={`
                px-6 py-3 rounded-lg font-medium transition-all
                ${loading 
                  ? 'bg-slate-600 cursor-wait' 
                  : 'bg-blue-600 hover:bg-blue-500 hover:shadow-blue-500/20 shadow-lg'}
              `}
            >
              {loading ? 'Running Scanner...' : 'Initialize System Context'}
            </button>

            {contextData && (
              <button 
                onClick={copyToClipboard}
                className="px-6 py-3 rounded-lg font-medium bg-emerald-600 hover:bg-emerald-500 transition-all text-white"
              >
                Copy to Clipboard
              </button>
            )}
          </div>

          {/* Status Output */}
          {status && (
            <div className={`mt-6 p-4 rounded-lg border font-mono text-sm ${
              status.includes('Error') ? 'bg-red-900/30 border-red-700 text-red-200' : 'bg-slate-900 border-slate-700'
            }`}>
              {status}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default DevToolsPage;
export const DevTools = DevToolsPage;