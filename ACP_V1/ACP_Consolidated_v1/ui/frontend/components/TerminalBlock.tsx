import React, { useEffect, useState, useRef } from 'react';
import { Terminal } from 'lucide-react';

interface TerminalBlockProps {
  scriptName: string;
  args?: string[];
  autoRun?: boolean;
}

export const TerminalBlock: React.FC<TerminalBlockProps> = ({ scriptName, args = [], autoRun = false }) => {
  const [logs, setLogs] = useState<string[]>([]);
  const [status, setStatus] = useState<string>("READY");
  const ws = useRef<WebSocket | null>(null);

  const runScript = () => {
    setLogs([]);
    setStatus("RUNNING");
    ws.current = new WebSocket("ws://localhost:8090/ws/run-script");
    ws.current.onopen = () => {
      ws.current?.send(JSON.stringify({ name: scriptName, args }));
    };
    ws.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === 'log') setLogs(prev => [...prev, `> ${data.line}`]);
      if (data.type === 'error') setLogs(prev => [...prev, `❌ ${data.message}`]);
      if (data.type === 'status') {
        setStatus(data.message);
        ws.current?.close();
      }
    };
  };

  useEffect(() => {
    if (autoRun) runScript();
    return () => ws.current?.close();
  }, []);

  return (
    <div className="bg-black text-green-400 font-mono text-xs p-4 rounded-lg border border-gray-800 shadow-lg">
      <div className="flex justify-between border-b border-gray-800 pb-2 mb-2">
        <span className="flex items-center gap-2"><Terminal size={14}/> {scriptName}</span>
        <button onClick={runScript} className="hover:text-white underline">{status}</button>
      </div>
      <div className="h-48 overflow-y-auto space-y-1">
        {logs.map((log, i) => <div key={i}>{log}</div>)}
        {logs.length === 0 && <span className="opacity-50">Waiting for output...</span>}
      </div>
    </div>
  );
};
