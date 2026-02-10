import React from 'react';
import { FileText, AlertCircle, CheckCircle } from 'lucide-react';

export const DocReview = () => {
    return (
        <div className="h-full flex gap-6">
            <div className="w-64 shrink-0 flex flex-col gap-4">
                <h2 className="text-xl font-bold text-white">Review Queue</h2>
                <div className="space-y-2">
                    {['technical_spec_v2.pdf', 'api_contract_draft.md', 'compliance_audit.docx'].map((file, i) => (
                        <div key={i} className={`p-3 rounded-lg border cursor-pointer transition-all ${i === 0 ? 'bg-blue-900/20 border-blue-500 text-white' : 'bg-gray-900/50 border-gray-800 text-gray-400 hover:border-gray-600'}`}>
                            <div className="flex items-center gap-2 mb-1">
                                <FileText size={16} />
                                <span className="text-sm font-medium truncate">{file}</span>
                            </div>
                            <div className="flex justify-between items-center text-xs opacity-70">
                                <span>2 mins ago</span>
                                <span className="bg-gray-800 px-1.5 py-0.5 rounded">Pending</span>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
            
            <div className="flex-1 bg-gray-900/50 border border-gray-800 rounded-xl flex flex-col overflow-hidden">
                <div className="p-4 border-b border-gray-800 bg-gray-950 flex justify-between items-center">
                    <h3 className="font-semibold text-white">technical_spec_v2.pdf</h3>
                    <button className="bg-blue-600 text-white text-xs px-3 py-1.5 rounded-md hover:bg-blue-500">Run Auto-Audit</button>
                </div>
                <div className="flex-1 p-6 overflow-y-auto">
                    <div className="max-w-3xl mx-auto space-y-6">
                        <div className="p-4 bg-red-900/20 border border-red-800/50 rounded-lg">
                            <div className="flex items-center gap-2 text-red-400 mb-2 font-bold">
                                <AlertCircle size={18} />
                                <span>Critical Finding: Security Policy Missing</span>
                            </div>
                            <p className="text-sm text-gray-300">The specification defines public endpoints but lacks an authentication schema definition in Section 4.2.</p>
                        </div>
                        <div className="p-4 bg-green-900/20 border border-green-800/50 rounded-lg">
                            <div className="flex items-center gap-2 text-green-400 mb-2 font-bold">
                                <CheckCircle size={18} />
                                <span>Compliance Pass: Data Retention</span>
                            </div>
                            <p className="text-sm text-gray-300">GDPR compliance checks passed for data storage lifecycle definitions.</p>
                        </div>
                        <div className="h-96 bg-gray-800/30 rounded-lg animate-pulse"></div>
                    </div>
                </div>
            </div>
        </div>
    );
};
