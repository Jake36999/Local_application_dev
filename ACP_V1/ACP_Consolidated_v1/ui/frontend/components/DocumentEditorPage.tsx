import React from 'react';
import { Bold, Italic, List, AlignLeft, Save } from 'lucide-react';

export const DocumentEditor = () => {
    return (
        <div className="h-full flex flex-col max-w-5xl mx-auto">
             <div className="flex justify-between items-center mb-4">
                <div className="flex items-center gap-4">
                    <input type="text" defaultValue="Untitled_System_Design.md" className="bg-transparent text-xl font-bold text-white focus:outline-none border-b border-transparent focus:border-blue-500" />
                    <span className="text-xs text-gray-500">Last saved: Just now</span>
                </div>
                <button className="flex items-center gap-2 bg-gray-100 text-gray-900 px-4 py-2 rounded-lg text-sm font-semibold hover:bg-white"><Save size={16}/> Save Doc</button>
            </div>

            <div className="flex-1 bg-white rounded-xl overflow-hidden text-gray-900 flex flex-col">
                <div className="bg-gray-100 border-b border-gray-200 p-2 flex gap-2">
                    <button className="p-2 hover:bg-gray-200 rounded"><Bold size={18} /></button>
                    <button className="p-2 hover:bg-gray-200 rounded"><Italic size={18} /></button>
                    <div className="w-px h-8 bg-gray-300 mx-1" />
                    <button className="p-2 hover:bg-gray-200 rounded"><AlignLeft size={18} /></button>
                    <button className="p-2 hover:bg-gray-200 rounded"><List size={18} /></button>
                </div>
                <textarea 
                    className="flex-1 p-8 text-lg font-serif focus:outline-none resize-none leading-relaxed" 
                    placeholder="Start typing your documentation..."
                    defaultValue="# System Architecture v1.0\n\n## 1. Overview\nThe proposed system utilizes a microservices architecture..."
                />
            </div>
        </div>
    );
};
