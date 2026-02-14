import { useState } from 'react';
import { UploadCloud, CheckCircle, AlertCircle, Loader2 } from 'lucide-react';
import api from '../services/api'

export function Upload() {
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState<'idle' | 'success' | 'error'>('idle');
  const [msg, setMsg] = useState('');

  async function handleFileUpload(e: React.ChangeEvent<HTMLInputElement>) {
    if (!e.target.files?.length) return;
    
    const file = e.target.files[0];
    const formData = new FormData();
    formData.append('file', file);

    setLoading(true);
    setStatus('idle');
    setMsg('Processando vetores na GPU... (Isso pode levar alguns segundos)');

    try {
      const res = await api.post('/docs/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      
      setStatus('success');
      setMsg(`Sucesso! ${res.data.chunks_criados} trechos indexados.`);
    } catch (error) {
      console.error(error);
      setStatus('error');
      setMsg('Erro ao processar. Verifique se é um PDF ou Markdown válido.');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="p-4 bg-slate-800 rounded-lg border border-slate-700 shadow-lg mb-6">
      <h2 className="text-lg font-semibold text-white mb-2 flex items-center gap-2">
        <UploadCloud className="w-5 h-5 text-blue-400" />
        Ingestão de Conhecimento
      </h2>
      
      <div className="flex items-center gap-4">
        <label className={`
          flex items-center justify-center px-4 py-2 rounded cursor-pointer transition-all
          ${loading ? 'bg-slate-600 cursor-not-allowed' : 'bg-blue-600 hover:bg-blue-500 text-white'}
        `}>
          {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : 'Selecionar PDF'}
          <input 
            type="file" 
            accept=".pdf,.md,.txt" 
            onChange={handleFileUpload} 
            disabled={loading} 
            className="hidden" 
          />
        </label>

        <div className="text-sm">
            {status === 'idle' && loading && <span className="text-blue-300 animate-pulse">{msg}</span>}
            {status === 'success' && <span className="text-green-400 flex items-center gap-1"><CheckCircle className="w-4 h-4"/> {msg}</span>}
            {status === 'error' && <span className="text-red-400 flex items-center gap-1"><AlertCircle className="w-4 h-4"/> {msg}</span>}
            {status === 'idle' && !loading && <span className="text-slate-400">Nenhum arquivo processado.</span>}
        </div>
      </div>
    </div>
  );
}