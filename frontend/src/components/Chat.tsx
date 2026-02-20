import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { vscDarkPlus } from "react-syntax-highlighter/dist/esm/styles/prism";

import { useState, useRef, useEffect } from "react";
import { Send, Bot, User, BrainCircuit, Sparkles } from "lucide-react";
import api from "../services/api";

interface Message {
  role: "user" | "bot";
  content: string;
  sources?: string[];
}

export function Chat() {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "bot",
      content: "Olá, Pablo! Sou o **Synca**. O motor RAG está online. O que vamos construir hoje?",
    },
  ]);
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);
  const [sessionId, setSessionId] = useState("");

  useEffect(() => {
    let id = localStorage.getItem("synca_session_id");
    if (!id) {
      id = crypto.randomUUID();
      localStorage.setItem("synca_session_id", id);
    }
    setSessionId(id);
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  async function handleSend() {
    if (!input.trim() || loading) return;

    const userMsg = input;
    setInput("");

    setMessages((prev) => [...prev, { role: "user", content: userMsg }]);
    setLoading(true);

    try {
      const res = await api.post("/chat/", {
        pergunta: userMsg,
        session_id: sessionId,
      });

      const botResponse = res.data.resposta;
      const sources = res.data.fontes_utilizadas;

      setMessages((prev) => [
        ...prev,
        { role: "bot", content: botResponse, sources },
      ]);
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        {
          role: "bot",
          content:
            "⚠️ **Erro de Conexão:** Não consegui acessar o servidor do Llama 3.1.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex flex-col h-[700px] w-full max-w-5xl mx-auto bg-gradient-to-br from-slate-900 via-slate-900 to-slate-950 rounded-2xl border border-slate-700/50 shadow-[0_0_40px_-15px_rgba(168,85,247,0.3)] overflow-hidden">
      
      <div className="bg-slate-900/80 backdrop-blur-md p-4 border-b border-white/5 flex items-center justify-between sticky top-0 z-10">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-purple-500/10 rounded-lg border border-purple-500/20">
            <BrainCircuit className="text-purple-400 w-6 h-6 animate-pulse" />
          </div>
          <div>
            <h2 className="text-white font-bold tracking-wide">Synca <span className="text-purple-400 font-light">Neural</span></h2>
            <p className="text-xs text-green-400 flex items-center gap-1">
              <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></span> Sistema Online
            </p>
          </div>
        </div>
        <Sparkles className="w-5 h-5 text-slate-500" />
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-6 scrollbar-thin scrollbar-thumb-slate-700 scrollbar-track-transparent">
        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`flex gap-4 ${msg.role === "user" ? "justify-end" : "justify-start"}`}
          >
            {msg.role === "bot" && (
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-purple-600 to-indigo-600 flex items-center justify-center shrink-0 shadow-lg shadow-purple-500/20 border border-purple-400/30">
                <Bot className="w-5 h-5 text-white" />
              </div>
            )}

            <div
              className={`max-w-[85%] rounded-2xl p-4 shadow-md ${
                msg.role === "user"
                  ? "bg-gradient-to-br from-blue-600 to-indigo-600 text-white rounded-tr-sm"
                  : "bg-slate-800/80 backdrop-blur-sm border border-slate-700/50 text-slate-200 rounded-tl-sm"
              }`}
            >
              <div className="prose prose-invert max-w-none text-sm prose-pre:bg-slate-900/50 prose-pre:border prose-pre:border-slate-700/50 prose-a:text-purple-400">
                <ReactMarkdown
                  remarkPlugins={[remarkGfm]}
                  components={{
                    code({ node, inline, className, children, ...props }: any) {
                      const match = /language-(\w+)/.exec(className || "");
                      return !inline && match ? (
                        <div className="rounded-lg overflow-hidden my-4 border border-slate-700 shadow-xl">
                          <div className="bg-slate-900 text-slate-400 px-4 py-2 text-xs uppercase font-semibold flex justify-between items-center tracking-wider">
                            {match[1]}
                            <span className="flex gap-1.5">
                              <span className="w-2.5 h-2.5 rounded-full bg-red-500/80"></span>
                              <span className="w-2.5 h-2.5 rounded-full bg-yellow-500/80"></span>
                              <span className="w-2.5 h-2.5 rounded-full bg-green-500/80"></span>
                            </span>
                          </div>
                          <SyntaxHighlighter
                            style={vscDarkPlus}
                            language={match[1]}
                            PreTag="div"
                            customStyle={{ margin: 0, padding: '1rem', background: '#0f172a' }}
                            {...props}
                          >
                            {String(children).replace(/\n$/, "")}
                          </SyntaxHighlighter>
                        </div>
                      ) : (
                        <code
                          className="bg-slate-900 text-purple-300 px-1.5 py-0.5 rounded-md text-xs border border-slate-700 font-mono"
                          {...props}
                        >
                          {children}
                        </code>
                      );
                    },
                  }}
                >
                  {msg.content}
                </ReactMarkdown>
              </div>

              {msg.sources && msg.sources.length > 0 && (
                <div className="mt-4 pt-3 border-t border-slate-700/50">
                  <p className="text-xs text-slate-400 font-semibold mb-2 flex items-center gap-1">
                    <Sparkles className="w-3 h-3 text-purple-400" /> Fragmentos Recuperados:
                  </p>
                  <div className="flex flex-col gap-1.5">
                    {msg.sources.map((src, i) => (
                      <div
                        key={i}
                        className="text-[11px] text-slate-400 bg-slate-900/50 border border-slate-700/50 px-2 py-1.5 rounded-md truncate hover:text-slate-300 transition-colors cursor-default"
                        title={src}
                      >
                        {src.substring(0, 120)}...
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
            {msg.role === "user" && (
              <div className="w-10 h-10 rounded-xl bg-slate-800 flex items-center justify-center shrink-0 border border-slate-600 shadow-md">
                <User className="w-5 h-5 text-slate-300" />
              </div>
            )}
          </div>
        ))}
        {loading && (
          <div className="flex gap-4 justify-start">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-purple-600 to-indigo-600 flex items-center justify-center shrink-0 shadow-lg shadow-purple-500/20 border border-purple-400/30">
              <Bot className="w-5 h-5 text-white animate-pulse" />
            </div>
            <div className="bg-slate-800/80 backdrop-blur-sm border border-slate-700/50 rounded-2xl rounded-tl-sm p-4 flex items-center gap-1.5 h-[52px]">
              <div className="w-2 h-2 bg-purple-400 rounded-full animate-bounce [animation-delay:-0.3s]"></div>
              <div className="w-2 h-2 bg-purple-400 rounded-full animate-bounce [animation-delay:-0.15s]"></div>
              <div className="w-2 h-2 bg-purple-400 rounded-full animate-bounce"></div>
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      <div className="p-4 bg-slate-900/80 backdrop-blur-md border-t border-white/5">
        <div className="flex gap-2 max-w-4xl mx-auto relative">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSend()}
            placeholder="Envie um prompt para o modelo..."
            className="flex-1 bg-slate-800/50 border border-slate-600 text-slate-100 rounded-xl pl-4 pr-12 py-3 focus:outline-none focus:ring-2 focus:ring-purple-500/50 focus:border-purple-500 transition-all placeholder:text-slate-500"
            disabled={loading}
          />
          <button
            onClick={handleSend}
            disabled={loading || !input.trim()}
            className="absolute right-2 top-2 bottom-2 bg-purple-600 hover:bg-purple-500 disabled:bg-slate-700 disabled:text-slate-500 text-white p-2 rounded-lg transition-all duration-200 shadow-md flex items-center justify-center group"
          >
            <Send className="w-4 h-4 group-hover:-translate-y-0.5 group-hover:translate-x-0.5 transition-transform" />
          </button>
        </div>
        <p className="text-center text-[10px] text-slate-500 mt-2">
          Synca RAG Powered by Llama 3.1 & FastAPI. Respostas geradas por IA podem conter erros.
        </p>
      </div>
    </div>
  );
}