import React, { useState, useEffect, useRef } from 'react';
import { Database, Bot, Cpu, Send, Shield, Code, Layout, ChevronDown, Wrench, FileText, Edit3, AlertCircle } from 'lucide-react';
import AdaptiveMessage from './AdaptiveMessage';

const LLM_URL = "http://localhost:1234/v1/chat/completions";
const BACKEND_URL = "http://localhost:8090";

// Map string keys to Lucide Icons
const ICON_MAP: any = {
  Code: Code,
  Shield: Shield,
  Layout: Layout,
  Bot: Bot
};

// Helper for extracting JSON from LLM response
const extractToolCall = (content: string) => {
  const codeBlockMatch = content.match(/```json\n([\s\S]*?)\n```/);
  if (codeBlockMatch) {
    try { return JSON.parse(codeBlockMatch[1]); } catch (e) {}
  }
  const rawMatch = content.match(/\{[\s\S]*\}/);
  if (rawMatch) {
    try { 
      const parsed = JSON.parse(rawMatch[0]);
      if (parsed.tool) return parsed; 
    } catch (e) {}
  }
  return null;
};

const cleanReasoning = (content: string) => {
  return content.replace(/<think>[\s\S]*?<\/think>/g, "").trim();
};

export default function ChatPage() {
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [agentMode, setAgentMode] = useState(true);
  
  // Dynamic Profile State
  const [profiles, setProfiles] = useState<any>({});
  const [activeProfileKey, setActiveProfileKey] = useState<string>('coder');
  const [showProfileMenu, setShowProfileMenu] = useState(false);

  const [systemContext, setSystemContext] = useState<string | null>(null);
  const scrollRef = useRef<HTMLDivElement>(null);

  // 1. Fetch Identities on Mount
  useEffect(() => {
    const fetchIdentities = async () => {
      try {
        const res = await fetch(`${BACKEND_URL}/dev/identities`, {
          headers: { 'x-api-key': 'dev_key' }
        });
        const data = await res.json();
        if ((data.status === 'success' || data.status === 'fallback') && data.profiles && typeof data.profiles === 'object') {
          setProfiles(data.profiles);
          // Default to first available or coder
          const keys = Object.keys(data.profiles);
          if (keys.length > 0 && !data.profiles['coder']) {
             setActiveProfileKey(keys[0]);
          }
        } else {
          // Fallback if profiles is missing or invalid
          setProfiles({
            coder: { name: "Coder (Offline)", role: "system", content: "You are a coder.", icon_key: "Code" }
          });
        }
      } catch (e) {
        console.error("Failed to load identities:", e);
        // Fallback if backend is down
        setProfiles({
            coder: { name: "Coder (Offline)", role: "system", content: "You are a coder.", icon_key: "Code" }
        });
      }
    };
    fetchIdentities();
  }, []);

  // 2. Load System Context
  const loadSystemContext = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${BACKEND_URL}/dev/initialize-context`, {
        method: 'POST',
        headers: { 'x-api-key': 'dev_key' }
      });
      const data = await res.json();
      setSystemContext(data.system_context);
      setMessages(prev => [
        { role: 'system', content: `CONTEXT:\n${data.system_context}`, hidden: true },
        { role: 'assistant', content: "✅ Context Loaded." },
        ...prev
      ]);
    } catch (err) {
      setMessages(prev => [...prev, { role: 'assistant', content: `❌ Load failed: ${err}` }]);
    } finally {
      setLoading(false);
    }
  };

  // 3. Tool Execution Engine
  const executeTool = async (toolCall: any) => {
    const { tool, arguments: args } = toolCall;
    let result = "";
    try {
        let endpoint = "";
        if (tool === "read_file") endpoint = "/dev/read-file";
        if (tool === "write_file") endpoint = "/dev/write-file";
        if (tool === "list_directory") endpoint = "/dev/list-directory";
        if (tool === "activate_workflow") endpoint = "/dev/activate-workflow";
        
        if (!endpoint) throw new Error("Unknown tool");

        const res = await fetch(`${BACKEND_URL}${endpoint}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'x-api-key': 'dev_key' },
            body: JSON.stringify(args)
        });
        const data = await res.json();
        result = JSON.stringify(data, null, 2);
    } catch (e: any) {
        result = `Error: ${e.message}`;
    }

    const outputMsg = {
        role: "user",
        content: `Tool Output (${tool}):\n\`\`\`json\n${result}\n\`\`\``,
        label: "Tool Output",
        isTool: true
    };
    setMessages(prev => [...prev, outputMsg]);
    // Loop back to LLM with result
    await sendMessageLoop(outputMsg.content, "user", true); 
  };

  // 4. Chat Logic
  const handleUserSend = async () => {
    if (!input.trim()) return;
    const content = input;
    setInput('');
    await sendMessageLoop(content, "user", false);
  };

  const sendMessageLoop = async (content: string, role: string, isAuto: boolean) => {
    if (!isAuto) setMessages(prev => [...prev, { role, content }]);
    setLoading(true);

    try {
        // Construct Messages
        const apiMessages = messages
            .concat(isAuto ? [] : { role, content })
            .filter(m => !m.hidden)
            .map(m => ({ role: m.role, content: m.content }));

        // Inject Identity (System Prompt)
        if (agentMode && profiles[activeProfileKey]) {
            const identity = profiles[activeProfileKey];
            // Ensure identity is the very first message
            apiMessages.unshift({ role: "system", content: identity.content });
        }

        const res = await fetch(LLM_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                model: "local-model",
                messages: apiMessages,
                temperature: 0.1,
                stream: false
            })
        });
        
        const data = await res.json();
        const raw = data.choices?.[0]?.message?.content || "";
        const clean = cleanReasoning(raw);
        const toolCall = extractToolCall(clean);

        if (toolCall && agentMode) {
            setMessages(prev => [...prev, { role: 'assistant', content: `🛠️ Using Tool: ${toolCall.tool}`, isTool: true }]);
            await executeTool(toolCall);
        } else {
            setMessages(prev => [...prev, { role: 'assistant', content: clean }]);
        }

    } catch (e) {
        setMessages(prev => [...prev, { role: 'assistant', content: "⚠️ Connection Error" }]);
    } finally {
        setLoading(false);
    }
  };

  // Render Helpers
  const activeProfile = profiles[activeProfileKey] || { name: "Loading...", icon_key: "Bot" };
  const ActiveIcon = ICON_MAP[activeProfile.icon_key] || Bot;

  return (
    <div className="flex flex-col h-full bg-[#1e1e1e] text-slate-200 font-sans">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-slate-700 bg-slate-800">
        <div className="flex items-center gap-4">
            <h1 className="font-bold text-lg flex items-center gap-2">
                <Bot className="w-6 h-6 text-blue-400" />
                Aletheia Operations
            </h1>
            <button onClick={loadSystemContext} disabled={!!systemContext} className="px-3 py-1 bg-blue-600 rounded text-xs hover:bg-blue-500 transition-colors flex items-center gap-2">
                <Database className="w-3 h-3" />
                {systemContext ? "Context Active" : "Load Context"}
            </button>
        </div>

        <div className="flex items-center gap-2 relative">
            {/* Identity Dropdown */}
            <button onClick={() => setShowProfileMenu(!showProfileMenu)} className="flex items-center gap-2 px-3 py-1.5 bg-slate-700 rounded-l-full hover:bg-slate-600 text-xs font-bold transition-colors">
                <ActiveIcon className="w-3 h-3 text-blue-300" />
                {activeProfile.name}
                <ChevronDown className="w-3 h-3 opacity-50" />
            </button>
            
            {showProfileMenu && (
                <div className="absolute top-full right-0 mt-2 w-64 bg-slate-800 border border-slate-600 rounded-xl shadow-xl overflow-hidden z-50">
                    <div className="p-2 bg-slate-900 border-b border-slate-700 text-xs font-bold text-slate-400 uppercase">Select Identity</div>
                    {Object.entries(profiles).map(([key, p]: any) => {
                        const Icon = ICON_MAP[p.icon_key] || Bot;
                        return (
                            <button key={key} onClick={() => { setActiveProfileKey(key); setShowProfileMenu(false); }} className="w-full text-left px-4 py-3 hover:bg-slate-700 flex items-center gap-3 text-xs border-b border-slate-700/50 last:border-0">
                                <Icon className="w-4 h-4 text-slate-400" />
                                <div>
                                    <div className="font-bold text-slate-200">{p.name}</div>
                                    <div className="text-[10px] text-slate-500 truncate w-40">{p.role}</div>
                                </div>
                            </button>
                        );
                    })}
                </div>
            )}

            <button onClick={() => setAgentMode(!agentMode)} className={`flex items-center gap-2 px-3 py-1.5 rounded-r-full text-xs font-bold border-l border-slate-600 ${agentMode ? 'bg-emerald-900/50 text-emerald-400' : 'bg-slate-800 text-slate-400'}`}>
                <Cpu className="w-3 h-3" />
                {agentMode ? "ON" : "OFF"}
            </button>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 custom-scrollbar">
        {messages.map((msg, idx) => (
            <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`max-w-[85%] rounded-2xl p-4 ${msg.role === 'user' ? 'bg-blue-600 text-white' : msg.isTool ? 'bg-purple-900/40 border border-purple-500/30 font-mono text-xs' : 'bg-slate-800 border border-slate-700'}`}>
                    {msg.label && <div className="text-[10px] uppercase text-slate-400 mb-1 border-b border-white/10 pb-1">{msg.label}</div>}
                    <AdaptiveMessage content={msg.content} />
                </div>
            </div>
        ))}
        {loading && <div className="p-4 text-slate-500 text-xs animate-pulse">Thinking...</div>}
        <div ref={scrollRef} />
      </div>

      {/* Input */}
      <div className="p-4 bg-slate-800 border-t border-slate-700">
        <div className="flex gap-2 max-w-4xl mx-auto">
            <input type="text" value={input} onChange={(e) => setInput(e.target.value)} onKeyDown={(e) => e.key === 'Enter' && handleUserSend()} className="flex-1 bg-slate-900 border border-slate-600 rounded-xl px-4 py-3 text-sm text-white focus:outline-none focus:border-blue-500" placeholder={`Command ${activeProfile.name}...`} />
            <button onClick={handleUserSend} disabled={loading} className="bg-blue-600 text-white p-3 rounded-xl hover:bg-blue-500 transition-all"><Send className="w-5 h-5" /></button>
        </div>
      </div>
    </div>
  );
}