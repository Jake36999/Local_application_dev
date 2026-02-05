import React, { useState } from 'react';
import { ToggleLeft, ToggleRight } from 'lucide-react';

export const LMSetup = () => {
    const [apiBridge, setApiBridge] = useState(false);
    return (
        <div className="max-w-4xl mx-auto">
            <div className="mb-6">
                <h2 className="text-2xl font-bold text-white mb-1">LM Runtime & Governance</h2>
                <p className="text-gray-400 text-sm">Configure model runtimes and context window parameters.</p>
            </div>
            <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-6 space-y-6">
                <div className="flex justify-between items-center p-4 bg-gray-800/50 rounded-lg">
                    <div>
                        <h4 className="font-medium text-white">API Bridge</h4>
                        <p className="text-xs text-gray-400">Enable isolation layer between local and cloud environments.</p>
                    </div>
                    <button onClick={() => setApiBridge(!apiBridge)} className="flex items-center gap-2 text-2xl">
                        {apiBridge ? <ToggleRight className="text-green-500"/> : <ToggleLeft className="text-gray-500"/>}
                    </button>
                </div>
                <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">Context Window</label>
                    <input type="range" min="1000" max="128000" defaultValue="12400" step="1000" className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer" />
                    <p className="text-xs text-gray-500 mt-1 text-right">12,400 Tokens</p>
                </div>
                <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">Generations</label>
                    <input type="number" defaultValue="5" className="w-full bg-gray-800 border border-gray-700 rounded-md p-2 text-sm" />
                    <p className="text-xs text-gray-500 mt-1">Limits recursive prompt iteration rounds.</p>
                </div>
                 <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">Containment</label>
                    <input type="text" disabled value="Hard-coded via safe_ops/isolation_layer.py" className="w-full bg-gray-800 border border-gray-700 rounded-md p-2 text-sm text-gray-500" />
                    <p className="text-xs text-gray-500 mt-1">Defines the sandbox boundary for execution.</p>
                </div>
            </div>
        </div>
    );
};
