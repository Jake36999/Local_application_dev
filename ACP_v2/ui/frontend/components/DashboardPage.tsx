import React, { useState } from 'react';

export const InternalAuditDashboard = ({ logs }) => {
    const [logSource, setLogSource] = useState('system');
    const [filter, setFilter] = useState('ALL');
    const filteredLogs = logs.filter(log => filter === 'ALL' || log.includes(`[${filter}]`));
    
    const renderLog = (log, i) => {
        let color = 'text-gray-300';
        if (log.includes('[ERROR]')) color = 'text-red-400';
        else if (log.includes('[REASONING]')) color = 'text-purple-400';
        else if (log.includes('[INFO]')) color = 'text-blue-400';
        return <div key={i} className={`truncate opacity-80 hover:opacity-100 ${color}`}><span className="text-gray-500 mr-2">{'>'}</span>{log}</div>;
    };

    return (
        <div className="grid grid-cols-12 gap-6 max-w-7xl mx-auto">
            <div className="col-span-12">
                <h2 className="text-2xl font-bold text-white mb-1">Internal Audit</h2>
                <p className="text-gray-400 text-sm">Telemetry from aletheia_system.log and test_results.log.</p>
            </div>
            <div className="col-span-12 md:col-span-8 bg-black border border-gray-800 rounded-xl p-4 font-mono text-xs flex flex-col h-[60vh] shadow-inner">
                <div className="flex justify-between items-center mb-2 pb-2 border-b border-gray-800">
                    <div className="flex items-center gap-2">
                        <div className="flex gap-1 bg-gray-800 p-1 rounded-md">
                            <button onClick={() => setLogSource('system')} className={`px-2 py-0.5 text-xs rounded ${logSource === 'system' ? 'bg-gray-700 text-white' : 'text-gray-400 hover:text-white'}`}>aletheim_system.log</button>
                            <button onClick={() => setLogSource('test')} className={`px-2 py-0.5 text-xs rounded ${logSource === 'test' ? 'bg-gray-700 text-white' : 'text-gray-400 hover:text-white'}`}>test_results.log</button>
                        </div>
                    </div>
                    <span className="text-green-500 animate-pulse">● LIVE</span>
                </div>
                <div className="flex-1 overflow-y-auto flex flex-col-reverse">{filteredLogs.map(renderLog)}</div>
            </div>
            <div className="col-span-12 md:col-span-4">
                <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-4">
                    <h3 className="font-semibold text-lg flex items-center gap-2 mb-4">Log Filtering</h3>
                    <div className="flex flex-col gap-2">
                        {['ALL', 'INFO', 'ERROR', 'REASONING'].map(f => (
                            <button key={f} onClick={() => setFilter(f)} className={`w-full text-left px-3 py-2 text-sm rounded ${filter === f ? 'bg-blue-600 text-white' : 'bg-gray-800 text-gray-300 hover:bg-gray-700'}`}>{f}</button>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
};
