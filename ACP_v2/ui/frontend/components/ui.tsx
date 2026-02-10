import React from 'react';

export const Placeholder = ({ title, icon }) => (
    <div className="h-full flex flex-col">
        <div className="mb-6">
            <h2 className="text-2xl font-bold text-white mb-1">{title}</h2>
            <p className="text-gray-400 text-sm">This module is under construction.</p>
        </div>
        <div className="flex-1 bg-gray-950/50 border border-gray-800 rounded-xl border-dashed border-2 flex items-center justify-center flex-col gap-4 text-gray-600">
            {React.cloneElement(icon, { size: 48 })}
            <p>{title} interface will be available here.</p>
        </div>
    </div>
);

export const NavIcon = ({ icon: Icon, id, active, set, label }) => (
  <button onClick={() => set(id)} className={`p-3 my-1 rounded-xl transition-all duration-200 group relative ${active === id ? 'bg-blue-600 text-white shadow-lg shadow-blue-500/50' : 'text-gray-500 hover:bg-gray-800 hover:text-gray-200'}`} aria-label={label}>
    <Icon size={22} strokeWidth={active === id ? 2.5 : 2} />
    <span className="absolute left-full ml-4 bg-gray-800 text-white text-xs px-2 py-1 rounded opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap pointer-events-none border border-gray-700 z-50">{label}</span>
  </button>
);

export const ChatMessage = ({ role, text }) => (
  <div className={`flex gap-3 items-start ${role === 'user' ? 'justify-end' : 'justify-start'}`}>
    <div className={`max-w-[80%] rounded-2xl p-4 text-sm leading-relaxed ${role === 'user' ? 'bg-blue-600 text-white rounded-br-none' : 'bg-gray-800 text-gray-200 border border-gray-700 rounded-bl-none'}`}>{text}</div>
  </div>
);
