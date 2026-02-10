import { useState, useEffect } from 'react';
import { ToggleLeft, ToggleRight, Server, Activity, CheckCircle, AlertCircle } from 'lucide-react';

export function LMSetup() {
    const [apiBridge, setApiBridge] = useState(false);
    const [backendStatus, setBackendStatus] = useState<'checking' | 'online' | 'offline'>('checking');

    useEffect(() => {
        checkBackend();
    }, []);

    const checkBackend = async () => {
        try {
            const res = await fetch('http://localhost:8090/health');
            if (res.ok) setBackendStatus('online');
            else setBackendStatus('offline');
        } catch (e) {
            setBackendStatus('offline');
        }
    };

    return (
        <div className="max-w-4xl mx-auto p-8 text-slate-200">
            <div className="mb-8">
                <h2 className="text-3xl font-bold text-white mb-2">LM Runtime & Governance</h2>
                <p className="text-slate-400">Configure model runtimes and verify system connectivity.</p>
            </div>

            <div className="grid gap-6">
                {/* System Health Card */}
                <div className="bg-slate-800 border border-slate-700 rounded-xl p-6 shadow-lg">
                    <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                        <Activity className="w-5 h-5 text-blue-400" />
                        System Status
                    </h3>
                    
                    <div className="flex items-center justify-between bg-slate-900/50 p-4 rounded-lg border border-slate-700">
                        <div className="flex items-center gap-3">
                            <Server className="w-5 h-5 text-slate-400" />
                            <div>
                                <div className="font-medium">Backend API (Tools)</div>
                                <div className="text-xs text-slate-500">http://localhost:8090</div>
                            </div>
                        </div>
                        <div className={`flex items-center gap-2 px-3 py-1 rounded-full text-xs font-bold border ${
                            backendStatus === 'online' 
                                ? 'bg-emerald-900/30 border-emerald-800 text-emerald-400' 
                                : 'bg-red-900/30 border-red-800 text-red-400'
                        }`}>
                            {backendStatus === 'online' ? <CheckCircle className="w-3 h-3" /> : <AlertCircle className="w-3 h-3" />}
                            {backendStatus.toUpperCase()}
                        </div>
                    </div>
                </div>

                {/* Configuration Card */}
                <div className="bg-slate-800 border border-slate-700 rounded-xl p-6 shadow-lg space-y-6">
                    <div className="flex justify-between items-center pb-6 border-b border-slate-700">
                        <div>
                            <h4 className="font-medium text-white">API Bridge</h4>
                            <p className="text-sm text-slate-400">Enable isolation layer between local and cloud environments.</p>
                        </div>
                        <button onClick={() => setApiBridge(!apiBridge)} className="text-3xl transition-colors">
                            {apiBridge ? <ToggleRight className="text-emerald-500"/> : <ToggleLeft className="text-slate-500"/>}
                        </button>
                    </div>

                    <div className="space-y-4">
                        <div>
                            <label htmlFor="context-window" className="block text-sm font-medium text-slate-300 mb-2">Context Window</label>
                            <input id="context-window" name="context-window" type="range" min="1000" max="128000" defaultValue="12400" step="1000" className="w-full h-2 bg-slate-600 rounded-lg appearance-none cursor-pointer accent-blue-500" />
                            <p className="text-xs text-slate-500 mt-2 text-right">12,400 Tokens</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
export default LMSetup;