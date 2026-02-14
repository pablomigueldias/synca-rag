import { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, BrainCircuit } from 'lucide-react';
import api from '../services/api';

// Tipagem das mensagens
interface Message {
  role: 'user' | 'bot';
  content: string;
  sources?: string[];
}

export function Chat() {

  const [input, setInput] = useState('');
  const [messages, setMessages] = useState<Message[]>([
    { role: 'bot', content: 'Olá! Sou o Synca. Pergunte algo sobre seus documentos.' }
  ]);
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);
  const [sessionId, setSessionId] = useState('');

  useEffect(() => {
    let id = localStorage.getItem('synca_session_id');
    if (!id) {
      id = crypto.randomUUID();
      localStorage.setItem('synca_session_id', id);
    }
    setSessionId(id);
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  async function handleSend() {
    if (!input.trim() || loading) return;

    const userMsg = input;
    setInput('');
    
    setMessages(prev => [...prev, { role: 'user', content: userMsg }]);
    setLoading(true);

    try {
      const res = await api.post('/chat/', { 
          pergunta: userMsg,
          session_id: sessionId 
      });
      
      const botResponse = res.data.resposta;
      const sources = res.data.fontes_utilizadas;

      setMessages(prev => [...prev, { role: 'bot', content: botResponse, sources }]);
    } catch (error) {
      setMessages(prev => [...prev, { role: 'bot', content: 'Erro ao conectar com o cérebro do Synca. O backend está rodando?' }]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex flex-col h-[600px] bg-slate-900 rounded-lg border border-slate-700 shadow-2xl overflow-hidden">

      <div className="bg-slate-800 p-4 border-b border-slate-700 flex items-center gap-2">
        <BrainCircuit className="text-purple-400 w-6 h-6" />
        <h2 className="text-white font-bold">Synca Neural Interface</h2>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-slate-900/50">
        {messages.map((msg, idx) => (
          <div key={idx} className={`flex gap-3 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            
            {msg.role === 'bot' && (
              <div className="w-8 h-8 rounded-full bg-purple-600 flex items-center justify-center shrink-0">
                <Bot className="w-5 h-5 text-white" />
              </div>
            )}

            <div className={`max-w-[80%] rounded-2xl p-3 text-sm ${
              msg.role === 'user' 
                ? 'bg-blue-600 text-white rounded-br-none' 
                : 'bg-slate-700 text-slate-200 rounded-bl-none'
            }`}>
              <p className="whitespace-pre-wrap">{msg.content}</p>
              
              {msg.sources && msg.sources.length > 0 && (
                <div className="mt-2 pt-2 border-t border-slate-600">
                  <p className="text-xs text-slate-400 font-semibold mb-1">Fontes:</p>
                  {msg.sources.map((src, i) => (
                    <div key={i} className="text-[10px] text-slate-500 bg-slate-800 p-1 rounded mb-1 truncate">
                      {src.substring(0, 100)}...
                    </div>
                  ))}
                </div>
              )}
            </div>

            {msg.role === 'user' && (
              <div className="w-8 h-8 rounded-full bg-blue-500 flex items-center justify-center shrink-0">
                <User className="w-5 h-5 text-white" />
              </div>
            )}
          </div>
        ))}
        
        {loading && (
          <div className="flex gap-3">
             <div className="w-8 h-8 rounded-full bg-purple-600 flex items-center justify-center animate-pulse">
                <Bot className="w-5 h-5 text-white" />
              </div>
              <div className="bg-slate-700 p-3 rounded-2xl rounded-bl-none">
                <span className="text-slate-400 text-xs animate-pulse">Pensando... (GPU em uso)</span>
              </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      <div className="p-4 bg-slate-800 border-t border-slate-700 flex gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSend()}
          placeholder="Digite sua pergunta..."
          className="flex-1 bg-slate-900 border border-slate-600 text-white rounded-lg px-4 py-2 focus:outline-none focus:border-purple-500"
          disabled={loading}
        />
        <button
          onClick={handleSend}
          disabled={loading}
          className="bg-purple-600 hover:bg-purple-700 text-white p-2 rounded-lg transition-colors disabled:opacity-50"
        >
          <Send className="w-5 h-5" />
        </button>
      </div>
    </div>
  );
}