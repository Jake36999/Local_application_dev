import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Terminal } from 'lucide-react';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import AdaptiveMessage from './chat/AdaptiveMessage';
import CognitiveToolbar from './chat/CognitiveToolbar';
import { TerminalBlock } from './TerminalBlock';
import DialecticalView from './DialecticalView';

export default function ChatPage() {
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [dialecticalMode, setDialecticalMode] = useState(false);
  const [activeLens, setActiveLens] = useState('None');
  const scrollRef = useRef<HTMLDivElement>(null);

  // Connect to LM Studio (The Brain)
  const LLM_URL = "http://localhost:1234/v1/chat/completions";
  const BACKEND_URL = import.meta.env.VITE_API_URL || "http://localhost:8090";

  const sendMessage = async () => {
    if (!input.trim()) return;

    // 1. Update backend cognitive state
    await fetch(`${BACKEND_URL}/system/set-cognitive-state`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ lens: activeLens, dialectical: dialecticalMode })
    });

    const userMsg = { role: 'user', content: input };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    try {
      // 2. Send Request to AI
      const response = await fetch(LLM_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          model: "local-model",
          messages: [...messages, userMsg],
          temperature: 0.7,
          stream: false
        })
      });
      const data = await response.json();
      const aiContent = data.choices?.[0]?.message?.content || "Error: No response.";
      setMessages(prev => [...prev, { role: 'assistant', content: aiContent }]);
    } catch (err) {
      setMessages(prev => [...prev, { role: 'assistant', content: `Connection Failed: Is LM Studio running? (${err})` }]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    scrollRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  return (
    <div className="flex flex-col h-[calc(100vh-100px)]">
      {/* Toolbar */}
      <CognitiveToolbar
        dialecticalMode={dialecticalMode}
        setDialecticalMode={setDialecticalMode}
        activeLens={activeLens}
        setActiveLens={setActiveLens}
      />
      {/* Chat Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && (
          <div className="text-center text-gray-400 mt-20">
            <Bot size={48} className="mx-auto mb-4 opacity-50" />
            <p>System Online. Awaiting Orders.</p>
          </div>
        )}
        {messages.map((msg, idx) => {
          // Detect dialectical JSON structure
          let dialecticalData = null;
          try {
            const parsed = typeof msg.content === 'string' ? JSON.parse(msg.content) : msg.content;
            if (parsed && parsed.thesis && parsed.antithesis && parsed.synthesis) {
              dialecticalData = parsed;
            }
          } catch {}
          return (
            <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-[80%] rounded-lg p-4 ${
                msg.role === 'user' ? 'bg-blue-600 text-white' : 'bg-gray-800 text-gray-100 shadow-sm border border-gray-700'
              }`}>
                <div className="flex items-center gap-2 mb-2 border-b border-gray-600 pb-1">
                  {msg.role === 'user' ? <User size={16} /> : <Bot size={16} />}
                  <span className="text-xs uppercase font-bold">{msg.role}</span>
                </div>
                {/* Render DialecticalView if dialectical JSON detected */}
                {dialecticalData ? (
                  <DialecticalView data={dialecticalData} />
                ) : (
                  <AdaptiveMessage content={msg.content} />
                )}
              </div>
            </div>
          );
        })}
        {loading && <div className="text-gray-500 text-sm animate-pulse">Thinking...</div>}
        <div ref={scrollRef} />
      </div>
      {/* Demo: TerminalBlock for script runner */}
      <div className="my-4">
        <TerminalBlock scriptName="example_script.py" autoRun={false} />
      </div>
      {/* Input Area */}
      <div className="p-4 bg-white border-t border-gray-200">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && sendMessage()}
            className="flex-1 p-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 font-mono text-sm"
            placeholder="Initialize system scan..."
          />
          <button 
            onClick={sendMessage}
            disabled={loading}
            className="bg-blue-600 text-white p-3 rounded-lg hover:bg-blue-700 disabled:opacity-50"
          >
            <Send size={20} />
          </button>
        </div>
      </div>
    </div>
  );
}
