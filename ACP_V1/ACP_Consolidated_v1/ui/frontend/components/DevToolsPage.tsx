import React, { useState } from 'react';
import { Terminal, Activity, Database } from 'lucide-react';

export const DevTools = () => {
    const [activeTab, setActiveTab] = useState('terminal');
    const [commands, setCommands] = useState(['> systemctl status aletheia.service', '[OK] Service active (running)']);

    const runCommand = (e) => {
        if (e.key === 'Enter') {
            const cmd = e.target.value;
            setCommands([...commands, `> ${cmd}`, `[INFO] Executing '${cmd}'...`, '[DONE] Execution finished in 12ms']);
            e.target.value = '';
        }
    };

    return (
        <div className="h-full flex flex-col gap-4">
             <div className="flex justify-between items-end mb-2">
                <div>
                    <h2 className="text-2xl font-bold text-white mb-1">Developer Tools</h2>
                    <p className="text-gray-400 text-sm">System diagnostics and runtime control.</p>
                </div>
                <div className="flex gap-2 bg-gray-900 p-1 rounded-lg border border-gray-800">
                    {['terminal', 'network', 'storage'].map(tab => (
                        <button key={tab} onClick={() => setActiveTab(tab)} className={`px-4 py-1.5 text-sm rounded capitalize ${activeTab === tab ? 'bg-gray-700 text-white' : 'text-gray-400 hover:text-white'}`}>{tab}</button>
                    ))}
                </div>
            </div>

            <div className="flex-1 bg-black border border-gray-800 rounded-xl overflow-hidden flex flex-col font-mono text-sm">
                {activeTab === 'terminal' && (
                    <>
                        <div className="flex items-center justify-between px-4 py-2 bg-gray-900 border-b border-gray-800">
                            <span className="text-gray-400 text-xs">Gbsh: /usr/local/bin/aletheia</span>
                            <div className="flex gap-2">
                                <div className="w-3 h-3 rounded-full bg-red-500/20 border border-red-500"></div>
                                <div className="w-3 h-3 rounded-full bg-yellow-500/20 border border-yellow-500"></div>
                                <div className="w-3 h-3 rounded-full bg-green-500/20 border border-green-500"></div>
                            </div>
                        </div>
                        <div className="flex-1 p-4 overflow-y-auto space-y-1">
                            {commands.map((line, i) => (
                                <div key={i} className={`${line.startsWith('>') ? 'text-blue-400' : 'text-gray-300'}`}>{line}</div>
                            ))}
                        </div>
                        <div className="p-2 bg-gray-900 border-t border-gray-800 flex gap-2 items-center">
                            <span className="text-green-500">{'>'}</span>
                            <input type="text" onKeyDown={runCommand} className="flex-1 bg-transparent focus:outline-none text-white" placeholder="Enter command..." autoFocus />
                        </div>
                    </>
                )}
                 {activeTab === 'network' && (
                     <div className="p-8 text-center text-gray-500 flex flex-col items-center justify-center h-full gap-4">
                        <Activity size={48} className="opacity-20" />
                        <p>Network Trace Agent is initializing...</p>
                     </div>
                 )}
                 {activeTab === 'storage' && (
                     <div className="p-8 text-center text-gray-500 flex flex-col items-center justify-center h-full gap-4">
                        <Database size={48} className="opacity-20" />
                        <p>Local Vector Store: 142MB / 5GB used.</p>
                     </div>
                 )}
            </div>
        </div>
    );
};
