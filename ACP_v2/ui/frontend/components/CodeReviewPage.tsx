import React from 'react';
import { GitPullRequest, Check, X } from 'lucide-react';

export const CodeReview = () => {
    return (
        <div className="h-full flex flex-col gap-4">
             <div className="flex justify-between items-end mb-2">
                <div>
                    <h2 className="text-2xl font-bold text-white mb-1">Code Review</h2>
                    <p className="text-gray-400 text-sm">PR #42: Feature/Auth-Middleware-Integration</p>
                </div>
                <div className="flex gap-3">
                     <button className="flex items-center gap-2 px-4 py-2 bg-red-900/30 text-red-400 border border-red-800 hover:bg-red-900/50 rounded-lg text-sm"><X size={16}/> Request Changes</button>
                     <button className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white hover:bg-green-500 rounded-lg text-sm font-medium"><Check size={16}/> Approve Merge</button>
                </div>
            </div>

            <div className="bg-gray-900/50 border border-gray-800 rounded-xl overflow-hidden flex-1 flex flex-col">
                <div className="flex items-center gap-2 p-3 bg-gray-950 border-b border-gray-800 text-sm">
                    <GitPullRequest size={16} className="text-purple-500" />
                    <span className="text-gray-300 font-mono">middleware/auth.ts</span>
                    <span className="text-gray-600">-- +24, -2 lines</span>
                </div>
                <div className="flex-1 overflow-auto font-mono text-sm">
                    <div className="flex bg-gray-900/30">
                        <div className="w-12 text-right pr-3 text-gray-600 select-none py-1">21</div>
                        <div className="flex-1 py-1 text-gray-400 pl-4">  const token = req.headers['authorization'];</div>
                    </div>
                    <div className="flex bg-red-900/10">
                        <div className="w-12 text-right pr-3 text-gray-600 select-none py-1 bg-red-900/20 border-r border-red-800/50">22</div>
                        <div className="flex-1 py-1 text-red-300 pl-4 bg-red-900/10">- if (!token) return res.status(401).send();</div>
                    </div>
                    <div className="flex bg-green-900/10">
                        <div className="w-12 text-right pr-3 text-gray-600 select-none py-1 bg-green-900/20 border-r border-green-800/50">22</div>
                        <div className="flex-1 py-1 text-green-300 pl-4 bg-green-900/10">+ if (!token) throw new AuthenticationError('Token missing');</div>
                    </div>
                    <div className="flex bg-gray-900/30">
                         <div className="w-12 text-right pr-3 text-gray-600 select-none py-1">23</div>
                         <div className="flex-1 py-1 text-gray-400 pl-4">  try {'{'}</div>
                    </div>
                </div>
                <div className="p-4 border-t border-gray-800 bg-gray-900">
                    <div className="flex gap-3">
                        <div className="w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center text-xs font-bold text-white">AI</div>
                        <div className="flex-1">
                            <p className="text-sm text-gray-200 mb-2"><span className="font-bold text-blue-400">Aletheia Bot:</span> The exception class `AuthenticationError` is not imported. This will cause a runtime crash.</p>
                            <button className="text-xs text-blue-400 hover:text-blue-300 underline">Apply Fix Import</button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};
