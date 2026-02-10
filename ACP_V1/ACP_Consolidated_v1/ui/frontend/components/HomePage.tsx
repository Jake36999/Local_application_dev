import React from 'react';
import { Cpu, ShieldCheck, Users, Code, Clock } from 'lucide-react';

// FIX: Made `progress` prop optional by setting a default value to fix missing prop errors.
const MetricCard = ({ icon, title, value, footer, progress = undefined }) => (
    <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-4 flex flex-col justify-between">
        <div>
            <div className="flex items-center gap-2 text-gray-400 mb-2">
                {icon}
                <span className="text-sm font-medium">{title}</span>
            </div>
            <div className="text-3xl font-bold text-white mb-2">{value}</div>
        </div>
        {progress !== undefined ? (
            <div>
                <div className="w-full bg-gray-700 rounded-full h-1.5 mb-1">
                    <div className="bg-blue-500 h-1.5 rounded-full" style={{width: `${progress}%`}}></div>
                </div>
                 <p className="text-xs text-gray-500">{footer}</p>
            </div>
        ) : (
            <p className="text-xs text-gray-500">{footer}</p>
        )}
    </div>
);

const ActivityItem = ({ icon, text, time }) => (
    <div className="flex items-center gap-3 py-2 border-b border-gray-800/50 last:border-b-0">
        <div className="text-gray-500">{icon}</div>
        <div className="flex-1">
            <p className="text-sm text-gray-200">{text}</p>
        </div>
        <div className="text-xs text-gray-500 font-mono flex items-center gap-1.5">
            <Clock size={12} />
            <span>{time}</span>
        </div>
    </div>
);

export const HomeDashboard = ({ logs }) => {
    const renderLog = (log, i) => {
        let color = 'text-gray-400';
        if (log.includes('[ERROR]')) color = 'text-red-400';
        else if (log.includes('[REASONING]')) color = 'text-purple-400';
        else if (log.includes('[INFO]')) color = 'text-blue-400';
        return <div key={i} className={`whitespace-nowrap ${color}`}><span className="text-gray-600 mr-2">{'>'}</span>{log}</div>;
    };

    return (
        <div className="max-w-7xl mx-auto h-full flex flex-col gap-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                {/* Hero Section */}
                <div className="lg:col-span-1 bg-gradient-to-br from-blue-600 to-purple-700 rounded-xl p-6 text-white flex flex-col justify-between shadow-lg">
                    <h2 className="text-xl font-bold">Welcome Back</h2>
                    <div>
                         <p className="text-4xl font-bold">System Nominal</p>
                         <p className="text-blue-200 text-sm">All agents and services are operational.</p>
                    </div>
                </div>

                {/* Live Metrics Grid */}
                <div className="lg:col-span-3 grid grid-cols-1 md:grid-cols-3 gap-6">
                    <MetricCard 
                        icon={<Cpu size={16} />} 
                        title="Context Usage" 
                        value="12,400"
                        footer="of 128k Tokens"
                        progress={(12400/128000)*100}
                    />
                    <MetricCard 
                        icon={<ShieldCheck size={16} />} 
                        title="Stability Score" 
                        value="99.8%"
                        footer="Calculated from 1,203 checks"
                    />
                    <MetricCard 
                        icon={<Users size={16} />} 
                        title="Active Agents" 
                        value="5"
                        footer="Orchestrator reporting 2 idle"
                    />
                </div>
            </div>

            {/* Recent Activity & Live Terminal */}
            <div className="flex-1 grid grid-cols-1 lg:grid-cols-3 gap-6 overflow-hidden">
                <div className="lg:col-span-1 bg-gray-900/50 border border-gray-800 rounded-xl p-4 flex flex-col">
                    <h3 className="font-semibold text-lg text-white mb-2">Recent Activity</h3>
                    <p className="text-sm text-gray-400 mb-4">Latest actions from the Code Factory.</p>
                    <div className="flex flex-col">
                        <ActivityItem icon={<Code size={16}/>} text="Generated Stack: Payment Gateway" time="2m ago" />
                        <ActivityItem icon={<Code size={16}/>} text="Audited Module: auth_v1.json" time="15m ago" />
                        <ActivityItem icon={<Code size={16}/>} text="Deployed Service: JWT_Service" time="45m ago" />
                    </div>
                </div>
                <div className="lg:col-span-2 bg-black border border-gray-800 rounded-xl p-4 font-mono text-xs flex flex-col h-full shadow-inner">
                     <div className="flex justify-between items-center mb-2 pb-2 border-b border-gray-800">
                        <h3 className="text-sm text-gray-300">Live Telemetry: aletheia_system.log</h3>
                        <span className="text-green-500 animate-pulse flex items-center gap-1.5 text-xs">● LIVE</span>
                     </div>
                     <div className="flex-1 overflow-y-auto flex flex-col-reverse">
                        <div className="flex flex-col-reverse gap-1">
                            {logs.map(renderLog)}
                        </div>
                     </div>
                </div>
            </div>
        </div>
    );
};
